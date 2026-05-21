import random

import networkx as nx


DEFAULT_FAILURE_THRESHOLDS = {
    "cpu": 85,
    "runtime": 15,
}

DEFAULT_PROPAGATION_CONFIG = {
    "propagation_enabled": True,
    "propagation_strength": 0.35,
    "propagation_decay": 0.6,
    "max_propagation_depth": 3,
}

TELEMETRY_PROPAGATION_IMPACT = {
    "anomaly_score": 0.6,
    "runtime": 20,
    "retry_count": 2,
    "queue_delay": 12,
    "timeout_count": 2,
}


def _normalize_thresholds(thresholds):
    normalized = DEFAULT_FAILURE_THRESHOLDS.copy()
    if isinstance(thresholds, dict):
        normalized.update(
            {key: value for key, value in thresholds.items() if value is not None}
        )
    return normalized


def _normalize_propagation_config(config):
    normalized = DEFAULT_PROPAGATION_CONFIG.copy()
    if isinstance(config, dict):
        normalized.update(
            {key: value for key, value in config.items() if value is not None}
        )
    return normalized


def _clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def _apply_propagation_effects(node_features, risk):
    if risk <= 0:
        return

    anomaly_score = node_features.get("anomaly_score", 0.0)
    node_features["anomaly_score"] = round(
        _clamp(
            anomaly_score + risk * TELEMETRY_PROPAGATION_IMPACT["anomaly_score"],
            0.0,
            1.0,
        ),
        3,
    )

    runtime = node_features.get("runtime", 0)
    node_features["runtime"] = int(
        round(max(0.0, runtime + risk * TELEMETRY_PROPAGATION_IMPACT["runtime"]))
    )

    retry_count = node_features.get("retry_count", 0)
    node_features["retry_count"] = int(
        round(
            max(
                0.0,
                retry_count + risk * TELEMETRY_PROPAGATION_IMPACT["retry_count"],
            )
        )
    )

    queue_delay = node_features.get("queue_delay", 0)
    node_features["queue_delay"] = int(
        round(
            max(
                0.0,
                queue_delay
                + risk * TELEMETRY_PROPAGATION_IMPACT["queue_delay"],
            )
        )
    )

    timeout_count = node_features.get("timeout_count", 0)
    node_features["timeout_count"] = int(
        round(
            max(
                0.0,
                timeout_count
                + risk * TELEMETRY_PROPAGATION_IMPACT["timeout_count"],
            )
        )
    )


def simulate_failure(node_features, thresholds=None):
    thresholds = _normalize_thresholds(thresholds)

    cpu_threshold = thresholds.get("cpu", DEFAULT_FAILURE_THRESHOLDS["cpu"])
    runtime_threshold = thresholds.get(
        "runtime", DEFAULT_FAILURE_THRESHOLDS["runtime"]
    )

    return int(
        node_features.get("cpu_usage", 0) > cpu_threshold
        and node_features.get("runtime", 0) > runtime_threshold
    )


def _compute_propagation_risk(graph, base_failures, config):
    risk_by_node = {node: 0.0 for node in graph.nodes()}

    if not config["propagation_enabled"]:
        return risk_by_node

    strength = float(config["propagation_strength"])
    decay = float(config["propagation_decay"])
    max_depth = int(config["max_propagation_depth"])

    if strength <= 0 or decay <= 0 or max_depth <= 0:
        return risk_by_node

    failed_nodes = [
        node for node, failed in base_failures.items() if failed == 1
    ]

    for failed_node in failed_nodes:
        distances = nx.single_source_shortest_path_length(
            graph, failed_node, cutoff=max_depth
        )
        for node, distance in distances.items():
            if distance == 0:
                continue
            influence = strength * (decay ** (distance - 1))
            risk_by_node[node] = min(1.0, risk_by_node[node] + influence)

    return risk_by_node


def simulate_graph_failures(
    graph,
    node_features_by_node,
    thresholds=None,
    propagation_config=None,
):
    thresholds = _normalize_thresholds(thresholds)
    propagation = _normalize_propagation_config(propagation_config)

    base_failures = {
        node: simulate_failure(features, thresholds)
        for node, features in node_features_by_node.items()
    }

    risk_by_node = _compute_propagation_risk(graph, base_failures, propagation)

    impacted_nodes = 0
    propagated_failures = 0
    final_failures = dict(base_failures)

    for node, risk in risk_by_node.items():
        if risk <= 0:
            continue

        impacted_nodes += 1
        _apply_propagation_effects(node_features_by_node[node], risk)

        if final_failures.get(node, 0) == 0 and random.random() < risk:
            final_failures[node] = 1
            propagated_failures += 1

    base_failures_count = sum(base_failures.values())
    total_failures_count = sum(final_failures.values())

    stats = {
        "base_failures": base_failures_count,
        "propagated_failures": propagated_failures,
        "impacted_nodes": impacted_nodes,
        "total_failures": total_failures_count,
        "propagation_enabled": propagation["propagation_enabled"],
    }

    return node_features_by_node, final_failures, stats


if __name__ == "__main__":

    sample_node = {
        "cpu_usage": 92,
        "runtime": 18,
        "anomaly_score": 0.1,
        "retry_count": 0,
        "queue_delay": 0,
        "timeout_count": 0,
    }

    result = simulate_failure(sample_node)

    print("Failure:", result)