from flask import Flask, render_template, request
import pika
import json
import sys
sys.path.append('..')
from shared import create_zmq_server, MessageQueue


app = Flask(__name__)
mq = MessageQueue('wizard')


@app.route('/say')
def say():
    mq.publish(
        exchange='wizard',
        routing_key='action.say',
        body={'text': request.args.get('text', '')},
        no_time=True
    )
    return 'OK'

@app.route('/dialog_act')
def accuse():
    action = request.args.get('action')
    print(action)
    if action:
        mq.publish(
            exchange='wizard',
            routing_key='action.{}'.format(request.args.get('action')),
            body={'participant': request.args.get('participant', '')},
            no_time=True
        )
        return 'OK'
    return 'NOT_OK'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

    from threading import Thread

    def run():
        print('I am running in my own thread!')

        fatima_listner_mq = MessageQueue('fatima_listener')

        def update_belief_interface(msg):
            participant = msg['participant']
            belief = msg['belief']
            print(participant,belief)
            #send_to_wizard(participant,belief)

        def display_suggested_action(msg):
            print(msg['action'])
            #send_to_wizard(msg['action'])

        def display_suggested_vote(msg):
            print(msg['participant'])
            #send_to_wizard(msg['participant'])

        def update_wizard(_mq, get_shifted_time, routing_key, body):

            action = routing_key
            msg = body

            if action == 'belief_update':
                update_belief_interface(msg)

            if action == 'suggest_action':
                display_suggested_action(msg)

            if action == 'suggest_vote':
                display_suggested_vote(msg)


        fatima_listner_mq.bind_queue(
            exchange='fatima_agent', routing_key='*', callback=update_wizard
        )

        print('[*] Waiting for messages. To exit press CTRL+C')
        fatima_listner_mq.listen()


    thread = Thread(target=run)
    thread.deamon = True
    thread.start()
    while True:
        pass
