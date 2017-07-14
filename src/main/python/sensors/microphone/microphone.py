import pyaudio
import sys
import time
import msgpack
sys.path.append('../..')
import numpy as np
import re
from shared import create_zmq_server, MessageQueue



FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 2000

zmq_socket_1, zmq_server_addr_1 = create_zmq_server()
zmq_socket_2, zmq_server_addr_2 = create_zmq_server()

mq = MessageQueue()

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    d= p.get_device_info_by_index(i)
    print('[{}] {}'.format(d['index'], d['name']))
device_index = int(input('Select device: '))

device = p.get_device_info_by_index(device_index)

device_names = re.search('\[(.*)\]\s\/\sm-audio', device['name']).group(1).split(',')

mq.publish(
    exchange='sensors', routing_key='microphone.new_sensor.{}'.format(device_names[0]), body=zmq_server_addr_1
)
mq.publish(
    exchange='sensors', routing_key='microphone.new_sensor.{}'.format(device_names[1]), body=zmq_server_addr_2
)


def callback(in_data, frame_count, time_info, status):
    result = np.fromstring(in_data, dtype=np.uint16)
    result = np.reshape(result, (frame_count, 2))
    zmq_socket_1.send(msgpack.packb((result[:, 0].tobytes(), time.time())))
    zmq_socket_2.send(msgpack.packb((result[:, 1].tobytes(), time.time())))
    return None, pyaudio.paContinue


stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input_device_index=device_index,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

input('[*] Serving at {} and {}. To exit press enter'.format(zmq_server_addr_1, zmq_server_addr_2))

stream.stop_stream()
stream.close()
zmq_socket_1.close()
zmq_socket_2.close()
