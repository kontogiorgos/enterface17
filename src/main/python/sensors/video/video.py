
import zmq
import pika
import time
import msgpack
import cv2
import sys
import zmq
import numpy as np
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
zmq_socket, zmq_server_addr = create_zmq_server()
import socket

if len(sys.argv) != 3:
    exit('error. python video.py [color] [port]')
participant = sys.argv[1]
port = int(sys.argv[1])


UDP_IP = "127.0.0.1"

mq = MessageQueue()
mq.publish(
    exchange='sensors',
    routing_key='scren_capture.new_sensor.{}'.format(participant),
    body={'address': zmq_server_addr, 'file_type': 'video'}
)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, port))

while True:
    data, addr = sock.recvfrom(10000)
    zmq_socket.send(msgpack.packb((data, time.time())))

input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

sock.close()
zmq_socket.close()
