"""create topic"""
from typing import List
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException

TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"
admin_client = AdminClient(
    {
        "bootstrap.servers": "172.21.100.167:9092",
    }
)

topic_list: List[NewTopic] = [
    NewTopic(topic=TOPIC200, num_partitions=1, replication_factor=1),
    NewTopic(topic=TOPIC201, num_partitions=1, replication_factor=1),
    NewTopic(topic=TOPIC210, num_partitions=1, replication_factor=1),
    NewTopic(topic=TOPIC220, num_partitions=1, replication_factor=1),
]

# validate before doing anything
admin_client.create_topics(new_topics=topic_list, validate_only=True)

# now create the topic actually
topic_creation_results = admin_client.create_topics(new_topics=topic_list, validate_only=False)

# Wait for each operation to finish.
for topic, f in topic_creation_results.items():
    try:
        f.result()  # The result itself is None
        print(f"Topic {topic} created with status {f.result()}")
    except KafkaException as e:
        print(f"Failed to create topic {topic}: {e}")

# now list all topics
cluster_meta = admin_client.list_topics()
for key, value in cluster_meta.topics.items():
    if not key.startswith("_"):
        print(key, value)
