import zmq
import pika
import json
import time
import msgpack
import re
import sys
sys.path.append('..')
from shared import MessageQueue
import yaml
import os
import json
from collections import defaultdict
import datetime

# Settings
SETTINGS_FILE = '../settings.yaml'
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

# files = {
#     'red': './asr-red.txt',
#     'white': './asr-red.txt',
#     'brown': './asr-red.txt',
#     'red': './asr-red.txt',
#     'red': './asr-red.txt',
#     'red': './asr-red.txt',
#     'red': './asr-red.txt',
# }

files = defaultdict(lambda x: './asr-{}.txt'.format(x))


session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

log_path = os.path.join(settings['logging']['asr_path'], session_name)

os.mkdir(log_path)




# Procees input data
def callback(_mq, get_shifted_time, routing_key, body):
    # participant = routing_key.rsplit('.', 1)[1]
    with open('{}/{}.txt'.format(log_path, routing_key), 'a') as f:
        f.write(json.dumps(body) + '\n')
    print(routing_key, body)
    print("-------------------------------------------------")

mq = MessageQueue('mocap-gaze-processor')

mq.bind_queue(exchange='pre-processor', routing_key="*.*.*", callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
