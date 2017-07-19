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
mocap_dict['white']['type'] = 'glasses'
# pink = kinnect1
mocap_dict['pink']['type'] = 'hat'
# blue = glasses2
mocap_dict['blue']['type'] = 'glasses'
# orange = kinnect2
mocap_dict['orange']['type'] = 'hat'
# brown = glasses3
mocap_dict['brown']['type'] = 'glasses'
# black = kinnect3
mocap_dict['black']['type'] = 'hat'

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('connected!')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body.get('address'))

    # Initiate parameters
    frame = "0"
    objects = "0"
    name = "0"
    pname = "0"
    position = "0"
    rotation = "0"
    marker0 = "0"
    marker0name = "0"
    marker0pos = "0"
    marker1 = "0"
    marker1name = "0"
    marker1pos = "0"
    marker2 = "0"
    marker2name = "0"
    marker2pos = "0"
    marker3 = "0"
    marker3name = "0"
    marker3pos = "0"

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
            # Get marker 0 name
            r6a = re.search('(.*) \(.*\)', marker0)
            if r6a:
                marker0name = r6a.group(1)
                print "Marker 0 Name: ", marker0name
            # Get marker 0 position
            marker0pos = re.search(r'\((.*?)\)', marker0).group(1)
            print "Marker 0 Position: ", marker0pos

        # Get marker 1 position
        r7 = re.search('Marker #1: (.+?) False', msgdata)
        if r7:
            marker1 = r7.group(1)
            # Get marker 1 name
            r7a = re.search('(.*) \(.*\)', marker1)
            if r7a:
                marker1name = r7a.group(1)
                print "Marker 1 Name: ", marker1name
            # Get marker 1 position
            marker1pos = re.search(r'\((.*?)\)', marker1).group(1)
            print "Marker 1 Position: ", marker1pos

        # Get marker 2 position
        r8 = re.search('Marker #2: (.+?) False', msgdata)
        if r8:
            marker2 = r8.group(1)
            # Get marker 2 name
            r8a = re.search('(.*) \(.*\)', marker2)
            if r8a:
                marker2name = r8a.group(1)
                print "Marker 2 Name: ", marker2name
            # Get marker 2 position
            marker2pos = re.search(r'\((.*?)\)', marker2).group(1)
            print "Marker 2 Position: ", marker2pos

        # Get marker 3 position
        r9 = re.search('Marker #3: (.+?) False', msgdata)
        if r9:
            marker3 = r9.group(1)
            # Get marker 3 name
            r9a = re.search('(.*) \(.*\)', marker3)
            if r9a:
                marker3name = r9a.group(1)
                print "Marker 3 Name: ", marker3name
            # Get marker 3 position
            marker3pos = re.search(r'\((.*?)\)', marker3).group(1)
            print "Marker 3 Position: ", marker3pos

        # Put values on a dictionary
        mocap_dict[pname]['participant'] = pname
        mocap_dict[pname]['object'] = name
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
            participantname = 'white'
            json_data = {
            	"frame": frame,
            	"participant": mocap_dict[participantname]['participant'],
            	"coord": "xyz_left",
            	"head": {
            		"type": mocap_dict[participantname]['type'],
            		"name":  mocap_dict[participantname]['object'],
            		"position": mocap_dict[participantname]['position'],
            		"rotation": mocap_dict[participantname]['rotation'],
            		"markers":
            		[
            			{
            				"name": marker0name,
            				"position": marker0pos
            			},
            			{
            				"name": marker1name,
            				"position": marker1pos
            			},
            			{
            				"name": marker2name,
            				"position": marker2pos
            			},
            			{
            				"name": marker3name,
            				"position": marker3pos
            			}
            		]
            	},
            	"glove_left": {},
            	"glove_right": {}
            }

            key = settings['messaging']['mocap_processing']
            participant = routing_key.rsplit('.', 1)[1]
            routing_key = "{key}.{participant}".format(key=key, participant=participant)
            _mq.publish(exchange='pre-processor', routing_key=routing_key, body=json_data)
    s.close()

mq = MessageQueue('mocap-preprocessor')
mq.bind_queue(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
