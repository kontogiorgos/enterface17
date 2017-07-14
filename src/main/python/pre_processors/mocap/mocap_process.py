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
    print('connected!')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body)

    frame = "0"
    objects = "0"

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)

        # Process mocap data
        # Get frame
        r0 = re.search('Frame Number: (.*)', msgdata)
        if r0:
            frames = r0.group(1)
            if frames != '0':
                frame = frames
                print "frame: ", frame

        # Check how many objects
        r1 = re.search('Subjects (.+?):', msgdata)
        if r1:
            objects = r1.group(1)
            objects = objects[1]
            print "objects: ", objects

        # next

        # Send processed data
        # message = {
        #   'action': 'start',
        #   'content-type': 'audio/l16;rate=44100',
        #   'word_confidence': True,
        #   'timestamps': True,
        #   'continuous' : True,
        #   'interim_results' : True,
        # }
        #
        # print(json.dumps(message))
        # ws.send(json.dumps(message).encode('utf-8'))
        #ch.basic_publish(exchange='pre-processor', routing_key='asr_incremental.data.{}'.format(participant), body=json.dumps(data))
    s.close()

mq = MessageQueue()
mq.bind_to_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
