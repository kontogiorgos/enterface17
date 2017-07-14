import pyaudio
import sys
import time
import msgpack
sys.path.append('../..')
import numpy as np
from shared import create_zmq_server, MessageQueue



# zmq_socket, zmq_server_addr = create_zmq_server()
#
# credentials = pika.PlainCredentials('test', 'test')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.108', credentials=credentials))
# channel = connection.channel()
# channel.basic_publish(exchange='sensors', routing_key='microphone.new_sensor.1', body=zmq_server_addr)
#
# def callback(indata, frames, _time, status):
#     # print(round(indata[:,0].mean(), 2), round(indata[:,1].mean(), 2))
#     print(np.frombuffer(indata).shape)
#     zmq_socket.send(msgpack.packb(( np.frombuffer(indata)[:,1].tobytes() , time.time())))
#     # zmq_socket.send(msgpack.packb((indata, time.time())))
#
#
# with sd.RawInputStream(channels=2, samplerate=44100, callback=callback):
#     input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))
# zmq_socket.close()


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 2000

zmq_socket_1, zmq_server_addr_1 = create_zmq_server()
zmq_socket_2, zmq_server_addr_2 = create_zmq_server()

mq = MessageQueue()


mq.publish(
    exchange='sensors', routing_key='microphone.new_sensor.red', body=zmq_server_addr_1
)
mq.publish(
    exchange='sensors', routing_key='microphone.new_sensor.blue', body=zmq_server_addr_2
)


def callback(in_data, frame_count, time_info, status):
    result = np.fromstring(in_data, dtype=np.uint16)
    result = np.reshape(result, (frame_count, 2))
    zmq_socket_1.send(msgpack.packb((result[:, 0].tobytes(), time.time())))
    zmq_socket_2.send(msgpack.packb((result[:, 1].tobytes(), time.time())))
    return None, pyaudio.paContinue

stream = pyaudio.PyAudio().open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

input('[*] Serving at {} and {}. To exit press enter'.format(zmq_server_addr_1, zmq_server_addr_2))

stream.stop_stream()
stream.close()
zmq_socket_1.close()
zmq_socket_2.close()
