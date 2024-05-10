import sys
import time
from NatNetClient import NatNetClient
import DataDescriptions
import MoCapData
from multiprocessing import Process
import matplotlib.pyplot as plt
import numpy as np
import math as m
from djitellopy import Tello

from multiprocessing import Process

#global lr_vel,fb_vel,ud_vel
lr_vel,fb_vel,ud_vel = 0,0,0

#tello = Tello()
#tello.connect()
#tello.takeoff()
#tello.move_down(20)




x_err=[]
y_err=[]
z_err=[]

x_val=[]
y_val=[]
z_val=[]

global KP_X,KP_Y,KP_Z,KI_X,KI_Y,KI_Z,KD_X,KD_Y,KD_Z
KP_X = 0.4
KI_X = 0.4
KD_X = 0.4

KP_Y = 0.4
KI_Y = 0.4
KD_Y = 0.4

KP_Z = 0.4
KI_Z = 0.4
KD_Z = 0.4

global prev_error_x,error_x
global prev_error_y,error_y
global prev_error_z,error_z

error_x = 0
error_y = 0
error_z = 0


prev_error_x = 0
prev_error_y = 0
prev_error_z = 0

prev_value_x = 0
prev_value_y = 0
prev_value_z = 0

target_cord = [200, 750, -800]
global current_cord
current_cord = [0,0,0]

def receive_rigid_body_frame( new_id, position, rotation ):
    #print( "Received frame for rigid body", new_id )
    r = rotation
    print( "Received frame for rigid body", new_id," ",position )
    

def add_lists(totals, totals_tmp):
    totals[0]+=totals_tmp[0]
    totals[1]+=totals_tmp[1]
    totals[2]+=totals_tmp[2]
    return totals

def print_configuration(natnet_client):
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
    s_client.send_request(s_client.command_socket, s_client.NAT_REQUEST_MODELDEF,    "",  (s_client.server_ip_address, s_client.command_port) )

def test_classes():
    totals = [0,0,0]
    print("Test Data Description Classes")
    totals_tmp = DataDescriptions.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("Test MoCap Frame Classes")
    totals_tmp = MoCapData.test_all()
    totals=add_lists(totals, totals_tmp)
    print("")
    print("All Tests totals")
    print("--------------------")
    print("[PASS] Count = %3.1d"%totals[0])
    print("[FAIL] Count = %3.1d"%totals[1])
    print("[SKIP] Count = %3.1d"%totals[2])

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
    rotation = rotation
    id = id
    current_cord[0] = position[0]
    current_cord[1] = position[1]
    current_cord[2] = position[2]
    #print(current_cord[0])


def x_value():
        global prev_error_x
        error_x = target_cord[0]-current_cord[0]
        value = KP_X * error_x + KD_X * (error_x - prev_error_x)
        prev_error_x = error_x
        print("value X",value)
        return error_x,value

def y_value():
        global prev_error_y
        error_y = target_cord[1]-current_cord[1]
        # if(error_y != prev_error_y):
        #     print("Error Y",error_y)
        P = error_y
        I =+ error_y
        D = error_y - prev_error_y

        #value = KP_Y*P+KI_Y*I+KD_Y*D
        value = KP_Y * error_y + KD_Y * (error_y - prev_error_y)
        prev_error_y = error_y
        # print("value Y",value)
        return error_y,value


def z_value():
        global prev_error_z
        error_z = target_cord[2]-current_cord[2]
        # if(error_z != prev_error_z):
        #     print("Error Z",error_z)
        P = error_z
        I =+ error_z
        D = error_z - prev_error_z

        #value = KP_Z*P+KI_Z*I+KD_Z*D
        value = KP_Z * error_z + KD_Z * (error_z - prev_error_z)
        prev_error_z = error_z
        prev_value = value
        # print("value Z",value)
        return error_z,value

    

if __name__ == "__main__":
    def main_func():

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

        print_configuration(streaming_client)
        print("\n")

        # px = Process(target=x_value)
        # py = Process(target=y_value)
        # pz = Process(target=z_value)

        # p.start()
        # #y.start()
        # #z.start()
        while True:
            px=x_value()
            py=y_value()
            pz=z_value()
            yaw = 0

            lr_vel = px[1]
            #lr_vel = int(np.clip(lr_vel, -5, 5))
            #print("lr: " + str(lr_vel))

            fb_vel = pz[1]
            #fb_vel = int(np.clip(fb_vel, -5, 5))
            #print("fb:" + str(fb_vel))

            ud_vel = py[1]
            #ud_vel = int(np.clip(ud_vel, -5, 5))
            #print("ud: " + str(ud_vel))

            #tello.send_rc_control(lr_vel,fb_vel,ud_vel,yaw)
    main_func()

#x = 200
#y = 700
#z = -850