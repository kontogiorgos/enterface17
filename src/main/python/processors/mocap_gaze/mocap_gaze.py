import zmq
import pika
import json
import time
import msgpack

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

    while True:
        data = s.recv()
        msgdata, timestamp = msgpack.unpackb(data, use_list=False)
        print timestamp
        #ch.basic_publish(exchange='pre-processor', routing_key='mocap.data.{}'.format(participant), body=json.dumps(data))
    s.close()

channel.basic_consume(callback, queue=queue_name)

print('[*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
