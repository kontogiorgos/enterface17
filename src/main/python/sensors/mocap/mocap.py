import pika
import sys
import time
import msgpack
sys.path.append('..')
from create_zmq_server import create_zmq_server
from subprocess import Popen, PIPE

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()

# Estabish la conneccion!
credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.108', credentials=credentials))
channel = connection.channel()
channel.basic_publish(exchange='sensors', routing_key='mocap.new_sensor.1', body=zmq_server_addr)

# Wait a minute!
time.sleep(2)

# Get mocap data stream
process = Popen(['./vicon/ViconDataStreamSDK_CPPTest', '192.168.0.108'], stdout=PIPE, stderr=PIPE)

# Send each data stream
for stdout_line in iter(process.stdout.readline, ""):
    print('Sending mocap stream')
    zmq_socket.send(msgpack.packb((stdout_line, time.time())))

# Print input
input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

# Close connection
zmq_socket.close()
