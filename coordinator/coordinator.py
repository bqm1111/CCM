"""simple producer"""
import json
import logging
import logging.config
import os
import socket
import subprocess
import urllib
import uuid
import time
from dynaconf import Dynaconf
import models
from confluent_kafka import Consumer, Producer
from database import Base, SessionLocal, engine
from pydantic import UUID4, parse_raw_as
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import and_
import sys
sys.path.append("../")

from schemas.config_schema import (DsAppConfig, DsInstanceConfig,
                                   FACE_align_config, FACE_pgie_config,
                                   FACE_sgie_config, MOT_pgie_config,
                                   MOT_sgie_config, SingleSourceConfig,
                                   SourcesConfig, parse_txt_as)
from schemas.topic_schema import (TOPIC301,TOPIC200, TOPIC201, TOPIC210, TOPIC220, TOPIC300, TOPIC222,
                                  DsInstance, NodeInfo, ExitedInstanceInfo, Topic200Model,
                                  Topic201Model, TOPIC210Model, Topic220Model, Topic222Model
                                  )

settings = Dynaconf(settings_file='settings.toml')
log_config = os.path.join(os.path.dirname(__file__), "logging.ini")

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.config.fileConfig(log_config, disable_existing_loggers=False)
LOGGER = logging.getLogger(__file__)

BOOTSTRAP_SERVER = settings.BOOTSTRAP_SERVER
PRODUCER = Producer({'bootstrap.servers': BOOTSTRAP_SERVER})
RUNNING = True
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

CONSUMER.subscribe([TOPIC200, TOPIC220, TOPIC300, TOPIC301])

Base.metadata.create_all(engine)

DATABASE = SessionLocal()

def get_hardware_id():
    """get hardware id of machine. eg. 7ca68a9b822e4abfaaa0c05fad5c6081"""
    p = subprocess.run(["cat", "/etc/machine-id"], capture_output=True)
    return p.stdout.decode().rstrip()

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def create_sample_TOPIC210():
    with open("sample_configs/app_conf.json", "r") as f:
        appconfig = json.load(f)
    with open("sample_configs/source_list.json", "r") as f:
        source_list_json = json.load(f)
    source_list = []
    for cam in source_list_json["sources"]:
        source_list.append(SingleSourceConfig.parse_obj(cam))

    
    with open("sample_configs/faceid_primary.txt") as f:
        face_pgie_json, _ = parse_txt_as(FACE_pgie_config, f.read())
    with open("sample_configs/mot_primary.txt") as f:
        mot_pgie_json, _ = parse_txt_as(MOT_pgie_config, f.read())

    with open("sample_configs/faceid_secondary.txt") as f:
        face_sgie_json, _ = parse_txt_as(FACE_sgie_config, f.read())

    with open("sample_configs/mot_sgie.txt") as f:
        mot_sgie_json, _ = parse_txt_as(MOT_sgie_config, f.read())

    with open("sample_configs/faceid_align_config.txt") as f:
        face_align_json, _ = parse_txt_as(FACE_align_config, f.read())

    face_pgie_conf = FACE_pgie_config.parse_obj(face_pgie_json)
    face_sgie_conf = FACE_sgie_config.parse_obj(face_sgie_json)
    face_align_conf = FACE_align_config.parse_obj(face_align_json)
    mot_pgie_conf = MOT_pgie_config.parse_obj(mot_pgie_json)
    mot_sgie_conf = MOT_sgie_config.parse_obj(mot_sgie_json)
    app_conf = DsAppConfig.parse_obj(appconfig)
    source_conf = SourcesConfig(sources=source_list)

    instance_config = DsInstanceConfig(appconfig=app_conf, 
                                    sourceconfig=source_conf,
                                    face_pgie=face_pgie_conf,
                                    face_sgie=face_sgie_conf,
                                    face_align=face_align_conf,
                                    mot_pgie=mot_pgie_conf,
                                    mot_sgie=mot_sgie_conf)
    deepstream_instance_info_list = []
    deepstream_instance_info_list.append(DsInstance(name="deepstream-1", config=instance_config))
    deepstream_instance_info_list.append(DsInstance(name="deepstream-2", config=instance_config))

    hostname = socket.gethostname()
    node_id = UUID4(get_hardware_id())
    return TOPIC210Model(agent_info_list=[NodeInfo(hostname=hostname,
                                                node_id=node_id,
                                                node_config_list=deepstream_instance_info_list)])
def generate_exited_instance_list():
    DATABASE.flush()
    exited_list = []
    for agent in DATABASE.query(models.Agent).options(joinedload(models.Agent.dsInstance)).all():
        DATABASE.refresh(agent)
        if not agent.connected:
            continue
        exited_instance_name_list = []
        for dsInstance in agent.dsInstance:
            DATABASE.refresh(dsInstance)
            if dsInstance.status == 'exited':
                exited_instance_name_list.append(dsInstance.instance_name)
        
        exited_list.append(ExitedInstanceInfo(hostname=agent.hostname, node_id=agent.node_id, exited_instance_name_list=exited_instance_name_list))
    return Topic222Model(exited_list=exited_list)       

def generate_new_configuration():
    LOGGER.info("Generating new configuration from database")
    DATABASE.flush()
    
    agent_info_list = []
    for agent in DATABASE.query(models.Agent).options(joinedload(models.Agent.dsInstance)).all():
        DATABASE.refresh(agent)
        if not agent.connected:
            continue
        hostname = agent.hostname
        node_id = uuid.UUID(agent.node_id)
        instance_info_list = []
        
        for dsInstance in agent.dsInstance:
            DATABASE.refresh(dsInstance)
            cameras = DATABASE.query(models.Camera).where(models.Camera.dsInstance_id == dsInstance.id).all()
            source_list = []
            for camera in cameras:
                DATABASE.refresh(camera)
                try:
                    cam = DATABASE.query(models.Camera).where(models.Camera.camera_id == camera.camera_id).one()
                except NoResultFound:
                    LOGGER.warning(f"No camera with camera_id {camera.camera_id} in agent {agent.agent_name} is found in database")
                except MultipleResultsFound:
                    LOGGER.error(f"Multiple camera with camera_id {camera.camera_id} in agent {agent.agent_name} are found in database")
                else:
                    url_password = urllib.parse.quote_plus(cam.password)
                    rtsp_address = "rtsp://" + cam.username + ":" + url_password + "@" + cam.ip_address + "/main"
                    source = dict()
                    source["camera_id"] = str(cam.camera_id)
                    source["address"] = rtsp_address
                    source["encode_type"] = cam.encodeType
                    source["type"] = cam.type
                    source_list.append(SingleSourceConfig.parse_obj(source))
            source_conf = SourcesConfig(sources=source_list)
            app_config = dsInstance.to_app_conf_dict()
            app_conf = DsAppConfig.parse_obj(app_config)
            
            with open("sample_configs/faceid_primary.txt") as f:
                face_pgie_json, _ = parse_txt_as(FACE_pgie_config, f.read())
            with open("sample_configs/mot_primary.txt") as f:
                mot_pgie_json, _ = parse_txt_as(MOT_pgie_config, f.read())

            with open("sample_configs/faceid_secondary.txt") as f:
                face_sgie_json, _ = parse_txt_as(FACE_sgie_config, f.read())

            with open("sample_configs/mot_sgie.txt") as f:
                mot_sgie_json, _ = parse_txt_as(MOT_sgie_config, f.read())

            with open("sample_configs/faceid_align_config.txt") as f:
                face_align_json, _ = parse_txt_as(FACE_align_config, f.read())
            
            face_pgie_conf = FACE_pgie_config.parse_obj(face_pgie_json)
            face_sgie_conf = FACE_sgie_config.parse_obj(face_sgie_json)
            face_align_conf = FACE_align_config.parse_obj(face_align_json)
            mot_pgie_conf = MOT_pgie_config.parse_obj(mot_pgie_json)
            mot_sgie_conf = MOT_sgie_config.parse_obj(mot_sgie_json)
            face_pgie_conf.gpu_id = dsInstance.gpu_id
            face_sgie_conf.gpu_id = dsInstance.gpu_id
            mot_pgie_conf.gpu_id = dsInstance.gpu_id
            mot_sgie_conf.gpu_id = dsInstance.gpu_id

            instance_config = DsInstanceConfig(appconfig=app_conf, 
                                    sourceconfig=source_conf,
                                    face_pgie=face_pgie_conf,
                                    face_sgie=face_sgie_conf,
                                    face_align=face_align_conf,
                                    mot_pgie=mot_pgie_conf,
                                    mot_sgie=mot_sgie_conf)
            
            instance_info_list.append(DsInstance(name=dsInstance.instance_name,
                                                 config=instance_config))
        agent_info_list.append(NodeInfo(hostname=hostname,
                                        node_id=node_id,
                                        node_config_list=instance_info_list))
    return TOPIC210Model(agent_info_list=agent_info_list)


def update_configuration():
    topic210data = generate_new_configuration()
    PRODUCER.produce(TOPIC210, topic210data.json())


def produce():
    start = time.time()   
    while True:
        current = time.time()
        if current - start > settings.check_exited_container_interval:
            start = current
            print("sending TOPIC222 to restart exited container")
            topic222data = generate_exited_instance_list()
            PRODUCER.produce(TOPIC222, topic222data.json())

        msg = CONSUMER.poll(1)
        if msg is None:
            continue
        if msg.error():
            LOGGER.error(f"Consumer error")

        if msg.topic() == TOPIC200:
            data = parse_raw_as(Topic200Model, msg.value())
            agent = DATABASE.query(models.Agent).where(models.Agent.ip_address == str(data.ip_address)).one()
            
            agent.hostname = data.hostname
            agent.node_id = str(data.node_id)
            agent.connected = True
            DATABASE.commit()       
                
        if msg.topic() == TOPIC220:
            data = parse_raw_as(Topic220Model, msg.value())
            node_id = str(data.node_id)
            try:
                agent = DATABASE.query(models.Agent).where(models.Agent.node_id == node_id).one()
            except NoResultFound:
                LOGGER.warning(f"No agent with node_id {node_id} is found in database")
            else:
                status_list = data.status
                for instance in status_list:
                    try:
                        dsInstance = DATABASE.query(models.DsInstance).where(and_(models.DsInstance.agent_id == agent.id,
                                                                              models.DsInstance.instance_name == instance.instance_name)).one()
                    except NoResultFound:
                        LOGGER.warning(f"No dsInstance with name {instance.instance_name} in agent {agent.agent_name} is found in database")
                    else:
                        dsInstance.status = instance.state
                        DATABASE.commit()
                        
        if msg.topic() == TOPIC300:
            update_configuration()
            
        if msg.topic() == TOPIC301:
            # Query from database and send message to all computers whose IPs are listed in the database(TOPIC201)
            all_agents = DATABASE.query(models.Agent).all()
            for agent in all_agents:
                topic201data = create_TOPIC201(agent=agent, name="VTX")    
                PRODUCER.poll(0)
                PRODUCER.produce(TOPIC201, topic201data.json())

                

def create_TOPIC201(agent: models.Agent, name: str):
    if not agent.agent_name:
        return Topic201Model(agent_name=agent.agent_name, ip_address=agent.ip_address)
    else:
        return Topic201Model(agent_name=name, ip_address=agent.ip_address)

def main():
    """main function to be call"""
    try:
        produce()
    except KeyboardInterrupt:
        LOGGER.info("Close consumers and flush producer")
    finally:
        PRODUCER.flush()
        CONSUMER.close()


if __name__ == "__main__":
    main()

