REM start webcam blue
START CMD /K CALL "ffmpeg_video-blue.bat"

REM start python webcam sensor blue
START CMD /K CALL "run_video-blue.bat"

REM start webcam brown
START CMD /K CALL "ffmpeg_video-brown.bat"

REM start python webcam sensor brown
START CMD /K CALL "run_video-brown.bat"

REM start webcam white
START CMD /K CALL "ffmpeg_video-white.bat"

REM start python webcam sensor white
START CMD /K CALL "run_video-white.bat"
