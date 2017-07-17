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
    name = "0"

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
                print "----------------------------------------------------------------"
                print "Frame: ", frame

        # Check how many objects
        r1 = re.search('Subjects (.+?):', msgdata)
        if r1:
            objects = r1.group(1)
            objects = objects[1]
            print "Objects: ", objects

        # Get Object No
        r2 = re.search('Subject #(.*)', msgdata)
        if r2:
            objectno = r2.group(1)
            print "Object: ", objectno

        # Get Object name
        r3 = re.search('Root Segment: (.*)', msgdata)
        if r3:
            name = r3.group(1)
            print "Name: ", name

        # Get object position
        r4 = re.search('Global Translation: (.+?) False', msgdata)
        if r4:
            position = r4.group(1)
            print "Position: ", position

        # Get object rotation
        r5 = re.search('Global Rotation Quaternion: (.+?) False', msgdata)
        if r5:
            rotation = r5.group(1)
            print "Rotation: ", rotation

        # Get marker 0 position
        r6 = re.search('Marker #0: (.+?) False', msgdata)
        if r6:
            marker0 = r6.group(1)
            print "Marker 0: ", marker0

        # Get marker 1 position
        r7 = re.search('Marker #1: (.+?) False', msgdata)
        if r7:
            marker1 = r7.group(1)
            print "Marker 1: ", marker1

        # Get marker 2 position
        r8 = re.search('Marker #2: (.+?) False', msgdata)
        if r8:
            marker2 = r8.group(1)
            print "Marker 2: ", marker2

        # Get marker 3 position
        r9 = re.search('Marker #3: (.+?) False', msgdata)
        if r9:
            marker3 = r9.group(1)
            print "Marker 3: ", marker3

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
