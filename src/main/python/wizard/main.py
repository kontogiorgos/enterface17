# -*- coding: utf-8 -*-

import signal
from flask import Flask, render_template, request
import pika
import json
sys.path.append('..')
from shared import create_zmq_server, MessageQueue


app = Flask(__name__)
mq = MessageQueue()


@app.route('/say')
def say():
    mq.publish(
        exchange='wizard',
        routing_key='action.say',
        body=json.dumps({'text': request.args.get('text', '')})
    )
    return 'OK'

@app.route('/dialog_act')
def accuse():
    action = request.args.get('action')
    if action:
        mq.publish(
            exchange='wizard',
            routing_key='action.{}'.format(request.args.get('action')),
            body=json.dumps({'participant': request.args.get('participant', '')})
        )
        return 'OK'
    return 'NOT_OK'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html')


def signal_handler(signal, frame):
    print('killing furhat...')
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
