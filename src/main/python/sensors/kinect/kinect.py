import sys
import pika
import time
import msgpack
sys.path.append('..')
from create_zmq_server import create_zmq_server
from GazeSense import GazeSenseSub

KINECT_STREAM_TIMEOUT = 10.0  # the amount of time data from the Kinect will be sent

zmq_socket, zmq_server_addr = create_zmq_server()

credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.108', credentials=credentials))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='kinect.new_sensor.1', body=zmq_server_addr)


def my_callback(data):
    zmq_socket.send(msgpack.packb((data, time.time())))

gc = GazeSenseSub(callback=my_callback, verbose=True)

# Sleep, just to emulate your main thread process
try:
    time.sleep(KINECT_STREAM_TIMEOUT)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    # clean up
    gc.stop()

input('[*] Sering at {}. To exit press enter'.format(zmq_server_addr))

zmq_socket.close()
