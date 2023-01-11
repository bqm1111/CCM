import socket
from typing import Optional, List

import os
import logging
import logging.config
import docker
import requests as r
import utils 
from confluent_kafka import Consumer, Message, Producer
from docker.models.containers import Container
from dynaconf import Dynaconf
from pydantic import parse_obj_as, parse_raw_as
import tarfile
from schemas.config_schema import (TOPIC200, TOPIC201, TOPIC210, TOPIC220,DsInstanceConfig,
                                   DsAppConfig, TOPIC210Model, write_config, DsInstanceInfo)

settings = Dynaconf(settings_file='settings.toml')
log_config = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.config.fileConfig(log_config, disable_existing_loggers=False)
LOGGER = logging.getLogger()

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
    print(server_config.appconfig)
    print(local_config.appconfig)
    if server_config != local_config:
        # Update local config if there are differences
        container = DOCKER_CLIENT.containers.get(name)
        path = os.path.join("../configs/", name)
        write_config(path, server_config)
        # Restart the container
        LOGGER.info(f"Restarting container {container.name}")

        container.restart()
        LOGGER.info(f"Restart container {container.name} ... DONE")


def create_container(name: str, config: DsInstanceConfig):
    # Parse configuration from config and write it to a file
    path = os.path.join("../configs/", name)
    write_config(path, config)        
    # Run container with mounted config
    config_folder = os.path.abspath(path)
    print(config_folder)
    LOGGER.info(f"Creating container {name}")
    DOCKER_CLIENT.containers.run(image=IMAGE_NAME,
                                       name=name,
                                       # runtime="nvidia",
                                       restart_policy={
                                           "Name": "on-failure", "MaximumRetryCount": 5},
                                       volumes={config_folder: {
                                           'bind': '/workspace/config', 'mode': 'rw'}},
                                       detach=True)
    LOGGER.info(f"Creating container {name} ... DONE")
def delete_container(container: Container):
    LOGGER.info(f"deleting container {container.name} - ({container.id})")
    container.stop()
    container.remove()
    LOGGER.info("delete %s (%s) ... DONE ", container.name, container.id)
    

def consume():
    while RUNNING:
        local_configs = {}
        containers = {}
        for _container in DOCKER_CLIENT.containers.list(all=True):
            if _container.attrs['Config']['Image'] == IMAGE_NAME:
                
                containers[_container.name] = _container                
                _id, _config = utils.read_config(_container)
                local_configs[_id] = _config

        msg = CONSUMER.poll(1)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
        
        if msg.topic() == TOPIC210:
            data = parse_raw_as(TOPIC210Model, msg.value())    
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            machine_id = utils.get_hardware_id()
            server_config = {}
            for machine in data.machine_config_list:
                if machine.machine_id == machine_id and machine.hostname == hostname:
                    for instance in machine.deepstream_app_info_list:
                        server_config[instance.name] = instance.config
                    for container_name in set(local_configs) - set(server_config):
                        delete_container(containers[container_name])
                        
                    for container_name in set(server_config) - set(local_configs):
                        create_container(container_name, server_config[container_name])
                        
                    for container_name in set(local_configs) & set(server_config):
                        print(container_name)
                        update_container(container_name, server_config[container_name], local_configs[container_name])
                        
            
        if msg.topic() == TOPIC201:
            print("Hearing from topic201")

# 
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
