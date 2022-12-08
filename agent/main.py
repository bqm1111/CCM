import os
import docker
import time
import logging
import logging.config
import requests as r
from docker.models.containers import Container
from dynaconf import settings
import utils

log_config = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.config.fileConfig(log_config, disable_existing_loggers=False)
LOGGER = logging.getLogger()

IMAGE_NAME = settings.IMAGE_NAME
MANAGER = settings.COORDINATOR_URI

NODE_ID = utils.get_hardware_id()

node = r.get(f"{MANAGER}/nodes/{NODE_ID}")
assert node.ok
node = node.text

if node == 'null':
    # if this node doesn't exit, create it
    node = r.post(f"{MANAGER}/nodes/{NODE_ID}", json={
        'ip': settings.HOST_IP,
        'capacity': settings.HOST_CAPACITY,
        'description': settings.HOST_DESC
    })
    assert node.ok
    LOGGER.info("create node %s", node.text)

DOCKER_CLIENT = docker.from_env()
for image in client.images.list():
    print(image.id)

