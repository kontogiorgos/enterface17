import pyaudio
import pika
import sys
import time
import msgpack
sys.path.append('..')
from create_zmq_server import create_zmq_server
from GazeSense import GazeSenseSub
import time


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2205

zmq_socket, zmq_server_addr = create_zmq_server()


connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.100', port=32777))
channel = connection.channel()
channel.queue_declare(queue='kinect')

connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.100', port=32777))
channel2 = connection2.channel()

#channel.basic_publish(exchange='', routing_key='kinect', body="hiiiiiii")

def callback(ch, method, properties, body):
    #zmq_socket.send(msgpack.packb((in_data, time.time())))
    print "received " + str(body)
    #return None, pyaudio.paContinue

#     format=FORMAT,
#     channels=CHANNELS,
#     rate=RATE,
#     input=True,
#     frames_per_buffer=CHUNK,
#     stream_callback=callback
# )

channel2.basic_consume(callback,
                       queue='kinect',
                       no_ack=True)
# stream = pyaudio.PyAudio().open(

def my_callback(data):
    """
    Callback function example. Simply follow this signature, and you will receive a dictionary with the following items

    data['GazeCoding'] <- String with the current gazed target
    data['InTracking'] <- Boolean to indicate the subject is being tracked
    data['ConnectionOK'] <- Boolean to indicate there is a connection to the GazeSense application

    It will be called when:
    - A new data frame has been processed and gaze coding data is available
    - There is change in either the tracking status or the connection status
    """
    channel.basic_publish(exchange='', routing_key='kinect', body=str(data))
    connection.close()


gc = GazeSenseSub(callback=my_callback, verbose=True)

# Sleep, just to emulate your main thread process
try:
    time.sleep(3.0)
    gc.stop()

except KeyboardInterrupt:
    print("Stopping...")
finally:
    # clean up
    channel2.start_consuming()
    print "finished!"
    print "finished 2!"



# stream.stop_stream()
# stream.close()
# # audio.terminate()
# zmq_socket.close()
