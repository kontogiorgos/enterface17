REM start kinect sensor
START CMD /K CALL python ../python/sensors/kinect/kinect.py pink

REM start kinect screenreader hack
START CMD /K CALL "../screenreader_hack.bat"

REM start kinect python video sensor script
START CMD /K CALL "start_screenrecording_video.bat"

REM start python webcam sensors
CALL "run_webcams.bat"
