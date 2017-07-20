from flask import Flask, render_template, request
import pika
import json
import sys
from flask_socketio import SocketIO, send, emit
sys.path.append('..')
from shared import create_zmq_server, MessageQueue


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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


@socketio.on('dialog_act')
def handle_dialog_act(json):
    print('received json: ' + str(json))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/visualizations")
def visualizations():
    return render_template('visualizations.html')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
    # app.run(host='0.0.0.0', debug=True)
