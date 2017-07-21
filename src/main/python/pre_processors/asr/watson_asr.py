import json
import pika
import zmq
from threading import Thread
from watson_developer_cloud import AuthorizationV1
from watson_developer_cloud import SpeechToTextV1
import websocket
import msgpack
from websocket._abnf import ABNF
import time
from twisted.python import log
from twisted.internet import reactor
import sys
sys.path.append('../..')
from shared import MessageQueue

with open('.watson_credentials.json') as f:
    credentials = json.loads(f.read())
if not credentials:
    exit('no credentials')


authorization = AuthorizationV1(username=credentials['username'], password=credentials['password'])
token = authorization.get_token(url=SpeechToTextV1.default_url)



timer = None
last_timer = None


def callback(_mq, get_shifted_time, routing_key, body):
    participant = routing_key.rsplit('.', 1)[1]

    print('connected {}'.format(method.routing_key))


    def connect_to_watson():
        def on_open(ws):
            def run():
                global timer, last_timer
                context = zmq.Context()
                s = context.socket(zmq.SUB)
                s.setsockopt_string( zmq.SUBSCRIBE, '' )
                s.connect(body.get('address'))
                message = {
                  'action': 'start',
                  'content-type': 'audio/l16;rate=44100',
                  'word_confidence': True,
                  'timestamps': True,
                  'continuous' : True,
                  'interim_results' : True,
                }

                print(json.dumps(message))
                ws.send(json.dumps(message).encode('utf-8'))

                while True:
                    data = s.recv()
                    msgdata, timestamp = msgpack.unpackb(data, use_list=False)
                    if not timer: timer = timestamp
                    last_timer = timestamp
                    ws.send(msgdata, ABNF.OPCODE_BINARY)
                s.close()
                ws.close()
                print("thread terminating...")
            thread = Thread(target = run)
            thread.deamon = True
            thread.start()

        def on_error(self, error):
            """Print any errors."""
            print(error)

        def on_close(ws):
            print("Closed down")

        def on_message(ws, m):
            print('message')
            global timer
            msg = json.loads(str(m))
            if msg.get('results'):
                data = {
                    'time_start_asr': timer,
                    'time_until_asr': last_timer,
                    'text': msg['results'][0].get('alternatives', [{}])[0].get('transcript')
                }
                timer = None

                routing_key = 'asr.data.{}' if msg["results"][0]["final"] else 'asr.incremental_data.{}'
                _mq.publish(exchange='pre-processor', routing_key='asr_incremental.data.{}'.format(participant), body=data)


        headers = {'X-Watson-Authorization-Token': token}

        ws = websocket.WebSocketApp('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize',
                                    header=headers,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()


    thread = Thread(target = connect_to_watson)
    thread.deamon = True
    thread.start()

mq = MessageQueue('watson-asr-preprocessor')
mq.bind_queue(
    exchange='sensors', routing_key='microphone.new_sensor.*', callback=callback
)

print('[*] Waiting for messages. To exit press CTRL+C')
mq.listen()
