import os
from unicodedata import name
import docker
import time
import logging
import logging.config
import requests as r
from docker.models.containers import Container
from dynaconf import Dynaconf
from torch import detach
import utils
import asyncio
import threading
import asyncio
from confluent_kafka import Consumer, Producer, Message

TOPIC200 = "AgentReport"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"

# TODO: Remove hard code the address of bootstrap server
CONSUMER = Consumer(
    {
        "bootstrap.servers": "172.21.100.167:9092",
        "auto.offset.reset": "latest",
        "enable.auto.commit": "true",
        # Autocommit every 2 seconds. If a message isn't be matched in within 2 seconds, it should be ignore anyway
        # 'auto.commit.interval.ms': 2000,
        "group.id": "matchergroup",
    }
)

CONSUMER.subscribe([TOPIC201, TOPIC210])

PRODUCER = Producer({"bootstrap.servers": "tainp.local:9092"})


settings = Dynaconf(settings_file='settings.toml')
IMAGE_NAME = settings.IMAGE_NAME
docker_client = docker.from_env()

NODE_ID = utils.get_hardware_id()
print(NODE_ID)
containers =  docker_client.containers.list()

if docker_client.images.get(IMAGE_NAME):
    container = docker_client.containers.run(IMAGE_NAME, name="deepstream-app", stdout=True, detach=True, auto_remove=True)
    for line in container.logs(stream=True):
        print(line.strip())
    
else:
    print("Image not exist")

