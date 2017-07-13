# import fatima
from furhat import connect_to_iristk
import pika
# from .. import Player
from threading import Thread
import json
# etc..


class Agent(object):
    """docstring for Agent."""

    FURHAT_IP = '192.168.0.111'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}

    def __init__(self, environment):
        super(Agent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events

        self.thread = Thread(target = self.listen_to_wizard_events)
        self.thread.deamon = True
        self.thread.start()


    def listen_to_wizard_events(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(**self.RABBITMQ_CONNECTION))
        channel = connection.channel()
        channel.exchange_declare(exchange='wizard', type='topic')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='wizard', queue=queue_name, routing_key='action.*')

        # Callback for wizard events. map to furhat actions
        def callback(ch, method, properties, body):
            action = method.routing_key.rsplit('.', 1)[1]
            msg = json.loads(body)
            if action == 'say':
                self.say(msg['text'])
            if action == 'accuse':
                self.say('I accuse you')
                location = self.environment.get_participants(msg['participant']).get_furhat_angle()
                self.gaze_at({'x': 2, 'y': 0, 'z': 2})


        channel.basic_consume(callback, queue=queue_name)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)

a = Agent(None)
