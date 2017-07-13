# -*- coding: utf-8 -*-

import signal
from flask import Flask, render_template, request
import pika
import json
# from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)


@app.route('/say')
def say():
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}

    connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBITMQ_CONNECTION))
    channel = connection.channel()
    channel.basic_publish(exchange='wizard', routing_key='action.say', body=json.dumps({'text': request.args.get('text', '')}))
    return 'OK'

@app.route('/accuse')
def accuse():
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}

    connection = pika.BlockingConnection(pika.ConnectionParameters(**RABBITMQ_CONNECTION))
    channel = connection.channel()
    channel.basic_publish(exchange='wizard', routing_key='action.accuse', body=json.dumps({'participant': request.args.get('participant', '')}))
    return 'OK'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html')

# @socketio.on('my event')
# def handle_my_custom_event(json):
#     print('received json: ' + str(json))


def signal_handler(signal, frame):
    print('killing furhat...')
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # socketio.run(app, host='0.0.0.0', debug=True)
    app.run(host='0.0.0.0', debug=True)
