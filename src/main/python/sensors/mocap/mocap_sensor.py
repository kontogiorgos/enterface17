import pika
import sys
import time
import msgpack
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
from subprocess import Popen, PIPE
import yaml

# Get platform
if len(sys.argv) != 2:
    exit('Error.')
platform = sys.argv[1]

# Print messages
DEBUG = False

# Settings
SETTINGS_FILE = '../../settings.yaml'

# Define server
zmq_socket, zmq_server_addr = create_zmq_server()
mq = MessageQueue('mocap-sensor')

# Estabish la conneccion!
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())
mq.publish(
    exchange='sensors',
    routing_key=settings['messaging']['new_sensor_mocap'],
    body={'address': zmq_server_addr, 'file_type': 'txt'}
)

# Wait a minute!
#time.sleep(2)

# Get mocap data stream
if platform == 'mac':
    process = Popen(['./vicon_mac/ViconDataStreamSDK_CPPTest', settings['messaging']['mocap_host']], stdout=PIPE, stderr=PIPE)
elif platform == 'win64':
    process = Popen(['./vicon_windows64/ViconDataStreamSDK_CPPTest.exe', settings['messaging']['mocap_host']], stdout=PIPE, stderr=PIPE)

print('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))

# Send each data stream
try:
    for stdout_line in iter(process.stdout.readline, ""):
        if DEBUG: print(stdout_line)
        zmq_socket.send(msgpack.packb((stdout_line, time.time())))
finally:
    # Close connection
    zmq_socket.send(b'CLOSE')
    zmq_socket.close()
