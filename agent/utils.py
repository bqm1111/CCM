import os
import subprocess
import json
from typing import Tuple
from logging import Logger
import docker
from docker.models.containers import Container


def get_hardware_id():
    """get hardware id of machine. eg. 7ca68a9b822e4abfaaa0c05fad5c6081"""
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)
    return p.stdout.decode().rstrip()


def read_config(container: Container) -> Tuple[str, str]:
    """read config of container
    return tuple of (container.id, config)
    """
    for mount in container.attrs['Mounts']:
        if mount['Destination'] == '/workspace/config':
            break
    # read config from mount['Source']
    with open(mount['Source'] + '/app_conf.json') as f:
        config = f.read()
        return (container.name, json.loads(config))


def update_config(container: Container, config: json):
    for mount in container.attrs['Mounts']:
        if mount['Destination'] == '/workspace/config':
            break
    with open(mount['Source'] + '/config.json', 'w') as f:
        json.dump(config, f)

def write_config(config: json, file: str) -> None:
    """write config to file"""
    dir = os.path.dirname(file)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    # TODO: format the configuration base on definition from deepstream
    with open(file, 'w') as f:
        json.dump(config, f)


def new_container(image_name: str,
                  container_name: str,
                  config_file: str,
                  dclient: docker.DockerClient):
    """start a new container with config"""
    config_folder = os.path.dirname(config_file)
    container = dclient.containers.run(image_name,
                                       name=container_name,
                                       # runtime="nvidia",
                                       restart_policy={
                                           "Name": "on-failure", "MaximumRetryCount": 5},
                                       volumes={config_folder: {
                                           'bind': '/workspace/config', 'mode': 'ro'}},
                                       detach=True)
    return container


def ordered(obj):
    """sort json objects. Useful to compare two json"""
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

if __name__ == "__main__":
    image_name = 'deepstream-app'
    docker_client = docker.from_env()
    
    for container in docker_client.containers.list():  # only running container
        if container.attrs['Config']['Image'] == image_name:
            break

    print(read_config(container))
