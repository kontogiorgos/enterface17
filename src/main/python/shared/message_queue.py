import time
import sys
import yaml
import os
import pika


SETTINGS_FILE = os.path.abspath(
    os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'settings.yaml')
)


class MessageQueue(object):
    def __init__(self):
        settings = yaml.safe_load(open(SETTINGS_FILE, 'r').read())

        messaging_settings = settings['messaging']
        broker_host = messaging_settings['broker_host']
        broker_port = messaging_settings['broker_port']
        broker_user = messaging_settings['broker_user']
        broker_pass = messaging_settings['broker_pass']
        credentials = pika.PlainCredentials(broker_user, broker_pass)
        connection_parameters = pika.ConnectionParameters(
            host=broker_host, port=broker_port, credentials=credentials
        )
        connection = pika.BlockingConnection(connection_parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=settings['messaging']['pre_processing'], type='topic')
        self.channel.exchange_declare(exchange=settings['messaging']['sensors'], type='topic')

    def publish(self, exchange='', routing_key='', body=''):
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)

    def bind_to_queue(self, exchange='', routing_key='', callback=None):
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(callback, queue=queue_name)

    def listen(self):
        self.channel.start_consuming()
