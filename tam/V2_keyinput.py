import sys
import time
from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData
import matplotlib.pyplot as plt
import numpy as np
from djitellopy import Tello
import math
import keyboard
import logging

clip_v = 25
clip = [-1*clip_v,clip_v]

speed_x = 0
speed_y = 0
speed_z = 0
speed_t = 0
##0.4, 0.7, 1.0, 1.0	# lr, fb, ud, yaw
KP_X = 0.2
KP_Y = 0.2
KP_Z = 0.2
KP_T = 10

KI_X = 0.1
KI_Y = 0.1
KI_Z = 0.1
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


target_cord = [-975,350,-535]

##Checkpoints
target_cord_1 =[563,350,-535]
target_cord_2 =[563,350,168]
target_cord_3 =[-805,350,168]

target_t = 0
current_cord = [0,0,0]
current_t = 0

shot_pressed_qa = 0
shot_pressed_ed = 0
was_pressed = False

    

def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals

#def print_configuration(natnet_client):
    natnet_client.refresh_configuration()
    print("Connection Configuration:")
    print("  Client:          %s"% natnet_client.local_ip_address)
    print("  Server:          %s"% natnet_client.server_ip_address)
    print("  Command Port:    %d"% natnet_client.command_port)
    print("  Data Port:       %d"% natnet_client.data_port)

    #NatNet Server Info
    application_name = natnet_client.get_application_name()
    nat_net_requested_version = natnet_client.get_nat_net_requested_version()
    nat_net_version_server = natnet_client.get_nat_net_version_server()
    server_version = natnet_client.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" %(application_name))
    print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
       nat_net_requested_version[2], nat_net_requested_version[3]))
    #print("command_socket = %s"%(str(natnet_client.command_socket)))
    #print("data_socket    = %s"%(str(natnet_client.data_socket)))




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
tello.LOGGER.setLevel(logging.WARNING)
tello.connect()
tello.takeoff()


if __name__ == "__main__":

    optionsDict = {}
    optionsDict["clientAddress"] = "127.0.0.1"
    optionsDict["serverAddress"] = "127.0.0.1"
    optionsDict["use_multicast"] = True

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

    #print_configuration(streaming_client)
    print("\n")

    try:
        tello.move_down(20)
        while True:
            px = x_value()
            py = y_value()
            pz = z_value()
            pt = t_value()

            tello.send_rc_control(pz,px,py,pt)

            ## Proportional gain for X (q and a)
            if keyboard.is_pressed('q'):
                if not was_pressed:
                    KP_X += 0.01
                    was_pressed = True
            elif keyboard.is_pressed('a'):
                if not was_pressed:
                    KP_X -= 0.01
                    was_pressed = True

            ## Integral gain for X (w and s)
            elif keyboard.is_pressed('w'):
                if not was_pressed:
                    KI_X += 0.01
                    was_pressed = True
            elif keyboard.is_pressed('s'):
                if not was_pressed:
                    KI_X -= 0.01
                    was_pressed = True
            #######@@@@@@@@@@@@###########
            else:
                was_pressed = False
                #print("KP_X "+str(KP_X)+" KP_Y "+str(KP_Y)+" KP_Z "+str(KP_Z)+"      KI_X "+str(KI_X)+" KI_Y "+str(KI_Y)+" KI_Z "+str(KI_Z))

            #print("X VALUE "+str(px)+" Y VALUE "+str(py)+" Z VALUE "+str(pz)+" T VALUE "+str(pt)+ " Actual Angle "+str(current_t))

    except KeyboardInterrupt:
        tello.send_rc_control(0,0,0,0)
        tello.land()

# +X is Forward 
# +Y is Vertical
# +Z is Right
# +Rot is clockwise

#Target 
# Cords for now
# -709mm, 703mm, 35mm