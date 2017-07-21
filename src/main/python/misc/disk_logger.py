import tempfile
import sys
import zmq
import msgpack
sys.path.append('..')
from shared import MessageQueue
import datetime
import yaml
import os
from threading import Thread
import queue
import json
import time


SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

log_path = os.path.join(settings['logging']['sensor_path'], session_name)
q = queue.Queue()
running = True
os.mkdir(log_path)

def callback(mq, get_shifted_time, routing_key, body):
    print('connected')
    def run():
        global running



        a = 0
        go_on = True

        while go_on:
            try:
                os.mkdir(os.path.join(
                    log_path,
                    session_name,
                    '{}-{}'.format(routing_key, a))
                )
                go_on = False
            except:
                a += 1





        log_file = os.path.join(
            log_path,
            session_name,
            '{}-{}'.format(routing_key, a), 'data.{}'.format(body.get('file_type', 'unknown'))
        )

        print('[{}] streamer connected'.format(log_file))

        file_obj = tempfile.NamedTemporaryFile()
        file_obj.seek(0)



        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string( zmq.SUBSCRIBE, '' )
        s.RCVTIMEO = 10000
        s.connect(body['address'])

        t = time.time()

        while running:
            try:
                data = s.recv()
                msgdata, timestamp = msgpack.unpackb(data, use_list=False)
                file_obj.write(msgdata)

                if time.time() - t >= 5:
                    t = time.time()
                    file_obj.seek(0)
                    q.put((log_file, file_obj))
            except zmq.error.Again:
                break

        file_obj.seek(0)
        q.put((log_file, file_obj))
        s.close()
        print('[{}] streamer closed'.format(log_file))

    _thread = Thread(target = run)
    _thread.deamon = True
    _thread.start()


def storage_writer():
    global running

    while running or q.qsize() != 0:
        log_file, data = q.get()
        second_file_obj = tempfile.NamedTemporaryFile()
        second_file_obj.seek(0)
        second_file_obj.write(data.read())
        second_file_obj.seek(0)
        with open(log_file, 'ab') as f:
            f.write(second_file_obj.read())
        print('{} writes left to do..', q.qsize())
    data.close()
    print('writer closed'.format(log_file))

thread = Thread(target = storage_writer)
thread.deamon = True
thread.start()


mq = MessageQueue('logger')
mq.bind_queue(
    exchange='sensors', routing_key='*.new_sensor.*', callback=callback
)


thread2 = Thread(target = mq.listen)
thread2.deamon = True
thread2.start()

input('[*] Waiting for messages. To exit press enter')
running = False
print('ugly hack: now press CTRL-C')
mq.stop()
