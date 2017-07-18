import tempfile
import sys
import zmq
import msgpack
sys.path.append('..')
from smb.SMBConnection import SMBConnection
from shared import MessageQueue
import datetime


# There will be some mechanism to capture userID, password, client_machine_name, server_name and server_ip
# client_machine_name can be an arbitary ASCII string
# server_name should match the remote machine name, or else the connection will be rejected

session_name = datetime.datetime.now().isoformat().replace('.', '_').replace(':', '_')



def callback(ch, method, properties, body):
    print('connected')
    # participant = method.routing_key.rsplit('.', 1)[1]
    log_file = '/logger/{}/{}/data.txt'.format(session_name, method.routing_key)



    conn = SMBConnection('werewolf', 'furhatfurhat', 'KTHCloud', 'KTHCloud', use_ntlm_v2 = True) #,
    assert conn.connect('192.168.0.103', 139)

    conn.createDirectory('werewolf', '/logger/{}'.format(session_name))
    conn.createDirectory('werewolf', '/logger/{}/{}'.format(session_name, method.routing_key))

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
                conn.storeFile('werewolf', log_file, file_obj)
                print('writing')

                i = 0
            else:
                i += 1
    except KeyboardInterrupt:
        file_obj.seek(0)
        conn.storeFile('werewolf', log_file, file_obj)
        print('last write')

    file_obj.close()
    conn.close()
    s.close()






mq = MessageQueue()
mq.bind_to_queue(
    exchange='sensors', routing_key='*.new_sensor', callback=callback
)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
