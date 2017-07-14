import zmq
import pika
import json
import time
import msgpack
import re

# Iniciate la conneccion!
credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.108', credentials=credentials))
channel = connection.channel()
channel.exchange_declare(exchange='pre-processor', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

# Listen to mocap sensor
channel.queue_bind(exchange='sensors', queue=queue_name, routing_key='mocap.new_sensor.*')

# Procees input data
def callback(ch, method, properties, body):
    participant = method.routing_key.rsplit('.', 1)[1]
    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string(zmq.SUBSCRIBE, unicode(''))
    s.connect(body)

    frame = "0"
    objects = "0"

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)

        # Process mocap data
        # Get frame
        r0 = re.search('Frame Number: (.*)', msgdata)
        if r0:
            frames = r0.group(1)
            if frames != '0':
                frame = frames
                print "frame: ", frame

        # Check how many objects
        r1 = re.search('Subjects (.+?):', msgdata)
        if r1:
            objects = r1.group(1)
            objects = objects[1]
            print "objects: ", objects

        

        # Send processed data
        #ch.basic_publish(exchange='pre-processor', routing_key='mocap.data.{}'.format(participant), body=json.dumps(data))
    s.close()

channel.basic_consume(callback, queue=queue_name)

print('[*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
