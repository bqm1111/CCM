"""simple producer"""
from time import sleep
from json import dumps
from confluent_kafka import Producer
from schemas.config_schema import (
    TOPIC210Model, 
    TOPIC200, TOPIC201, TOPIC210, TOPIC220,
    SingleSourceConfig
)

BOOTSTRAP_SERVER = "172.21.100.167:9092"

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
        topic210data = TOPIC210Model(camera_info=[
            SingleSourceConfig(camera_id=3, address="rtsp://admin:123456a%40@172.21.111.101/main"),
            SingleSourceConfig(camera_id=1, address="rtsp://admin:123456a%40@172.21.111.104/main"),
            SingleSourceConfig(camera_id=2, address="rtsp://admin:123456a%40@172.21.111.111/main"),
            SingleSourceConfig(camera_id=4, address="rtsp://admin:123456a%40@172.21.104.112/main")
                ])
        # data = {'number': e}
        print(f"sending data: {topic210data.camera_info}")
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


