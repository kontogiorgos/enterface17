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

if len(sys.argv) != 2:
    print('No routing key given, assuming *.new_sensor.*')
    listen_to_routing_key = '*.new_sensor.*'
else:
    listen_to_routing_key = sys.argv[1]



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
    def run():
        global running

        a = 0
        go_on = True

        while go_on:
            try:
                os.mkdir(os.path.join(log_path, '{}-{}'.format(routing_key, a)))
                go_on = False
            except FileExistsError:
                a += 1

        log_file = os.path.join(
            log_path,
            '{}-{}'.format(routing_key, a), 'data.{}'.format(body.get('file_type', 'unknown'))
        )


        print('[{}] streamer connected'.format(log_file))
        with open(os.path.join(log_path, 'info.txt'), 'w') as f:
            f.write(json.dumps(body))


        context = zmq.Context()
        s = context.socket(zmq.SUB)
        s.setsockopt_string( zmq.SUBSCRIBE, '' )
        # s.RCVTIMEO = 30000
        s.connect(body['address'])

        t = time.time()

        d = bytes()
        while running:
            try:
                data = s.recv()
                d += data

                #msgdata, timestamp = msgpack.unpackb(data, use_list=False)
                #if type(msgdata) == dict:
                #file_obj.write(json.dumps((msgdata, timestamp)).encode('utf-8'))
                #else:
                #    file_obj.write(msgdata)

                if time.time() - t > 5:
                    q.put((log_file, d))
                    d = bytes()
            except KeyboardInterrupt:
                running = False


        if d: q.put((log_file, d))

        s.close()
        print('[{}] streamer closed'.format(log_file))

    _thread = Thread(target = run)
    _thread.deamon = True
    _thread.start()


def storage_writer():
    global running

    while running or q.qsize() != 0:
        log_file, data = q.get()
        with open(log_file, 'ab') as f:
            f.write(data)
        print('{} writes left to do..', q.qsize())
    data.close()
    print('writer closed'.format(log_file))

thread = Thread(target = storage_writer)
thread.deamon = True
thread.start()


mq = MessageQueue('logger')
mq.bind_queue(
    exchange='sensors', routing_key=listen_to_routing_key, callback=callback
)


thread2 = Thread(target = mq.listen)
thread2.deamon = True
thread2.start()

input('[*] Waiting for messages. To exit press enter')
running = False
print('ugly hack: now press CTRL-C')
mq.stop()
