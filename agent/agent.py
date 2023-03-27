import logging
import logging.config
import os
import socket
import time

import docker
from docker.errors import ContainerError, ImageNotFound, APIError
import utils
from confluent_kafka import Consumer, Producer
from docker.models.containers import Container
from dynaconf import Dynaconf
from pydantic import UUID4, parse_raw_as, ValidationError

from schemas.config_schema import DsInstanceConfig, write_config
from schemas.topic_schema import (TOPIC200, TOPIC201, TOPIC210, TOPIC220, TOPIC222, TOPIC302,
                                  Topic302Model, Topic200Model, Topic201Model, Topic222Model,
                                  Topic210Model, Topic220Model, InstanceStatus)

settings = Dynaconf(settings_file='settings.toml')
log_config = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.config.fileConfig(log_config, disable_existing_loggers=False)
LOGGER = logging.getLogger(__file__)

BOOTSTRAP_SERVER = settings.BOOTSTRAP_SERVER
CONSUMER = Consumer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVER,
        "auto.offset.reset": "latest",
        "enable.auto.commit": "true",
        # Autocommit every 2 seconds. If a message isn't be matched in within 2 seconds, it should be ignore anyway
        # 'auto.commit.interval.ms': 2000,
        "group.id": "coordinator",
    }
)

CONSUMER.subscribe([TOPIC201, TOPIC210, TOPIC222, TOPIC302])

PRODUCER = Producer({"bootstrap.servers": BOOTSTRAP_SERVER})


IMAGE_NAME = settings.IMAGE_NAME
DOCKER_CLIENT = docker.from_env()
NODE_ID = utils.get_hardware_id()
containers = DOCKER_CLIENT.containers.list()

def update_container(container: Container, server_config: DsInstanceConfig, local_config: DsInstanceConfig):
    # Check if server config and local config are identical
    if container.status == 'running':
        if server_config != local_config:
            LOGGER.info(f"Config in container {container.name} changed !!!!!!!!!!")
        # Update local config if there are differences
            path = os.path.join("../configs/", container.name)
            write_config(path, server_config)
            LOGGER.info(f"Changing config of container {container.name}")
            utils.copy_to_container(container, path, "/workspace/configs")
            # Restart the container
            LOGGER.info(f"Restarting container {container.name}")
            container.restart()
            LOGGER.info(f"Container {container.name} restarted")
    else:
        LOGGER.info(f"Restarting container {container.name}. Config does not change")
        if container.status == 'paused':
            container.unpause()
        try:
            container.start()
        except APIError as e:
            LOGGER.error(f"{e}")
        else:
            LOGGER.info(f"Container {container.name} restarted")

def create_container(name: str, config: DsInstanceConfig):
    # Parse configuration from config and write it to a file
    path = os.path.join("../configs/", name)
    write_config(path, config)       
    # Run container with mounted config
    LOGGER.info(f"Creating container {name}")
    container_engine_volume = name + "_engine"
    try:
        DOCKER_CLIENT.containers.run(image=IMAGE_NAME,
                                       name=name,
                                       runtime="nvidia",
                                       security_opt=["seccomp=unconfined"],
                                       environment={"CUDA_VISIBLE_DEVICES": str(config.appconfig.gpu_id)},
                                       restart_policy={
                                           "Name": "on-failure", "MaximumRetryCount": 5},
                                       volumes={
                                                container_engine_volume: {
                                           'bind': '/workspace/build', 'mode': 'rw'}},
                                       detach=True)
    except ImageNotFound:
        LOGGER.error(f"Image {IMAGE_NAME} not found. Please consider changing image name in the setting.toml file, building or pulling the required image")
    except ContainerError as e:
        LOGGER.error(f"Container exits with errors: {e}")    
    except APIError as e:
        LOGGER.error(f"Internal server error: {e}")
    else:
        container = DOCKER_CLIENT.containers.get(name)
        utils.copy_to_container(container, path, "/workspace/configs")
        try:
            container.restart()
        except APIError as e:
            LOGGER.error(f"{e}")
        else:
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
    try:
        container.stop()
    except APIError as e:
        LOGGER.error(f"Error while stopping container {container.name}. Internal server error: {e}")
    else:
        try:
            container.remove()
        except APIError as e:
            LOGGER.error(f"Error while removing container {container.name}. Internal server error: {e}")
        LOGGER.info(f"Deleted container {container.name} - ({container.id})")


def consume():
    start = time.time()    
    while True:
        current = time.time()
        if current - start > settings.check_container_status_interval:
            start = current
            agent_states = []
            for _container in DOCKER_CLIENT.containers.list(all=True):
                if _container.attrs['Config']['Image'] == IMAGE_NAME:
                    agent_states.append(InstanceStatus(instance_name=_container.name, state=_container.attrs["State"]["Status"]))
            
            if len(agent_states) > 0:
                PRODUCER.poll(0)
                PRODUCER.produce(TOPIC220, Topic220Model(node_id=UUID4(utils.get_hardware_id()), status=agent_states).json())

        msg = CONSUMER.poll(1)

        if msg is None:
            continue
        if msg.error():
            LOGGER.error(f"Consumer error: {msg.error()}")
            
        local_configs = {}
        containers = {}
        for _container in DOCKER_CLIENT.containers.list(all=True):
            if _container.attrs['Config']['Image'] == IMAGE_NAME:
                containers[_container.name] = _container                
                _id, _config = utils.read_config(_container)
                if _id is None:
                    continue
                local_configs[_id] = _config

        hostname = socket.gethostname()
        node_id = UUID4(utils.get_hardware_id())
        
        if msg.topic() == TOPIC210:
            try:
                data = parse_raw_as(Topic210Model, msg.value())  
            except ValidationError as e:
                LOGGER.error(f"{e}")
            else:
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
                            update_container(containers[container_name], server_config[container_name], local_configs[container_name])
            
            # DOCKER_CLIENT.volumes.prune()
            
        if msg.topic() == TOPIC302:
            try:
                data = parse_raw_as(Topic302Model, msg.value())  
            except ValidationError as e:
                LOGGER.error(f"{e}")
            else:
                if data.node_id == node_id:
                    LOGGER.info(f"Trying to pause container {data.instance_name}")
                    containers[data.instance_name].pause()
                    LOGGER.info(f"Container named {data.instance_name} is paused")

        if msg.topic() == TOPIC222:
            try:
                data = parse_raw_as(Topic222Model, msg.value())  
            except ValidationError as e:
                LOGGER.error(f"{e}")
            else:
                hostname = utils.get_hostname()
                node_id = UUID4(utils.get_hardware_id())
                server_config = {}
                for machine in data.exited_list:
                    if machine.node_id == node_id and machine.hostname == hostname:
                        for instance_name in machine.exited_instance_name_list:
                            server_config[instance_name] = instance_name
                        for container_name in set(local_configs) & set(server_config):
                            LOGGER.info(f"Restarting exited container {container_name}")
                            containers[container_name].start()
                            LOGGER.info(f"Container {container_name} restarted")

                        
        if msg.topic() == TOPIC201:
            try:
                data = parse_raw_as(Topic201Model, msg.value())
            except ValidationError as e:
                LOGGER.error(f"{e}")
            else:
                if utils.has_ip_address(str(data.ip_address)):
                    LOGGER.info("Sending TOPIC200 to refresh connection")
                    hostname = utils.get_hostname()
                    node_id = UUID4(utils.get_hardware_id())
                    PRODUCER.poll(0)
                    topic200data = Topic200Model(node_id=node_id, hostname=hostname, ip_address=str(data.ip_address))
                    PRODUCER.produce(TOPIC200, topic200data.json())


def main():
    try:
        consume()
    except KeyboardInterrupt:
        LOGGER.info("Close consumers and flush producer")
    finally:
        PRODUCER.flush()
        CONSUMER.close()


if __name__ == "__main__":
    main()
