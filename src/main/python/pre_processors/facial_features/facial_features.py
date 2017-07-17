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
import cv2
import numpy as np

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Procees input data
def callback(ch, method, properties, body):
    print('connected!', body)

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, '')
    s.connect(body)

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)
        print(msgdata)
        cv2.imshow('frame', np.array(msgdata))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #ch.basic_publish(exchange='pre-processor', routing_key='asr_incremental.data.{}'.format(participant), body=json.dumps(data))
    s.close()

mq = MessageQueue()
mq.bind_to_queue(exchange='sensors', routing_key='video.new_sensor.*', callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
