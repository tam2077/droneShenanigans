from multiprocessing import process
from djitellopy import tello
import ffmpeg
from threading import Thread
import time
chunkTime = 5


drone = tello.Tello()
drone.connect()
drone.streamon()

def recordVideo(chunkTime):
    stream = ffmpeg.input('udp://192.168.10.1:11111')
    #stream = ffmpeg.hflip(stream)
    stream = ffmpeg.output(stream, "output_%H%M%S.mp4", r=30, f='segment', segment_time=chunkTime,strftime='1',reset_timestamps = 1, codec = 'copy')
    args = stream.get_args()
    print(f'Args: {args}')
    ffmpeg.run(stream)

class record(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
    def run(self):
        while self.running:
            recordVideo(chunkTime)
    def stop(self):
        self.running = False
        

a = record()

a.start()
#drone.takeoff()
#drone.move_down(20)
# try:
#     while True:
#         drone.send_rc_control(0,25,0,0)
# except KeyboardInterrupt:
#     drone.send_rc_control(0,0,0,0)
#     drone.land()



process =(
    ffmpeg
    .input('udp://@:11111',)
    .output("output_%H%M%S.mp4", r=30, f='segment', segment_time=chunkTime,strftime='1',reset_timestamps = 1, codec = 'copy')    
)