import sys
import time
from NatNetClient import NatNetClient
import matplotlib.pyplot as plt
import numpy as np
from djitellopy import Tello
import math
import ffmpeg
from threading import Thread
import time

chunkTime = 10
# +X is Forward 
# +Y is Vertical
# +Z is Right
# +Rot is clockwise

x_val=[]
y_val=[]
z_val=[]
clip_v = 25
clip = [-1*clip_v,clip_v]

speed_x = 0
speed_y = 0
speed_z = 0
speed_t = 0


KP_X = 0.2
KP_Y = 0.2
KP_Z = 0.2
KP_T = 10

KI_X = 0.4
KI_Y = 0.4
KI_Z = 0.4
KI_T = 0

KD_X = 0
KD_Y = 0
KD_Z = 0
KD_T = 0


error_x = 0
error_y = 0
error_z = 0
error_t = 0

prev_error_x = 0
prev_error_y = 0
prev_error_z = 0
prev_error_t = 0

prev_value_x = 0
prev_value_y = 0
prev_value_z = 0
prev_value_t = 0
#T is theta 

#Target Cords for now
# -709mm, 703mm, 35mm
# 
target_cord = [-975,350,-535]

##Checkpoints
target_cord_1 =[563,350,-535]
target_cord_2 =[563,350,168]
target_cord_3 =[-805,350,168]


target_cord_4 =[0,0,0]
target_cord_5 =[0,0,0]


target_t = 0
current_cord = [0,0,0]
current_t = 0


    
def recordVideo(chunkTime):
    stream = ffmpeg.input('udp://@:11111',)
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

def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals



def request_data_descriptions(s_client):
    # Request the model definitions
    #s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,    "",  (s_client.server_ip_address, s_client.command_port) )
     pass

def test_classes():
    pass

def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len=len(arg_list)
    if arg_list_len>1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len>2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len>3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False

    return args_dict

def get_xyz(id,position,rotation):
    global current_t,current_cord
    #rotation = rotation
    id = id
    # values are received in meters, convert to mm
    current_cord[0] = position[0]*1000
    current_cord[1] = position[1]*1000
    current_cord[2] = position[2]*1000
    yaw = euler_from_quaternion(rotation[0],rotation[1],rotation[2],rotation[3])
    #print(math.degrees(yaw[1]))
    current_t = math.degrees(yaw[1])
    
    

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians
 


def within_range(percent, prev_tar_cord, cur_tar_cord):
    global target_cord,current_cord

    if (
        (prev_tar_cord[0] - prev_tar_cord[0] * (percent / 100)) <= current_cord[0] <= (prev_tar_cord[0] + prev_tar_cord[0] * (percent / 100)) and
        (prev_tar_cord[1] - prev_tar_cord[1] * (percent / 100)) <= current_cord[1] <= (prev_tar_cord[1] + prev_tar_cord[1] * (percent / 100)) and
        (prev_tar_cord[2] - prev_tar_cord[2] * (percent / 100)) <= current_cord[2] <= (prev_tar_cord[2] + prev_tar_cord[2] * (percent / 100))
    ):
        target_cord = cur_tar_cord

     
     
     
     
def x_value():
        global prev_error_x,KP_X,KI_X,KD_X,speed_x
        error_x = target_cord[0]-current_cord[0]
        
        speed_x = (KP_X*error_x)+(KI_X*(error_x-prev_error_x))
        prev_error_x = error_x
        speed_x = int(np.clip(speed_x,clip[0],clip[1]))
        return speed_x

def y_value():
        global prev_error_y,KP_Y,KI_Y,KD_Y,speed_y
        error_y = target_cord[1]-current_cord[1]

        speed_y = (KP_Y*error_y)+(KI_Y*(error_y-prev_error_y))
        prev_error_y = error_y
        speed_y = int(np.clip(speed_y,clip[0],clip[1]))
        return speed_y

def z_value():
        global prev_error_z,KP_Z,KI_Z,KD_Z,speed_z
        error_z = target_cord[2]-current_cord[2]

        speed_z = (KP_Z*error_z)+(KI_Z*(error_z-prev_error_z))
        prev_error_z = error_z
        speed_z = int(np.clip(speed_z,clip[0],clip[1]))
        return speed_z

def t_value():
        global prev_error_t,KP_T,KI_T,KD_T,speed_t
        error_t = target_t-current_t

        speed_t = (KP_T*error_t)+(KI_T*(error_t-prev_error_t))
        prev_error_t = error_t
        #speed_t = int(np.clip(speed_t,clip[0],clip[1]))
        speed_t = int(np.clip(speed_t,-100,100))
        return speed_t*-1


tello = Tello()
tello.connect()
tello.takeoff()
tello.streamon()

if __name__ == "__main__":

    optionsDict = {}
    optionsDict["clientAddress"] = "192.168.0.141"
    optionsDict["serverAddress"] = "192.168.0.214"
    optionsDict["use_multicast"] = False

    # This will create a new NatNet client
    optionsDict = my_parse_args(sys.argv, optionsDict)

    streaming_client = NatNetClient()
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # Configure the streaming client to call our rigid body handler on the emulator to send data out.
    #streaming_client.new_frame_listener = receive_new_frame
    
    #streaming_client.rigid_body_listener = receive_rigid_body_frame
    streaming_client.rigid_body_listener = get_xyz

    # Start up the streaming client now that the callbacks are set up.
    # This will run perpetually, and operate on a separate thread.
    is_running = streaming_client.run()
    if not is_running:
        print("ERROR: Could not start streaming client.")
        try:
            sys.exit(1)
        except SystemExit:
            print("...")
        finally:
            print("exiting")

    is_looping = True
    time.sleep(1)
    if streaming_client.connected() is False:
        print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
        try:
            sys.exit(2)
        except SystemExit:
            print("...")
        finally:
            print("exiting")
    print("\n")

    try:
        a.start()
        tello.move_down(20)
        while True:
            within_range(25,target_cord,target_cord_1)
            px = x_value()
            py = y_value()
            pz = z_value()
            pt = t_value()

            tello.send_rc_control(pz,px,py,pt)
            
    except KeyboardInterrupt:
        a.stop()
        tello.send_rc_control(0,0,0,0)
        tello.land()
#Target 
# Cords for now
# -709mm, 703mm, 35mm