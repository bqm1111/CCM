import os
import subprocess
import json
from typing import Tuple
from logging import Logger
import docker
from docker.models.containers import Container

def get_hardware_id():
    """get hardware id of machine"""
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)
    return p.stdout.decode().rstrip()

def read_config(container: Container) -> Tuple[str, str]:
    """read config of container 
    return tuple of (container.id, config)"""
    for mount in container.attrs['Mounts']:
        if mount['Destination'] == '/workspace/config':
            break
    
    