def simulate_failure(node_features):

    failed = 0

    # Failure logic
    if (
        node_features["cpu_usage"] > 85
        and node_features["runtime"] > 15
    ):
        failed = 1

    return failed


if __name__ == "__main__":

    sample_node = {
        "cpu_usage": 92,
        "runtime": 18
    }

    result = simulate_failure(sample_node)

    print("Failure:", result)