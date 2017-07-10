import zmq
import pika
import time
import msgpack


HOST = 'tcp://*:5556'
SELF_HOST = 'tcp://127.0.0.1:5556'

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind(HOST)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='video.new_sensor.1', body=SELF_HOST)


cap = cv2.VideoCapture(0)
while(True):
    _, frame = cap.read()
    socket.send(msgpack.packb((frame, time.time())))
    # cv2.imshow('frame', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break


input()
print("finished recording")

cap.release()
socket.close()
