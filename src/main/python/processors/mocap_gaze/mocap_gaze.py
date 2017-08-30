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
def callback(_mq, get_shifted_time, routing_key, body):
    #json.load
    print(body)
    print("-------------------------------------------------")

mq = MessageQueue('mocap-gaze-processor')

#mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['mocap_processing']), callback=callback)
mq.bind_queue(exchange='pre-processor', routing_key="{}.*".format(settings['messaging']['tobii_processing']), callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
