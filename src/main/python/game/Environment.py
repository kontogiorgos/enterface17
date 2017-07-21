import pika,os,sys

from Player import Player
from Game import Game
from ruamel import yaml
sys.path.append('../../fatima/')
from FAtiMA import DecisionMaking
sys.path.append('../..')
from shared import MessageQueue


HOST = '192.168.0.100'
PORT = 32777


class Environment(object):

    FURHAT_HOME = "/Users/jdlopes/enterface17/src/main/python/"
    SETTINGS_FILE = os.path.join(FURHAT_HOME,'settings_local.yaml')

    def __init__(self):
        self.settings = self._init_settings(Environment.SETTINGS_FILE)
        self.participants = Player.create_players(self.settings['players'])
        self.fatima = DecisionMaking()
        #self._init_subscription()
        self.game = None
        self.mq_env = MessageQueue("environment")

    @staticmethod
    def _init_settings(settings_file):
        try:
            return yaml.safe_load(open(settings_file, 'r').read())
        except:
            raise IOError("An error has occurred while trying to load settings file.")

    def get_participant(self, participant_name):
       return [x for x in self.participants if x.name == participant_name][0]

    def get_participants(self):
        return self.participants


    def listen_env(self):

        def event_handler(_mq, get_shifted_time, routing_key, body):
            action = routing_key.rsplit('.', 1)[1]
            msg = body

            participant = self.get_participant(msg['participant'])

            if action == 'vote':
                participant.last_vote = msg['last_vote']

            self.fatima.update_knowledge_base(participant)


        self.mq_env.bind_queue(
            exchange=self.settings['messaging']['environment'], routing_key='action.*', callback=event_handler
        )

        print('[*] Waiting for messages. To exit press CTRL+C')
        self.mq.listen()

#    def update_fatima_knowledge_base(self):
 #       '''
 #       updates the fatima knowledge base for each player
  #      :return:
  #      '''
  #      for player in self.participants:
  #          self.fatima.update_knowledge_base(player.name)



    def start_game(self, game=None):
        self.game = game if game and isinstance(game, Game) else Game(Environment.SETTINGS_FILE)



 #   def _init_subscription(self):
  #      print(HOST,PORT)
   #     connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
#        channel = connection.channel()

#        channel.queue_declare(queue='processors')
#        channel.basic_consume(self.process_processors_data, queue='processors', no_ack=True)

#        channel.start_consuming()

    def process_processors_data(self, ch, method, properties, body):
        print(" [x] Received %r" % body)


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=PORT))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    connection.close()