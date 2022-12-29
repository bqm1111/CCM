import os
import docker
import time
import logging
import logging.config
import requests as r
from docker.models.containers import Container
from dynaconf import Dynaconf
import utils
from confluent_kafka import Consumer, Producer, Message
import json
from pydantic import parse_raw_as
from schemas.agent_config_schema import TOPIC210Model

TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"
"""query the server config. example:
server_configs = {
    "MTAR_example": {
        "kafka": "tainp.local:9092",
        "topic": "xface.event",
        "URIs": [
            "rtsp://admin:123456a%40@172.21.104.100",
            "rtsp://admin:123456a%40@172.21.104.101",
            "rtsp://admin:123456a%40@172.21.104.102",
            "rtsp://admin:123456a%40@172.21.104.103"
        ]
    }
}
"""

# TODO: Remove hard code the address of bootstrap server
BOOTSTRAP_SERVER = "172.21.100.167:9092"
# 
CONSUMER = Consumer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVER,
        "auto.offset.reset": "latest",
        "enable.auto.commit": "true",
        # Autocommit every 2 seconds. If a message isn't be matched in within 2 seconds, it should be ignore anyway
        # 'auto.commit.interval.ms': 2000,
        "group.id": "matchergroup",
    }
)

CONSUMER.subscribe([TOPIC201, TOPIC210])

PRODUCER = Producer({"bootstrap.servers": BOOTSTRAP_SERVER})


settings = Dynaconf(settings_file='settings.toml')
IMAGE_NAME = settings.IMAGE_NAME
docker_client = docker.from_env()
NODE_ID = utils.get_hardware_id()

containers =  docker_client.containers.list()

index = 0

RUNNING = True
def consume():
    while RUNNING:
        msg = CONSUMER.poll(1)
        
        if msg is None:
                continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            
        if msg.topic() == TOPIC210:
            data = parse_raw_as(TOPIC210Model, msg.value())
            print(data.URIs)
        if msg.topic() == TOPIC201:
            print("Hearing from topic201")


# if docker_client.images.get(IMAGE_NAME):
#     container = docker_client.containers.run(IMAGE_NAME, name="deepstream-app", stdout=True, detach=True, auto_remove=True)
#     for line in container.logs(stream=True):
#         print(line.strip())
    
# else:
#     print("Image not exist")


def main():
    """main function to be call"""
    try:
        consume()
    except KeyboardInterrupt:
        global RUNNING
        RUNNING = False
        print("gracefully close consumers and flush producer")
    finally:
        PRODUCER.flush()
        CONSUMER.close()


if __name__ == "__main__":
    main()
