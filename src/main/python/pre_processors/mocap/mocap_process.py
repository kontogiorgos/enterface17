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
from collections import defaultdict

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Dictionaries
mocap_dict = defaultdict(lambda : defaultdict(dict))
# white = glasses1
# pink = kinnect1
# blue = glasses2
# orange = kinnect2
# brown = glasses3
# black = kinnect3

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('connected!')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body)

    # Initiate parameters
    frame = "0"
    objects = "0"
    name = "0"
    pname = "0"
    position = "0"
    rotation = "0"
    marker0 = "0"
    marker1 = "0"
    marker2 = "0"
    marker3 = "0"

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)

        # Get frame
        r0 = re.search('Frame Number: (.*)', msgdata)
        if r0:
            frames = r0.group(1)
            if frames != '0':
                frame = frames
                print "----------------------------------------------------------------"
                print "Frame: ", frame

        # Check how many objects
        #r1 = re.search('Subjects (.+?):', msgdata)
        #if r1:
            #objects = r1.group(1)
            #objects = objects[1]
            #print "Objects: ", objects

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

            r3a = re.search('_(.*)', msgdata)
            if r3a:
                pname = r3a.group(1)
                print "Participant Name: ", pname

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

        # Put values on a dictionary
        mocap_dict[pname]['participant'] = pname
        mocap_dict[pname]['position'] = position
        mocap_dict[pname]['rotation'] = rotation
        mocap_dict[pname]['marker0'] = marker0
        mocap_dict[pname]['marker1'] = marker1
        mocap_dict[pname]['marker2'] = marker2
        mocap_dict[pname]['marker3'] = marker3

        # Send processed data
        r10 = re.search('Waiting for new frame...', msgdata)
        if r10:
            # Send one by one the participant json files
            # White
            json_data = {
            	"frame": frame,
            	"participant": "red",
            	"coord": "xyz_left",
            	"head": {
            		"type": "glasses",
            		"name":  "glasses_red",
            		"position": {"x": 209.886, "y": 2296.58, "z": 852.55},
            		"rotation": {"x": 0.0488613, "y": -0.0312445, "z": 0.912453, "w": 0.405051},
            		"markers":
            		[
            			{
            				"name": "glasses1a",
            				"position": {"x": 154.961, "y": 2351.84, "z": 861.614}
            			},
            			{
            				"name": "glasses1c",
            				"position": {"x": 119.116, "y": 2315.4, "z": 854.728}
            			},
            			{
            				"name": "glasses1d",
            				"position": {"x": 258.76, "y": 2203.29, "z": 842.933}
            			},
            			{
            				"name": "glasses1b",
            				"position": {"x": 282.3, "y": 2268.21, "z": 848.115}
            			}
            		]
            	},
            	"glove_left": {},
            	"glove_right": {}
            }

            key = settings['messaging']['mocap_processing']
            participant = routing_key.rsplit('.', 1)[1]
            routing_key = "{key}.{participant}".format(key=key, participant=participant)
            _mq.publish(exchange='pre-processor', routing_key=routing_key, body=json.dumps(json_data))
    s.close()

mq = MessageQueue()
mq.bind_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
