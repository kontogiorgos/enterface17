
import zmq
import pika
import time
import msgpack
import cv2
import sys
import zmq
sys.path.append('../..')
sys.path.append('../')
from shared import create_zmq_server, MessageQueue
# zmq_socket, zmq_server_addr = create_zmq_server()


# Set up zmq server
context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_port = zmq_socket.bind('tcp://*:8083')
zmq_server_addr = 'tcp://{}:{}'.format('127.0.0.1', 8083)


mq = MessageQueue()

mq.publish(exchange='sensors', routing_key='video.new_sensor.1', body=zmq_server_addr)


cap = cv2.VideoCapture(0)
while(True):
    _, frame = cap.read()
    print(_, frame)
    if frame:
        zmq_socket.send(msgpack.packb((frame, time.time())))
    # cv2.imshow('frame', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break


input()
print("finished recording")

cap.release()
zmq_socket.close()
