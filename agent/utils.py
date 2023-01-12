import glob
import json
import os
import subprocess
import tarfile
import time
from io import BytesIO, StringIO
from logging import Logger
from typing import List, Tuple

import docker
from docker.models.containers import Container

from schemas.config_schema import (DsAppConfig, DsInstanceConfig,
                                   FACE_align_config, FACE_pgie_config,
                                   FACE_sgie_config, MOT_pgie_config,
                                   MOT_sgie_config, SingleSourceConfig,
                                   SourcesConfig, parse_txt_as)


def get_hardware_id():
    """get hardware id of machine. eg. 7ca68a9b822e4abfaaa0c05fad5c6081"""
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)
    return p.stdout.decode().rstrip()

def _read_deepstream_app_config(container:Container, filename):
    """Read a deepstream app config file in a container"""
    try:
        stream, _ = container.get_archive(filename)
    except:
        raise RuntimeError("Error reading deepstream-app config file")
    else:
        file_obj = BytesIO()
        for i in stream:
            file_obj.write(i)
        file_obj.seek(0)
        
        with tarfile.open(mode='r', fileobj=file_obj) as tar:
            for member in tar.getmembers():
                f=tar.extractfile(member)
                content=f.read()
                return content


def read_config(container: Container) -> Tuple[str, DsInstanceConfig]:
    """read config of container
    return tuple of (container.id, config)
    """
    data = _read_deepstream_app_config(container, "workspace/configs/faceid_primary.txt")
    face_pgie_json, mot_sgie_txt = parse_txt_as(FACE_pgie_config, data.decode('utf-8'))    
    
    data = _read_deepstream_app_config(container, "workspace/configs/faceid_secondary.txt")
    face_sgie_json, mot_sgie_txt = parse_txt_as(FACE_sgie_config, data.decode('utf-8'))
    
    data = _read_deepstream_app_config(container, "workspace/configs/faceid_align_config.txt")
    face_align_json, mot_sgie_txt = parse_txt_as(FACE_align_config, data.decode('utf-8'))
    
    data = _read_deepstream_app_config(container, "workspace/configs/mot_primary.txt")
    mot_pgie_json, mot_sgie_txt = parse_txt_as(MOT_pgie_config, data.decode('utf-8'))
    
    data = _read_deepstream_app_config(container, "workspace/configs/mot_sgie.txt")
    mot_sgie_json, mot_sgie_txt = parse_txt_as(MOT_sgie_config, data.decode('utf-8'))
    
    source_list_json = json.loads(_read_deepstream_app_config(container, "workspace/configs/source_list.json"))
    source_list = []
    for cam in source_list_json["stream"]:
        source_list.append(SingleSourceConfig.parse_obj(cam))

    app_conf_json = json.loads(_read_deepstream_app_config(container, "workspace/configs/app_conf.json"))
    
    face_pgie_conf = FACE_pgie_config.parse_obj(face_pgie_json)
    face_sgie_conf = FACE_sgie_config.parse_obj(face_sgie_json)
    face_align_conf = FACE_align_config.parse_obj(face_align_json)
    mot_pgie_conf = MOT_pgie_config.parse_obj(mot_pgie_json)
    mot_sgie_conf = MOT_sgie_config.parse_obj(mot_sgie_json)
    app_conf = DsAppConfig.parse_obj(app_conf_json)
    source_conf = SourcesConfig(sources=source_list)
    
    
    instance_config = DsInstanceConfig(appconfig=app_conf, 
                                     sourceconfig=source_conf,
                                     face_pgie=face_pgie_conf,
                                     face_sgie=face_sgie_conf,
                                     face_align=face_align_conf,
                                     mot_pgie=mot_pgie_conf,
                                     mot_sgie=mot_sgie_conf)

    return (container.name, instance_config)

def copy_to_container(container: Container, src_path: str, dst_path: str):
    all_config_file = os.listdir(src_path)
    
    for file in all_config_file:
        with create_archive(os.path.join(src_path,file)) as archive:
            container.put_archive(path=dst_path, data=archive)

def create_archive(file):
    pw_tarstream = BytesIO()
    pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
    with open(file, "r") as f:
        file_data = f.read()
    tarinfo = tarfile.TarInfo(name=file)
    tarinfo.size = len(file_data)
    tarinfo.mtime = time.time()
    pw_tar.addfile(tarinfo, BytesIO(file_data.encode('utf8')))
    pw_tar.close()
    pw_tarstream.seek(0)
    return pw_tarstream



if __name__ == "__main__":
    image_name = 'deepstream-app'
    docker_client = docker.from_env()
    
    for container in docker_client.containers.list():  # only running container
        if container.attrs['Config']['Image'] == image_name:
            break

    print(read_config(container))
