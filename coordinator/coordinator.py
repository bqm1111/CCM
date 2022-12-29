"""simple producer"""
from time import sleep
from json import dumps
from confluent_kafka import Producer
from schemas.agent_config_schema import TOPIC210Model

TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"
BOOTSTRAP_SERVER = "172.21.100.167:9092"

p = Producer({'bootstrap.servers': BOOTSTRAP_SERVER})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


for e in range(1000):
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)
    topic210data = TOPIC210Model(URIs = [
                "rtsp://admin:123456a%40@172.21.104.100",
                "rtsp://admin:123456a%40@172.21.104.101",
                "rtsp://admin:123456a%40@172.21.104.102",
                "rtsp://admin:123456a%40@172.21.104.103"
            ])
    data = {'number': e}
    # p.produce(TOPIC210, dumps(data).encode('utf-8'), callback=delivery_report)
    p.produce(TOPIC210, topic210data.json(), callback=delivery_report)

    sleep(1)
p.flush()



