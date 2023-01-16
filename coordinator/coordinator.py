"""simple producer"""
import json
import socket
import subprocess
from time import sleep

from confluent_kafka import Producer
from pydantic import UUID4, IPvAnyAddress

from schemas.config_schema import (DsAppConfig, DsInstanceConfig,
                                   FACE_align_config, FACE_pgie_config,
                                   FACE_sgie_config, MOT_pgie_config,
                                   MOT_sgie_config, SingleSourceConfig,
                                   SourcesConfig, parse_txt_as)
from schemas.topic_schema import (TOPIC200, TOPIC201, TOPIC210, TOPIC220,
                                  DsInstance, NodeInfo, TOPIC210Model)

BOOTSTRAP_SERVER = "172.21.100.242:9092"

PRODUCER = Producer({'bootstrap.servers': BOOTSTRAP_SERVER})
RUNNING = True

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
    with open("../sample_configs/app_conf.json", "r") as f:
        appconfig = json.load(f)
    with open("../sample_configs/source_list.json", "r") as f:
        source_list_json = json.load(f)
    source_list = []
    for cam in source_list_json["sources"]:
        source_list.append(SingleSourceConfig.parse_obj(cam))


    with open("../sample_configs/faceid_primary.txt") as f:
        face_pgie_json, _ = parse_txt_as(FACE_pgie_config, f.read())
    with open("../sample_configs/mot_primary.txt") as f:
        mot_pgie_json, _ = parse_txt_as(MOT_pgie_config, f.read())

    with open("../sample_configs/faceid_secondary.txt") as f:
        face_sgie_json, _ = parse_txt_as(FACE_sgie_config, f.read())

    with open("../sample_configs/mot_sgie.txt") as f:
        mot_sgie_json, _ = parse_txt_as(MOT_sgie_config, f.read())

    with open("../sample_configs/faceid_align_config.txt") as f:
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

def produce():
    while RUNNING:
        # Trigger any available delivery report callbacks from previous produce() calls
        PRODUCER.poll(0)
        topic210data = create_sample_TOPIC210()
        print(f"sending data: {topic210data.agent_info_list[0]}")
        PRODUCER.produce(TOPIC210, topic210data.json(), callback=delivery_report)

        sleep(1)

def main():
    """main function to be call"""
    try:
        produce()
    except KeyboardInterrupt:
        global RUNNING
        RUNNING = False
        print("gracefully close consumers and flush producer")
    finally:
        PRODUCER.flush()


if __name__ == "__main__":
    main()


