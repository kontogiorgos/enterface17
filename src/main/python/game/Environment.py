import pika

from Player import Player
from Game import Game
from ruamel import yaml

HOST = '192.168.0.100'
PORT = 32777


class Environment(object):

    SETTINGS_FILE = "../settings.yaml"

    def __init__(self):
        self.settings = self._init_settings(Environment.SETTINGS_FILE)
        self.participants = Player.create_players(self.settings['players'])
        self._init_subscription()
        self.game = None

    @staticmethod
    def _init_settings(settings_file):
        try:
            return yaml.safe_load(open(settings_file, 'r').read())
        except:
            raise IOError("An error has occurred while trying to load settings file.")

    def start_game(self, game=None):
        self.game = game if game and isinstance(game, Game) else Game(Environment.SETTINGS_FILE)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
        channel = connection.channel()
        channel.exchange_declare(exchange='environment', type='topic')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='processors', queue=queue_name, routing_key='*')

    def _init_subscription(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
        channel = connection.channel()

        channel.queue_declare(queue='processors')
        channel.basic_consume(self.process_processors_data, queue='processors', no_ack=True)

        channel.start_consuming()

    def process_processors_data(self, ch, method, properties, body):
        print(" [x] Received %r" % body)


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    connection.close()
