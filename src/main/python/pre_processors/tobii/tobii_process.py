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
from threading import Thread

# Settings
SETTINGS_FILE = '../../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# Print messages
DEBUG = False

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
    print('Connected! Receiving data')

    def run(participant, message_queue):
        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string(zmq.SUBSCRIBE, u'')
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
            if data == b'CLOSE':
                if DEBUG: print('connection closed')
                break
            msgdata, timestamp = msgpack.unpackb(data, use_list=False)

            if DEBUG: print "----------------------------------------------------------------"
            # Get timestamp
            r0 = re.search('"ts":(.*)', msgdata)
            if r0:
                timestamp = r0.group(1)
                timestamp = timestamp.split(',')[0]
                if DEBUG: print "Timestamp: ", timestamp

            # Get pupil diameter
            r1 = re.search('"pd":(.*)', msgdata)
            if r1:
                r1a = re.search('"eye":"left"', msgdata)
                r1b = re.search('"eye":"right"', msgdata)
                if r1a:
                    pdleft = r1.group(1)
                    pdleft = pdleft.split(',')[0]
                    if DEBUG: print "PD Left: ", pdleft
                if r1b:
                    pdright = r1.group(1)
                    pdright = pdright.split(',')[0]
                    if DEBUG: print "PD Right: ", pdright

            # Get gaze direction
            r2 = re.search('"gd":(.*)', msgdata)
            if r2:
                r2a = re.search('"eye":"left"', msgdata)
                r2b = re.search('"eye":"right"', msgdata)
                if r2a:
                    gdleft = r2.group(1)
                    gdleft = gdleft.split(',')[0] + "," + gdleft.split(',')[1] + "," + gdleft.split(',')[2]
                    if DEBUG: print "GD Left: ", gdleft
                if r2b:
                    gdright = r2.group(1)
                    gdright = gdright.split(',')[0] + "," + gdright.split(',')[1] + "," + gdright.split(',')[2]
                    if DEBUG: print "GD Right: ", gdright

            # Get gaze position
            r3 = re.search('"gp":(.*)', msgdata)
            if r3:
                gp = r3.group(1)
                gp = gp.split(',')[0] + "," + gp.split(',')[1]
                gp = gp.split('}')[0]
                if DEBUG: print "GP: ", gp

            # Get gaze position 3d
            r4 = re.search('"gp3":(.*)', msgdata)
            if r4:
                gp3 = r4.group(1)
                gp3 = gp3.split(',')[0] + "," + gp3.split(',')[1] + "," + gp3.split(',')[2]
                gp3 = gp3.split('}')[0]
                if DEBUG: print "GP3: ", gp3

            # # Put values on a dictionary
            # mocap_dict[pname]['participant'] = pname
            # mocap_dict[pname]['object'] = name
            # mocap_dict[pname]['position'] = position
            # mocap_dict[pname]['rotation'] = rotation
            # mocap_dict[pname]['marker0'] = marker0
            # mocap_dict[pname]['marker1'] = marker1
            # mocap_dict[pname]['marker2'] = marker2
            # mocap_dict[pname]['marker3'] = marker3

            # # Send processed data
            # r10 = re.search('Waiting for new frame...', msgdata)
            # if r10 and all(mocap_dict[pname].values()):
            #     # Send one by one the participant json files
            #     def sendjson(participantname):
            #         # Parse coordinates to float
            #         def poscoordtofloat(coord):
            #             if coord and coord != '0':
            #                 x, y, z = map(float, coord[1:][:-1].split(", "))
            #                 return {"x": x, "y": y, "z": z}
            #             else:
            #                 return None
            #         def rotcoordtofloat(coord):
            #             if coord and coord != '0':
            #                 x, y, z, w = map(float, coord[1:][:-1].split(", "))
            #                 return {"x": x, "y": y, "z": z, "w": w}
            #             else:
            #                 return None
            #
            #         json_data = {
            #             "frame": frame,
            #             "participant": mocap_dict[participantname]['participant'],
            #             "coord": "xyz_left",
            #             "head": {
            #                 "type": mocap_dict[participantname]['type'],
            #                 "name":  mocap_dict[participantname]['object'],
            #                 "position": poscoordtofloat(mocap_dict[participantname]['position']),
            #                 "rotation": rotcoordtofloat(mocap_dict[participantname]['rotation']),
            #                 "markers":
            #                 [
            #                     {
            #                         "name": mocap_dict[participantname]['marker0name'],
            #                         "position": poscoordtofloat(mocap_dict[participantname]['marker0pos'])
            #                     },
            #                     {
            #                         "name": mocap_dict[participantname]['marker1name'],
            #                         "position": poscoordtofloat(mocap_dict[participantname]['marker1pos'])
            #                     },
            #                     {
            #                         "name": mocap_dict[participantname]['marker2name'],
            #                         "position": poscoordtofloat(mocap_dict[participantname]['marker2pos'])
            #                     },
            #                     {
            #                         "name": mocap_dict[participantname]['marker3name'],
            #                         "position": poscoordtofloat(mocap_dict[participantname]['marker3pos'])
            #                     }
            #                 ]
            #             },
            #             "glove_left": {},
            #             "glove_right": {}
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
        s.close()
    participant = routing_key.rsplit('.', 1)[1]
    thread = Thread(target = run, args=(participant, _mq))
    thread.deamon = True
    thread.start()

mq = MessageQueue('tobii-preprocessor')

#routing_key = '{}.{}'.format(settings['messaging']['new_sensor_tobii'], participant)

mq.bind_queue(exchange='sensors', routing_key="{}.*".format(settings['messaging']['new_sensor_tobii']), callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
