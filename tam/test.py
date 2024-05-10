from djitellopy import Tello
import time
tello = Tello()

tello.connect()
tello.takeoff()

try:
    while True:
        tello.send_rc_control(10,0,0,0)

except KeyboardInterrupt:
    tello.send_rc_control(0,0,0,0)
    tello.land()
    