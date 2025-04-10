# Phydgets for GHOST

import time
import traceback
from Phidget22 import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.RCServo import *
 

def setpos(outcome,channels):
    """
    Sets positions of any number of motorized beam blocks simultaneously.
    Parameters
    outcome : int
        0 -> Beam is blocked
        1 -> Beam in unblocked
    channels : list of ints. '[0, 1, 2]' etc
        0 -> sampling
        1 -> test
        2 -> pump

    Returns
    None.
    """
    try:
        #Create your Phidget channels
        rcServos = []
        channelindex = []
        for n in channels:
            rcServos.append(RCServo())
            if n==0: 
                channelindex.append(0)
            if n==1: 
                channelindex.append(1)
            if n==3: 
                channelindex.append(2)
            if n==4: 
                channelindex.append(3)
            if n==6: 
                channelindex.append(4)
        
        #Set addressing parameters to specify which channel to open (if any)
        for n, servo in enumerate(rcServos):
            servo.setDeviceSerialNumber(594056)
            servo.setChannel(channels[n])
        #Open your Phidgets and wait for attachment
        for servo in rcServos:
            servo.openWaitForAttachment(5000)
        off_pos = [180, 95, 5, 100, 95]
        on_pos = [90, 180, 80, 20, 25]
        #Do stuff with your Phidgets here or in your event handlers.
        if outcome==0:
            angles = off_pos
        else:
            angles = on_pos
        for n, servo in enumerate(rcServos):
            servo.setTargetPosition(angles[channelindex[n]])
            servo.setEngaged(True)
        time.sleep(500e-3)
        
        #Close your Phidgets once the program is done.
        for servo in rcServos:
            servo.close()
        
    except PhidgetException as ex:
        #We will catch Phidget Exceptions here, and print the error informaiton.
        traceback.print_exc()
        print("")
        print("PhidgetException " + str(ex.code) + " (" + ex.description + "): " + ex.details)

print('Phidgets initialised')
setpos(0,[2])
