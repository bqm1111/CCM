import os
import docker
import time
import logging
import logging.config
import requests as r
from docker.models.containers import Container
from dynaconf import Dynaconf
import utils

settings = Dynaconf(settings_file='settings.toml')
IMAGE_NAME = settings.IMAGE_NAME
docker_client = docker.from_env()

containers =  docker_client.containers.list()

for container in docker_client.containers.list(all=True):
    if container.attrs['Config']['Image'] == IMAGE_NAME:
        print("Jump here")
        docker_client.containers.run(container.name, detach= False)