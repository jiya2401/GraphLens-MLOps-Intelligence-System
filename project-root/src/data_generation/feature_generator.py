import random


DEFAULT_CONFIG = {
    "ranges": {
        # Infrastructure metrics capture resource pressure that can cascade in graphs.
        "cpu_usage": (20, 100),
        "memory_usage": (20, 100),
        "gpu_usage": (0, 100),
        "disk_io": (5, 250),
        "network_latency": (1, 200),
        "temperature": (30, 95),
        # Execution metrics reveal throughput bottlenecks and scheduling contention.
        "runtime": (1, 120),
        "queue_delay": (0, 45),
        "retry_count": (0, 5),
        "throughput": (50, 2000),
        "batch_size": (16, 512),
        # Failure signals reflect past instability and upstream dependency risk.
        "anomaly_score": (0.0, 1.0),
        "timeout_count": (0, 6),
        "previous_failure_rate": (0.0, 0.6),
        "dependency_failure_count": (0, 5),
        # Resource and scaling metrics indicate orchestration stress.
        "pod_restart_count": (0, 6),
        "container_count": (1, 12),
        "autoscaling_events": (0, 6),
        # Data quality metrics correlate with downstream model issues.
        "missing_value_ratio": (0.0, 0.25),
        "data_drift_score": (0.0, 1.0),
        "schema_validation_errors": (0, 6),
    },
    "categories": {
        # Encoded metadata provides type-aware context for graph learning.
        "node_type": [
            "data_ingestion",
            "data_cleaning",
            "feature_engineering",
            "model_training",
            "evaluation",
            "deployment",
        ],
        "service_name": [
            "ingestion_service",
            "cleaning_service",
            "feature_store",
            "training_service",
            "evaluation_service",
            "deployment_service",
        ],
        "pipeline_stage": [
            "ingest",
            "clean",
            "feature",
            "train",
            "evaluate",
            "deploy",
        ],
    },
    "float_precision": 3,
}


def _rand_int(min_val, max_val):
    return random.randint(min_val, max_val)


def _rand_float(min_val, max_val, precision):
    return round(random.uniform(min_val, max_val), precision)


def _encode_category(categories):
    return random.randint(0, len(categories) - 1)


def generate_node_features(config=None):
    cfg = DEFAULT_CONFIG if config is None else config
    ranges = cfg["ranges"]
    categories = cfg["categories"]
    precision = cfg.get("float_precision", 3)

    return {
        # Infrastructure metrics
        "cpu_usage": _rand_int(*ranges["cpu_usage"]),
        "memory_usage": _rand_int(*ranges["memory_usage"]),
        "gpu_usage": _rand_int(*ranges["gpu_usage"]),
        "disk_io": _rand_int(*ranges["disk_io"]),
        "network_latency": _rand_int(*ranges["network_latency"]),
        "temperature": _rand_int(*ranges["temperature"]),
        # Execution metrics
        "runtime": _rand_int(*ranges["runtime"]),
        "queue_delay": _rand_int(*ranges["queue_delay"]),
        "retry_count": _rand_int(*ranges["retry_count"]),
        "throughput": _rand_int(*ranges["throughput"]),
        "batch_size": _rand_int(*ranges["batch_size"]),
        # Pipeline metadata encoded as stable integer categories
        "node_type": _encode_category(categories["node_type"]),
        "service_name": _encode_category(categories["service_name"]),
        "pipeline_stage": _encode_category(categories["pipeline_stage"]),
        "execution_priority": _rand_int(1, 5),
        # Failure and reliability signals
        "anomaly_score": _rand_float(*ranges["anomaly_score"], precision),
        "timeout_count": _rand_int(*ranges["timeout_count"]),
        "previous_failure_rate": _rand_float(
            *ranges["previous_failure_rate"], precision
        ),
        "dependency_failure_count": _rand_int(
            *ranges["dependency_failure_count"]
        ),
        # Resource and scaling metrics
        "pod_restart_count": _rand_int(*ranges["pod_restart_count"]),
        "container_count": _rand_int(*ranges["container_count"]),
        "autoscaling_events": _rand_int(*ranges["autoscaling_events"]),
        # Data quality metrics
        "missing_value_ratio": _rand_float(
            *ranges["missing_value_ratio"], precision
        ),
        "data_drift_score": _rand_float(*ranges["data_drift_score"], precision),
        "schema_validation_errors": _rand_int(
            *ranges["schema_validation_errors"]
        ),
    }


if __name__ == "__main__":

    features = generate_node_features()

    print(features)