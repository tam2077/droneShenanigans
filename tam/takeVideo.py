from djitellopy import Tello
import time
#Positive fb = Forward
#Positive LR = Right
#Positive UD = UP
tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()
try:
    while True:
        tello.send_rc_control(0,0,0,50)
except KeyboardInterrupt:
    tello.send_rc_control(0,0,0,0)
    tello.land()
