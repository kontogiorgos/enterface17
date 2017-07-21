REM start mocap sensor
REM START CMD /K CALL "mocap.bat"

REM start mocap preprocessor
START CMD /K CALL "mocap_preprocessor.bat"

REM start python webcam sensors
CALL "run_webcams.bat"
