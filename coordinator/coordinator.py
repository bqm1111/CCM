"""simple producer"""
from time import sleep
from json import dumps
from confluent_kafka import Producer

TOPIC200 = "AgentInfo"
TOPIC201 = "AgentCommand"
TOPIC210 = "AgentConfig"
TOPIC220 = "AgentResponse"
BOOSTRAP_SERVER = "172.21.100.167:9092"

p = Producer({'bootstrap.servers': BOOSTRAP_SERVER})

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

    data = {'number': e}
    p.produce(TOPIC201, dumps(data).encode('utf-8'), callback=delivery_report)
    sleep(1)
p.flush()
