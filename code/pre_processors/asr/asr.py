from google.cloud import speech
import zmq
from threading import Thread
import queue
import pika
import json
import time
import msgpack

RATE = 44100


class MicAsFile(object):
    def __init__(self, address):
        self.address = address
        self._buff = queue.Queue()
        self.closed = True
        self.timer = None
        self.last_timer = None

    def __enter__(self):
        self.thread = Thread(target = self.socket_thread)
        self.thread.deamon = True
        self.thread.start()  # Execute B
        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
        self.thread.join()

    def socket_thread(self):
        self.closed = False
        context = zmq.Context()
        s = context.socket(zmq.PAIR)
        s.connect(self.address)

        while not self.closed:
            data = s.recv()
            self._buff.put(msgpack.unpackb(data, use_list=False))
        s.close()

    def read(self, _):
        if self.closed:
            return
        da, timer = self._buff.get()
        if not self.timer: self.timer = timer
        data = [da]
        while True:
            try:
                new_da, _ = self._buff.get(block=False)
                data.append(new_da)
            except queue.Empty:
                break

        if self.closed:
            return

        self.last_timer = self.timer

        # print('len: ', len(data))
        return b''.join(data)


speech_client = speech.Client()


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
channel = connection.channel()
channel.exchange_declare(exchange='sensors', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='sensors', queue=queue_name, routing_key='microphone.new_sensor.*')


def callback(ch, method, properties, body):
    print('-')
    method.routing_key.rsplit('.', 1)[1]
    with MicAsFile(body) as stream:
        while True:
            print('new!')
            audio_sample = speech_client.sample(
                stream=stream,
                encoding=speech.encoding.Encoding.LINEAR16,
                sample_rate_hertz=RATE
            )
            results_gen = audio_sample.streaming_recognize(language_code='en-US', interim_results=True, single_utterance=True)
            for result in results_gen:
                if not result.alternatives or result.stability < 0.5:
                    continue
                if stream.timer:
                    timer = stream.timer
                else:
                    timer = stream.last_timer
                print(time.time() - timer, result.stability, result.confidence, result.transcript)
                stream.timer = None

                data = {'transcript': result.transcript, 'confidence': result.confidence, 'is_final': result.is_final, 'stability': result.stability}
                channel.basic_publish(exchange='pre-processor', routing_key='asr.data.1', body=json.dumps(data))
                if result.is_final:
                    break



channel.basic_consume(callback, queue=queue_name)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
