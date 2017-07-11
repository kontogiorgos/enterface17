import pika

from Player import Player
from Game import Game
from ruamel import yaml


class Environment(object):

    SETTINGS_FILE = "settings.yaml"

    def __init__(self):
        self.participants = [Player() for x in range(6)]
        self.settings = self._init_settings(Environment.SETTINGS_FILE)

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


        def callback(ch, method, properties, body):
            participant = method.routing_key.rsplit('.', 1)[1]


        channel.basic_consume(callback, queue=queue_name)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
