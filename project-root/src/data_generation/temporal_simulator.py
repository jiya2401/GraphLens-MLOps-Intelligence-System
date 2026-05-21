from copy import deepcopy
import random

from failure_simulator import simulate_graph_failures


DEFAULT_TEMPORAL_CONFIG = {
    "num_timesteps": 5,
    "temporal_drift_strength": 0.05,
    "recovery_probability": 0.1,
    "instability_accumulation_rate": 0.15,
}

RECOVERY_METRICS = (
    "anomaly_score",
    "runtime",
    "queue_delay",
    "retry_count",
    "timeout_count",
)


def _normalize_temporal_config(config):
    normalized = DEFAULT_TEMPORAL_CONFIG.copy()
    if isinstance(config, dict):
        normalized.update(
            {key: value for key, value in config.items() if value is not None}
        )
    return normalized


def _clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def _get_baselines(ranges):
    return {key: (bounds[0] + bounds[1]) / 2 for key, bounds in ranges.items()}


def _is_float_range(bounds):
    return isinstance(bounds[0], float) or isinstance(bounds[1], float)


def _apply_temporal_drift(
    features,
    ranges,
    baselines,
    drift_strength,
    instability,
    precision,
):
    for metric, bounds in ranges.items():
        min_val, max_val = bounds
        span = max_val - min_val
        if span <= 0:
            continue

        current = features.get(metric, baselines[metric])
        pull = (baselines[metric] - current) * drift_strength * 0.1
        noise = random.uniform(-1.0, 1.0) * drift_strength * span * 0.05
        instability_delta = instability * drift_strength * span * 0.1
        updated = current + pull + noise + instability_delta
        updated = _clamp(updated, min_val, max_val)

        if _is_float_range(bounds):
            features[metric] = round(updated, precision)
        else:
            features[metric] = int(round(updated))


def _apply_recovery(features, ranges, precision):
    for metric in RECOVERY_METRICS:
        bounds = ranges.get(metric)
        if not bounds:
            continue

        min_val, max_val = bounds
        span = max_val - min_val
        if span <= 0:
            continue

        current = features.get(metric, min_val)
        updated = current - span * 0.15
        updated = _clamp(updated, min_val, max_val)

        if _is_float_range(bounds):
            features[metric] = round(updated, precision)
        else:
            features[metric] = int(round(updated))


def simulate_temporal_graph(
    graph,
    graph_id,
    initial_features_by_node,
    thresholds,
    propagation_config,
    temporal_config,
    feature_config,
):
    temporal = _normalize_temporal_config(temporal_config)
    ranges = feature_config.get("ranges", {})
    precision = feature_config.get("float_precision", 3)

    num_timesteps = int(max(1, temporal["num_timesteps"]))
    drift_strength = float(temporal["temporal_drift_strength"])
    recovery_probability = float(temporal["recovery_probability"])
    instability_rate = float(temporal["instability_accumulation_rate"])

    baselines = _get_baselines(ranges)
    features_by_node = deepcopy(initial_features_by_node)
    instability = {node: 0.0 for node in graph.nodes()}

    rows = []
    propagation_totals = {
        "timesteps": 0,
        "base_failures": 0,
        "propagated_failures": 0,
        "impacted_nodes": 0,
        "total_failures": 0,
    }
    temporal_stats = {
        "graphs": 1,
        "timesteps": num_timesteps,
        "recovery_events": 0,
        "instability_sum": 0.0,
        "instability_samples": 0,
    }

    for timestep in range(num_timesteps):
        for node, features in features_by_node.items():
            _apply_temporal_drift(
                features,
                ranges,
                baselines,
                drift_strength,
                instability[node],
                precision,
            )

        features_by_node, failures_by_node, graph_stats = simulate_graph_failures(
            graph,
            features_by_node,
            thresholds=thresholds,
            propagation_config=propagation_config,
        )

        propagation_totals["timesteps"] += 1
        for key in (
            "base_failures",
            "propagated_failures",
            "impacted_nodes",
            "total_failures",
        ):
            propagation_totals[key] += graph_stats.get(key, 0)

        for node, features in features_by_node.items():
            failed = failures_by_node[node]
            prev_rate = features.get("previous_failure_rate", 0.0)
            smoothed = (1 - instability_rate) * prev_rate + instability_rate * failed
            features["previous_failure_rate"] = round(
                _clamp(smoothed, 0.0, 1.0), precision
            )

            rows.append(
                {
                    "graph_id": graph_id,
                    "node_name": node,
                    "timestep": timestep,
                    **features,
                    "failed": failed,
                }
            )

        for node, features in features_by_node.items():
            failed = failures_by_node[node]
            if failed:
                instability[node] = _clamp(
                    instability[node] + instability_rate, 0.0, 1.0
                )
            else:
                instability[node] = _clamp(
                    instability[node] - instability_rate * 0.5, 0.0, 1.0
                )

            if instability[node] > 0 and random.random() < recovery_probability:
                _apply_recovery(features, ranges, precision)
                instability[node] = _clamp(
                    instability[node] - instability_rate, 0.0, 1.0
                )
                temporal_stats["recovery_events"] += 1

            temporal_stats["instability_sum"] += instability[node]
            temporal_stats["instability_samples"] += 1

    return rows, propagation_totals, temporal_stats
