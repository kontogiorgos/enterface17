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



credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.108', credentials=credentials))
channel = connection.channel()
channel.exchange_declare(exchange='pre-processor', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='sensors', queue=queue_name, routing_key='microphone.new_sensor.*')

timer = None
last_timer = None

def callback(ch, method, properties, body):
    participant = method.routing_key.rsplit('.', 1)[1]


    def on_open(ws):
        def run():
            global timer, last_timer
            context = zmq.Context()
            s = context.socket(zmq.SUB)
            s.setsockopt_string( zmq.SUBSCRIBE, '' )
            s.connect(body)
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
        global timer
        msg = json.loads(str(m))
        if msg.get('results'):
            data = {
                'time_stat_asr': timer,
                'time_until_asr': last_timer,
                'text': msg['results'][0].get('alternatives', [{}])[0].get('transcript')
            }
            timer = None

            routing_key = 'asr.data.{}' if msg["results"][0]["final"] else 'asr.incremental_data.{}'
            ch.basic_publish(exchange='pre-processor', routing_key='asr_incremental.data.{}'.format(participant), body=json.dumps(data))

    with open('.watson_credentials.json') as f:
        credentials = json.loads(f.read())
    if credentials:
        authorization = AuthorizationV1(username=credentials['username'], password=credentials['password'])
        token = authorization.get_token(url=SpeechToTextV1.default_url)
        headers = {'X-Watson-Authorization-Token': token}

        ws = websocket.WebSocketApp('wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize',
                                    header=headers,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()
    else:
        print('no credentials')

channel.basic_consume(callback, queue=queue_name)

print('[*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
