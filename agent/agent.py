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
from confluent_kafka import Consumer, Producer, Message
import json
TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"

# TODO: Remove hard code the address of bootstrap server
BOOSTRAP_SERVER = "172.21.100.167:9092"

CONSUMER = Consumer(
    {
        "bootstrap.servers": BOOSTRAP_SERVER,
        "auto.offset.reset": "latest",
        "enable.auto.commit": "true",
        # Autocommit every 2 seconds. If a message isn't be matched in within 2 seconds, it should be ignore anyway
        # 'auto.commit.interval.ms': 2000,
        "group.id": "matchergroup",
    }
)
# 
CONSUMER.subscribe([TOPIC201, TOPIC210])

PRODUCER = Producer({"bootstrap.servers": BOOSTRAP_SERVER})


settings = Dynaconf(settings_file='settings.toml')
IMAGE_NAME = settings.IMAGE_NAME
docker_client = docker.from_env()
NODE_ID = utils.get_hardware_id()

containers =  docker_client.containers.list()

index = 0
while True:
    msg = CONSUMER.poll(1)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.errors()}")
        continue
    index = index + 1
    data = json.loads(msg.value())
    print(f"Receive message: {index}: {data}")


if docker_client.images.get(IMAGE_NAME):
    container = docker_client.containers.run(IMAGE_NAME, name="deepstream-app", stdout=True, detach=True, auto_remove=True)
    for line in container.logs(stream=True):
        print(line.strip())
    
else:
    print("Image not exist")

