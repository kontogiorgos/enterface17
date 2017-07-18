import tempfile
import sys
import zmq
import msgpack
sys.path.append('..')
from smb.SMBConnection import SMBConnection
from shared import MessageQueue
import datetime
import yaml
import os
from threading import Thread
import queue
import json


with open('.smb_credentials.json') as f:
    credentials = json.loads(f.read())
if not credentials:
    exit('no credentials')

SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)
settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')

q = queue.Queue()


def callback(mq, get_shifted_time, routing_key, body):
    print('connected')
    log_file = '/logger/{}/{}/data.txt'.format(session_name, routing_key)

    conn = SMBConnection(
        credentials['username'],
        credentials['password'],
        credentials['client_machine_name'],
        credentials['server_name'],
        use_ntlm_v2 = True
    )
    assert conn.connect(settings['file_storage']['host'], settings['file_storage']['port'])

    conn.createDirectory(settings['file_storage']['service_name'], '/logger/{}'.format(session_name))
    conn.createDirectory(settings['file_storage']['service_name'], '/logger/{}/{}'.format(session_name, routing_key))
    conn.close()


    file_obj = tempfile.NamedTemporaryFile()
    file_obj.seek(0)



    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.setsockopt_string( zmq.SUBSCRIBE, '' )
    s.connect(body)

    i = 0
    try:
        while True:
            data = s.recv()
            msgdata, timestamp = msgpack.unpackb(data, use_list=False)
            file_obj.write(msgdata)

            if i >= 7000:
                file_obj.seek(0)
                q.put((log_file, file_obj))
                i = 0
            else:
                i += 1
    except KeyboardInterrupt:
        file_obj.seek(0)
        q.put((log_file, file_obj))
        print('last write')

    file_obj.close()

    s.close()


def storage_writer():
    conn = SMBConnection(
        credentials['username'],
        credentials['password'],
        credentials['client_machine_name'],
        credentials['server_name'],
        use_ntlm_v2 = True
    )
    assert conn.connect(settings['file_storage']['host'], settings['file_storage']['port'])


    while True:
        log_file, data = q.get()
        second_file_obj = tempfile.NamedTemporaryFile()
        second_file_obj.seek(0)
        print(data)
        second_file_obj.write(data.read())
        second_file_obj.seek(0)

        conn.storeFile(settings['file_storage']['service_name'], log_file, second_file_obj)
        print('{} writes left to do..', q.qsize())
    conn.close()

thread = Thread(target = storage_writer)
thread.deamon = True
thread.start()


mq = MessageQueue()
mq.bind_queue(
    exchange='sensors', routing_key='*.new_sensor', callback=callback
)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
