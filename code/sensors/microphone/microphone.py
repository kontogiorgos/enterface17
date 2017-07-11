import pyaudio
import pika
import sys
import time
import msgpack
sys.path.append('..')
from create_zmq_server import create_zmq_server

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2205

zmq_socket, zmq_server_addr = create_zmq_server()


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='microphone.new_sensor.1', body=zmq_server_addr)

def callback(in_data, frame_count, time_info, status):
    zmq_socket.send(msgpack.packb((in_data, time.time())))
    return (None, pyaudio.paContinue)

stream = pyaudio.PyAudio().open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

input('[*] Sering at {}. To exit press enter'.format(zmq_server_addr))


stream.stop_stream()
stream.close()
zmq_socket.close()
