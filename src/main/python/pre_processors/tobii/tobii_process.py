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

# Get tobii address and participant
if len(sys.argv) != 3:
    exit('Error. Python tobii_sensor.py')
participant = sys.argv[1]
ip = sys.argv[2]

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Dictionaries
tobii_dict = defaultdict(lambda : defaultdict(dict))
# white = glasses1
tobii_dict['white']['type'] = 'glasses1'
# pink = kinnect1
# blue = glasses2
tobii_dict['blue']['type'] = 'glasses2'
# orange = kinnect2
# brown = glasses3
tobii_dict['brown']['type'] = 'glasses3'
# black = kinnect3

# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    print('connected!')

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body.get('address'))

    # Initiate parameters
    # frame = None
    # objects = None
    # name = None
    # pname = None
    # position = None
    # rotation = None
    # marker0 = None
    # marker0name = None
    # marker0pos = None
    # marker1 = None
    # marker1name = None
    # marker1pos = None
    # marker2 = None
    # marker2name = None
    # marker2pos = None
    # marker3 = None
    # marker3name = None
    # marker3pos = None

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)

        # Get frame
        # r0 = re.search('Frame Number: (.*)', msgdata)
        # if r0:
        #     frames = r0.group(1)
        #     if frames != '0':
        #         frame = frames
        #         print "----------------------------------------------------------------"
        #         print "Frame: ", frame
        #
        # # Check how many objects
        # #r1 = re.search('Subjects (.+?):', msgdata)
        # #if r1:
        #     #objects = r1.group(1)
        #     #objects = objects[1]
        #     #print "Objects: ", objects
        #
        # # Get Object No
        # r2 = re.search('Subject #(.*)', msgdata)
        # if r2:
        #     objectno = r2.group(1)
        #     print "Object: ", objectno
        #
        # # Get Object name
        # r3 = re.search('Root Segment: (.*)', msgdata)
        # if r3:
        #     name = r3.group(1)
        #     print "Name: ", name
        #
        #     r3a = re.search('_(.*)', msgdata)
        #     if r3a:
        #         pname = r3a.group(1)
        #         print "Participant Name: ", pname
        #
        # # Get object position
        # r4 = re.search('Global Translation: (.+?) False', msgdata)
        # if r4:
        #     position = r4.group(1)
        #     print "Position: ", position
        #
        # # Get object rotation
        # r5 = re.search('Global Rotation Quaternion: (.+?) False', msgdata)
        # if r5:
        #     rotation = r5.group(1)
        #     print "Rotation: ", rotation
        #
        # # Get marker 0 position
        # r6 = re.search('Marker #0: (.+?) False', msgdata)
        # if r6:
        #     marker0 = r6.group(1)
        #     # Get marker 0 name
        #     r6a = re.search('(.*) \(.*\)', marker0)
        #     if r6a:
        #         marker0name = r6a.group(1)
        #         print "Marker 0 Name: ", marker0name
        #     # Get marker 0 position
        #     marker0pos = re.search(r'\((.*?)\)', marker0).group(1)
        #     print "Marker 0 Position: ", marker0pos
        #
        # # Get marker 1 position
        # r7 = re.search('Marker #1: (.+?) False', msgdata)
        # if r7:
        #     marker1 = r7.group(1)
        #     # Get marker 1 name
        #     r7a = re.search('(.*) \(.*\)', marker1)
        #     if r7a:
        #         marker1name = r7a.group(1)
        #         print "Marker 1 Name: ", marker1name
        #     # Get marker 1 position
        #     marker1pos = re.search(r'\((.*?)\)', marker1).group(1)
        #     print "Marker 1 Position: ", marker1pos
        #
        # # Get marker 2 position
        # r8 = re.search('Marker #2: (.+?) False', msgdata)
        # if r8:
        #     marker2 = r8.group(1)
        #     # Get marker 2 name
        #     r8a = re.search('(.*) \(.*\)', marker2)
        #     if r8a:
        #         marker2name = r8a.group(1)
        #         print "Marker 2 Name: ", marker2name
        #     # Get marker 2 position
        #     marker2pos = re.search(r'\((.*?)\)', marker2).group(1)
        #     print "Marker 2 Position: ", marker2pos
        #
        # # Get marker 3 position
        # r9 = re.search('Marker #3: (.+?) False', msgdata)
        # if r9:
        #     marker3 = r9.group(1)
        #     # Get marker 3 name
        #     r9a = re.search('(.*) \(.*\)', marker3)
        #     if r9a:
        #         marker3name = r9a.group(1)
        #         print "Marker 3 Name: ", marker3name
        #     # Get marker 3 position
        #     marker3pos = re.search(r'\((.*?)\)', marker3).group(1)
        #     print "Marker 3 Position: ", marker3pos

        # # Put values on a dictionary
        # mocap_dict[pname]['participant'] = pname
        # mocap_dict[pname]['object'] = name
        # mocap_dict[pname]['position'] = position
        # mocap_dict[pname]['rotation'] = rotation
        # mocap_dict[pname]['marker0'] = marker0
        # mocap_dict[pname]['marker1'] = marker1
        # mocap_dict[pname]['marker2'] = marker2
        # mocap_dict[pname]['marker3'] = marker3

        # Send processed data
        # r10 = re.search('Waiting for new frame...', msgdata)
        # if r10 and all(mocap_dict[pname].values()):
        #     # Send one by one the participant json files
        #     def sendjson(participantname):
        #         # Parse coordinates to float
        #         def poscoordtofloat(coord):
        #             if coord != '0':
        #                 x, y, z = map(float, coord[1:][:-1].split(", "))
        #                 return {"x": x, "y": y, "z": z}
        #             else:
        #                 return None
        #         def rotcoordtofloat(coord):
        #             if coord != '0':
        #                 x, y, z, w = map(float, coord[1:][:-1].split(", "))
        #                 return {"x": x, "y": y, "z": z, "w": w}
        #             else:
        #                 return None
        #
        #         json_data = {
        #         	"frame": frame,
        #         	"participant": mocap_dict[participantname]['participant'],
        #         	"coord": "xyz_left",
        #         	"head": {
        #         		"type": mocap_dict[participantname]['type'],
        #         		"name":  mocap_dict[participantname]['object'],
        #         		"position": poscoordtofloat(mocap_dict[participantname]['position']),
        #         		"rotation": rotcoordtofloat(mocap_dict[participantname]['rotation']),
        #         		"markers":
        #         		[
        #         			{
        #         				"name": marker0name,
        #         				"position": poscoordtofloat(marker0pos)
        #         			},
        #         			{
        #         				"name": marker1name,
        #         				"position": poscoordtofloat(marker1pos)
        #         			},
        #         			{
        #         				"name": marker2name,
        #         				"position": poscoordtofloat(marker2pos)
        #         			},
        #         			{
        #         				"name": marker3name,
        #         				"position": poscoordtofloat(marker3pos)
        #         			}
        #         		]
        #         	},
        #         	"glove_left": {},
        #         	"glove_right": {}
        #         }
        #
        #         key = settings['messaging']['mocap_processing']
        #         new_routing_key = "{key}.{participant}".format(key=key, participant=participantname)
        #         _mq.publish(exchange='pre-processor', routing_key=new_routing_key, body=json_data)
        #
        #         return;
        #
        #     # Send for every participant
        #     sendjson('white')
        #     sendjson('pink')
        #     sendjson('blue')
        #     sendjson('orange')
        #     sendjson('brown')
        #     sendjson('black')
        print msgdata
    s.close()

mq = MessageQueue('tobii-preprocessor')

if participant == 'white':
    routing_key_p = settings['messaging']['new_sensor_tobii_1']
elif participant == 'blue':
    routing_key_p = settings['messaging']['new_sensor_tobii_2']
elif participant == 'brown':
    routing_key_p = settings['messaging']['new_sensor_tobii_3']

mq.bind_queue(exchange='sensors', routing_key=routing_key_p, callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
