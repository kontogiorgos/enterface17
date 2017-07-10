import pyaudio
import zmq
import pika
import time
import msgpack

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2205
HOST = 'tcp://*:5555'
SELF_HOST = 'tcp://127.0.0.1:5555'

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind(HOST)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='microphone.new_sensor.1', body=SELF_HOST)

def callback(in_data, frame_count, time_info, status):
    socket.send(msgpack.packb((in_data, time.time())))
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
audio.terminate()
socket.close()
