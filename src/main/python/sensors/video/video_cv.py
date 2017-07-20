import zmq
import pika
import time
import msgpack
import cv2
import sys
import zmq
import numpy as np
import subprocess
sys.path.append('../..')
from shared import create_zmq_server, MessageQueue
zmq_socket, zmq_server_addr = create_zmq_server()


if len(sys.argv) != 2:
    exit('error. python video_cv.py [color]')
participant = sys.argv[1]



mq = MessageQueue('video-webcam-sensor')


process = subprocess.Popen(
    ["/enterface/ffmpeg-20170711-0780ad9-win64-static/bin/ffmpeg.exe", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
    stderr=subprocess.PIPE
)
_, err = process.communicate()

data = str(err)
stuff = [
    ("white", data.index("vid_046d&pid_0843&mi_00#7&371f838&0&0000")),  # white webcam
    ("blue", data.index("vid_046d&pid_0843&mi_00#6&c7f0d35&0&0000")),  # blue webcam
    ("brown", data.index("046d&pid_08c9&mi_00#7&2ea013c4&0&0000"))  # brown webcam
]

# sort by appearance
sorted_devices = sorted(stuff, key=lambda x: x[1])

device_id = [x[0] for x in sorted_devices].index(participant)


camera = cv2.VideoCapture(device_id)
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT) # float

mq.publish(
    exchange='sensors',
    routing_key='webcam.new_sensor.{}'.format(participant),
    body={
        'address': zmq_server_addr,
        'file_type': 'cv-video',
        'img_size': {
            'width': width,
            'height': height,
            'channels': 3,
            'fps': 30,
        }
    }
)


while True:
    _, frame = camera.read()
    zmq_socket.send(msgpack.packb((frame.flatten().tobytes(), time.time())))

input('[*] Serving at {}. To exit press enter'.format(zmq_server_addr))


zmq_socket.close()
