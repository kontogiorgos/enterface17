import msgpack
import cv2
import numpy as np


with open('./logger/2017-07-24T01_53_18_080557/video.new_sensor.brown-0/data.cv-video', 'rb') as f:
    unpacker = msgpack.Unpacker(f)
    for value, timestamp in unpacker:
        print(np.frombuffer(value, dtype='uint8').shape)
        cv2.imshow('data', np.frombuffer(value, dtype='uint8').reshape((720, 1280, 3)))
        cv2.waitKey(1)
