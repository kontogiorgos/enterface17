import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('../..')
from shared import MessageQueue
import yaml

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Procees input data
def callback(ch, method, properties, body):
    #json.load
    print(body)
    print("-------------------------------------------------")

mq = MessageQueue()

mq.bind_to_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['mocap_processing']), callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
