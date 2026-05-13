import random


def generate_node_features():

    return {

        "cpu_usage": random.randint(20, 100),

        "memory_usage": random.randint(20, 100),

        "runtime": random.randint(1, 20),

        "queue_delay": random.randint(0, 10),

        "retry_count": random.randint(0, 3)
    }


if __name__ == "__main__":

    features = generate_node_features()

    print(features)