# -*- coding: utf-8 -*-

import signal
from flask import Flask, render_template, request
from furhat import connect_to_iristk
# from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)


FURHAT_HOST = '127.0.0.1'
FURHAT_AGENT = 'furhat6'


@app.route('/say')
def say():
    with connect_to_iristk(FURHAT_HOST) as furhat_client:
        furhat_client.say(FURHAT_AGENT, request.args.get('text', ''))
    return 'OK'


@app.route("/")
def index():
    return render_template('index.html')

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
