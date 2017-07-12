# import fatima
from furhat import connect_to_iristk
# etc..


class ArtificialAgent(Participant):
    """docstring for ArtificialAgent."""

    FURHAT_IP = 'x.x.x.x'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}

    def __init__(self, environment):
        super(ArtificialAgent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events
        self.listen_to_wizard_events()


    def listen_to_wizard_events(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBITMQ_CONNECTION))
        channel = connection.channel()
        channel.exchange_declare(exchange='wizard', type='topic')
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='wizard', queue=queue_name, routing_key='action.*')

        # Callback for wizard events. map to furhat actions
        def callback(ch, method, properties, body):
            action = method.routing_key.rsplit('.', 1)[1]
            if action == 'say':
                self.say(body)
            if action == 'gaze_at':
                #self.environment.participant('A').angle_from_furhat
                pass

        channel.basic_consume(callback, queue=queue_name)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)
