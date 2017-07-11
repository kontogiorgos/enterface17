import pika
import cv2
import json
import numpy as np
import time
import pickle

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()

channel.exchange_declare(exchange='sensors', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='sensors', queue=queue_name, routing_key='video.*')


def callback(ch, method, properties, body):
    data = pickle.loads(body)['time']
    print(properties, time.time() -  data)


    # img = np.array(json.loads(body), dtype='uint8')
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # channel.basic_publish(exchange='pre-processor', routing_key='video.1', body=json.dumps({'time': time.time(), 'accumulative_time_diff': 0, 'data': gray.tolist()}))

    # cv2.imshow('frame', )
    # cv2.waitKey(1)


channel.basic_consume(callback, queue=queue_name)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
