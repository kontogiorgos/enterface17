import time
import sys

import stomp

class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error "%s"' % message)
    def on_message(self, headers, message):
        print('received a message "%s"' % message)


class Messages(object):
    def __init__(self):
        self.conn = stomp.Connection([('127.0.0.1', 32771)])
        self.conn.set_listener('', MyListener())
        self.conn.start()
        self.conn.connect('admin', 'password', wait=True)

    def subscribe(self, topic):
        self.conn.subscribe(destination=topic, id=1, ack='auto')

    def send(self, message, topic):
        self.conn.send(body=message, destination=topic)

    def disconnect(self):
        self.conn.disconnect()
