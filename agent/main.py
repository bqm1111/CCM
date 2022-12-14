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
import aiodocker

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

