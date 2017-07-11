import pyaudio
import zmq
import pika
import time
import msgpack
import socket

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2205

# Get ip
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

# Set up zmq server
context = zmq.Context()
s = context.socket(zmq.PAIR)
zmq_port = s.bind_to_random_port('tcp://*', max_tries=150)
zmq_server_addr = 'tcp://{}:{}'.format(ip, zmq_port)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='microphone.new_sensor.1', body=zmq_server_addr)

def callback(in_data, frame_count, time_info, status):
    s.send(msgpack.packb((in_data, time.time())))
    return (None, pyaudio.paContinue)

stream = pyaudio.PyAudio().open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback
)

input()


print("finished recording")

stream.stop_stream()
stream.close()
s.close()
