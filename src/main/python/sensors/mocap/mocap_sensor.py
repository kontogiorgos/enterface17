import pika
import sys
import time
import msgpack
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
from subprocess import Popen, PIPE
import yaml

# Settings
SETTINGS_FILE = '../../settings.yaml'

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue()

# Estabish la conneccion!
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())
mq.publish(exchange='sensors', routing_key=settings['messaging']['new_sensor_mocap'], body=zmq_server_addr)

# Wait a minute!
#time.sleep(2)

# Get mocap data stream
process = Popen(['./vicon/ViconDataStreamSDK_CPPTest', settings['messaging']['mocap_host']], stdout=PIPE, stderr=PIPE)

# Send each data stream
for stdout_line in iter(process.stdout.readline, ""):
    print(stdout_line)
    zmq_socket.send(msgpack.packb((stdout_line, time.time())))

# Print input
input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

# Close connection
zmq_socket.close()
