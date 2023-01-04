"""simple producer"""
from time import sleep
from json import dumps
from confluent_kafka import Producer
from schemas.config_schema import (
    TOPIC210Model, 
    TOPIC200, TOPIC201, TOPIC210, TOPIC220,
    SingleSourceConfig,
    InstanceConfig,
    SourcesConfig,
    DsAppConfig,
    MOT_pgie_config,
    MOT_sgie_config,
    FACE_align_config,
    FACE_pgie_config,
    FACE_sgie_config
    
)

BOOTSTRAP_SERVER = "172.21.100.242:9092"

PRODUCER = Producer({'bootstrap.servers': BOOTSTRAP_SERVER})
RUNNING = True

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def produce():
    while RUNNING:
        # Trigger any available delivery report callbacks from previous produce() calls
        PRODUCER.poll(0)
        appconfig = DsAppConfig(kafka_connection_str="172.21.100.242:9092", streammux_batch_size=1)

        source = SourcesConfig(
            sources=[
                SingleSourceConfig(camera_id=3, address="rtsp://admin:123456a%40@172.21.111.101/main"),
                SingleSourceConfig(camera_id=1, address="rtsp://admin:123456a%40@172.21.111.104/main"),
                SingleSourceConfig(camera_id=2, address="rtsp://admin:123456a%40@172.21.111.111/main"),
                SingleSourceConfig(camera_id=4, address="rtsp://admin:123456a%40@172.21.104.112/main"),
            ]
        )

        mot_pgie = MOT_pgie_config(
            gpu_id=0,
            batch_size=len(source.sources),
            model_engine_file="../data/models/trt/deepsort_detector.trt",
            labelfile_path="../data/labels/mot_pgie_labels.txt",
            custom_lib_path="../build/src/nvdsinfer_customparser/libnvds_infercustomparser.so",
        )
        
        face_pgie = FACE_pgie_config(
            gpu_id=0,
            batch_size=len(source.sources),
            model_engine_file="../build/model_b12_gpu0_fp16.engine",
            labelfile_path="../data/labels/face_labels.txt",
            custom_lib_path="../build/src/facedetection/libnvds_facedetection.so",
        )

        mot_sgie = MOT_sgie_config(
            gpu_id=0,
            batch_size=12,
            model_engine_file="../data/models/trt/deepsort_extractor.trt",
        )

        face_sgie = FACE_sgie_config(
            gpu_id=0,
            batch_size=32,
            model_engine_file="../data/models/trt/glint360k_r50.trt",
            custom_lib_path="../build/src/facefeature/libnvds_parsenone.so",
            parse_bbox_func_name="NvDsInferParseNone",
        )
        

        face_align = FACE_align_config(
            tensor_buf_pool_size=10,
            input_object_min_width=50,
            input_object_max_width=3840,
            input_object_min_height=50,
            input_object_max_height=2160,
        )

        instance_config = InstanceConfig(
            appconfig=appconfig,
            sourceconfig=source,
            mot_pgie=mot_pgie,
            face_pgie=face_pgie,
            mot_sgie=mot_sgie,
            face_sgie=face_sgie,
            face_align=face_align
        )

        topic210data = TOPIC210Model(instance_config=instance_config)
        print(f"sending data: {topic210data.instance_config}")
        # p.produce(TOPIC210, dumps(data).encode('utf-8'), callback=delivery_report)
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


