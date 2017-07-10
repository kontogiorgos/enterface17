from .participant import Participant


class Environment(object):
    """docstring for Environment."""

    def __init__(self):
        self.participants = [Participant() for x in range(6)]


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
