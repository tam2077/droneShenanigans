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

tello = Tello()
tello.connect()
tello.takeoff()



# def receive_new_frame(data_dict):
#     order_list=[ "frameNumber", "markerSetCount", "unlabeledMarkersCount", "rigidBodyCount", "skeletonCount",
#                 "labeledMarkerCount", "timecode", "timecodeSub", "timestamp", "isRecording", "trackedModelsChanged" ]
#     dump_args = False
#     if dump_args == True:
#         out_string = "    "
#         for key in data_dict:
#             out_string += key + "="
#             if key in data_dict :
#                 out_string += data_dict[key] + " "
#             out_string+="/"
#         print(out_string)

x_err=[]
y_err=[]
z_err=[]

x_val=[]
y_val=[]
z_val=[]


KP_X = 1
KI_X = 1
KD_X = 1

KP_Y = 1
KI_Y = 1
KD_Y = 1

KP_Z = 1
KI_Z = 1
KD_Z = 1

error_x = 0
error_y = 0
error_z = 0
global prev_error_x
global prev_error_y
global prev_error_z

prev_error_x = 0
prev_error_y = 0
prev_error_z = 0

prev_value_x = 0
prev_value_y = 0
prev_value_z = 0

target_cord = [300,300,300]
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

def x_value():
        global prev_error_x
        error_x = target_cord[0]-current_cord[0]
        # if(error_x != prev_error_x):
        #     print("Error X",error_x)
        P = error_x
        I =+ error_x
        D = error_x - prev_error_x
        prev_error_x = error_x

        value = KP_X*P+KI_X*I+KD_X*D
        prev_value = value
        # print("value X",value)
        return error_x,value

def y_value():
        global prev_error_y
        error_y = target_cord[1]-current_cord[1]
        # if(error_y != prev_error_y):
        #     print("Error Y",error_y)
        P = error_y
        I =+ error_y
        D = error_y - prev_error_y
        prev_error_y = error_y

        value = KP_Y*P+KI_Y*I+KD_Y*D
        prev_value = value
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
        prev_error_z = error_z

        value = KP_Z*P+KI_Z*I+KD_Z*D
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
            if(px[0] and px[1] != 0):
                x_val.append(px[0])
                x_err.append(px[1])
            print("X Error ",px[0]," value ",px[1])
            py=y_value()
            if(py[0] and py[1] != 0):
                y_val.append(py[0])
                y_err.append(py[1])
            y_val.append(py[0])
            y_err.append(py[1])
            print("Y Error ",py[0]," value ",py[1])
            pz=z_value()
            if(pz[0] and pz[1] != 0):
                z_val.append(pz[0])
                z_err.append(pz[1])
            z_val.append(pz[0])
            z_err.append(pz[1])
            print("Z Error ",pz[0]," value ",pz[1])
            # print(x_val)
            # print(y_val)
            # print(z_val)

        # except KeyboardInterrupt:
        #         #plot X:
        #         plt.subplot(3, 1, 1)
        #         plt.plot(range(len(x_val)),x_val)

        #         #plot Y:
        #         plt.subplot(3, 1, 2)
        #         plt.plot(range(len(y_val)),y_val)

        #         #plot Z:
        #         plt.subplot(3, 1, 3)
        #         plt.plot(range(len(z_val)),z_val)
        #         tello.land()
        #         plt.show()
    def move_drone():
        #tello = Tello()
        tello.connect()

        tello.takeoff()

        yaw = 0
        while True:
            if x_err < 5 and x_err > -5:
                 lr_vel = x_err
            elif x_err > 5:
                 lr_vel = 5
            elif x_err < -5:
                 lr_vel = -5
            else:
                 lr_vel = 0

            if z_err < 5 and z_err > -5:
                 fb_vel = z_err
            elif z_err > 5:
                 fb_vel = 5
            elif z_err < -5:
                 fb_vel = -5
            else:
                 fb_vel = 0


            if y_err < 5 and y_err > -5:
                 ud_vel = y_err
            elif y_err > 5:
                 ud_vel = 5
            elif y_err < -5:
                 ud_vel = -5
            else:
                 ud_vel = 0

            fb_vel = z_err
            ud_vel = y_err
            tello.send_rc_control(lr_vel,fb_vel,ud_vel,yaw)

    process1 = Process(target = main_func)
    process2 = Process(target = move_drone)
    process1.start()
    process2.start()
