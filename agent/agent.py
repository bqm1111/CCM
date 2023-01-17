import logging
import logging.config
import os
import socket
import time
from typing import List, Optional

import docker
import requests as r
import utils
from confluent_kafka import Consumer, Message, Producer
from docker.models.containers import Container
from dynaconf import Dynaconf
from pydantic import parse_obj_as, parse_raw_as
from pydantic import UUID4
from schemas.config_schema import DsAppConfig, DsInstanceConfig, write_config
from schemas.topic_schema import (TOPIC200, TOPIC201, TOPIC210, TOPIC220,
                                  DsInstance, TOPIC210Model, Topic200Model, Topic201Model, Topic220Model)

settings = Dynaconf(settings_file='settings.toml')
log_config = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.config.fileConfig(log_config, disable_existing_loggers=False)
LOGGER = logging.getLogger(__file__)

# TODO: Remove hard code the address of bootstrap server
BOOTSTRAP_SERVER = "172.21.100.242:9092"
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


IMAGE_NAME = settings.IMAGE_NAME
DOCKER_CLIENT = docker.from_env()
NODE_ID = utils.get_hardware_id()

containers = DOCKER_CLIENT.containers.list()
# image = DOCKER_CLIENT.images.pull(IMAGE_NAME, settings.IMAGE_TAG)
RUNNING = True
def update_container(name: str, server_config: DsInstanceConfig, local_config: DsInstanceConfig):
    # Check if server config and local config are identical
    container = DOCKER_CLIENT.containers.get(name)
    if container.status == 'running':
        if server_config != local_config:
            LOGGER.info(f"Config in container {container.name} changed !!!!!!!!!!")
        # Update local config if there are differences
            path = os.path.join("../configs/", name)
            write_config(path, server_config)
            LOGGER.info(f"Changing config of container {container.name}")
            utils.copy_to_container(container, path, "/workspace/configs")
            # Restart the container
            LOGGER.info(f"Restarting container {container.name}")
            # container.restart()
            LOGGER.info(f"Container {container.name} restarted")
    else:
        LOGGER.info(f"Starting container {container.name}")
        container.start()
        LOGGER.info(f"Container {container.name} started")


def create_container(name: str, config: DsInstanceConfig):
    # Parse configuration from config and write it to a file
    path = os.path.join("../configs/", name)
    write_config(path, config)        
    # Run container with mounted config
    LOGGER.info(f"Creating container {name}")
    container_engine_volume = name + "_engine"
    container_config_volume = name + "_config"

    DOCKER_CLIENT.containers.run(image=IMAGE_NAME,
                                       name=name,
                                       # runtime="nvidia",
                                       restart_policy={
                                           "Name": "on-failure", "MaximumRetryCount": 5},
                                       volumes={
                                                container_engine_volume: {
                                           'bind': '/workspace/build', 'mode': 'rw'}},
                                       detach=True)
    LOGGER.info(f"Creating container {name} ... DONE")
    LOGGER.info(f"Waiting for container {name} to run")
    
    start = time.time()
    end = time.time()
    while DOCKER_CLIENT.containers.get(name).status != 'running' and (end - start) < 120:
        end = time.time()
        LOGGER.info(f"Waiting .....")
    LOGGER.info(f"Container {name} is running")

def delete_container(container: Container):
    LOGGER.info(f"Deleting container {container.name} - ({container.id})")
    container.stop()
    container.remove()
    LOGGER.info(f"Deleted container {container.name} - ({container.id})")

def create_TOPIC200():
    hostname = socket.gethostname()
    
def consume():
    PRODUCER.poll(0)
    
    while RUNNING:
        local_configs = {}
        containers = {}
        for _container in DOCKER_CLIENT.containers.list(all=True):
            if _container.attrs['Config']['Image'] == IMAGE_NAME:
                containers[_container.name] = _container                
                _id, _config = utils.read_config(_container)
                if _id is None:
                    continue
                local_configs[_id] = _config
        msg = CONSUMER.poll(1)
        # print(local_configs.keys())
        if msg is None:
            continue
        if msg.error():
            LOGGER.error(f"Consumer error: {msg.error()}")

        if msg.topic() == TOPIC210:
            data = parse_raw_as(TOPIC210Model, msg.value())    
            hostname = socket.gethostname()
            node_id = UUID4(utils.get_hardware_id())
            server_config = {}
            for machine in data.agent_info_list:
                if machine.node_id == node_id and machine.hostname == hostname:
                    for instance in machine.node_config_list:
                        server_config[instance.name] = instance.config
                    for container_name in set(local_configs) - set(server_config):
                        delete_container(containers[container_name])
                        
                    for container_name in set(server_config) - set(local_configs):
                        create_container(container_name, server_config[container_name])
                        
                    for container_name in set(local_configs) & set(server_config):
                        update_container(container_name, server_config[container_name], local_configs[container_name])
                        

        if msg.topic() == TOPIC201:
            data = parse_raw_as(Topic201Model, msg.value())
            if utils.has_ip_address(str(data.ip_address)):
                LOGGER.info("Sending TOPIC200")
                hostname = socket.gethostname()
                node_id = UUID4(utils.get_hardware_id())
                PRODUCER.poll(0)
                topic200data = Topic200Model(node_id=node_id, hostname=hostname, ip_address=str(data.ip_address))
                PRODUCER.produce(TOPIC200, topic200data.json())


def main():
    """main function to be call"""
    try:
        consume()
    except KeyboardInterrupt:
        global RUNNING
        RUNNING = False
        LOGGER.info("gracefully close consumers and flush producer")
    finally:
        PRODUCER.flush()
        CONSUMER.close()


if __name__ == "__main__":
    main()
