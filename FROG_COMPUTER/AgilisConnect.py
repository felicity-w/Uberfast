# Connect to Agilis UC2-UC8
import os
import clr
import sys
import inspect
import numpy as np
Path = r' C:\Program Files (x86)\Newport\Piezo Motion Control\AG-UC2-UC8\Samples'
sys.path.append (Path)
clr.AddReference ("CmdLibAgilis")
clr.AddReference ("VCPIOLib")
from Newport.Motion.CmdLibAgilis import *
from Newport.VCPIOLib import *
#from System.Text import StringBuilder

DIO = VCPIOLib (True)
CL = CmdLibAgilis (DIO)
DIO.DiscoverDevices ()

CL.SetRemoteMode()

print('FROG Delay Stage Initialising')
CL.Open('COM5')
CL.SetChannel(1)
axis = 1
CL.ResetStepCounter(axis)
axis_status = 0
P_amp = 19
N_amp = 24
CL.SetStepAmplitudePositive(axis,P_amp)
CL.SetStepAmplitudeNegative(axis,N_amp)

def SetHome()->bool:
   return CL.ResetStepCounter(axis)

def GoHome()->bool:
    wk, steps = CL.GetStepsAccumulated(axis, 1)
    inv_steps = -steps
    # CL.RelativeMove(axis, inv_steps)
    # return CL.ResetStepCounter(axis)
    if inv_steps > 0 :
        for i in range(0, inv_steps):
            CL.RelativeMove(axis, 1)
    if inv_steps < 0:
        for i in range(0, steps):
            CL.RelativeMove(axis, -1)
    return CL.ResetStepCounter(axis)

def GetStepSizes()->(int,int):
    wk1, p = CL.GetStepAmplitudePositive(axis,1)
    wk2, n = CL.GetStepAmplitudeNegative(axis,1)
    return (p, n)

def SetStepSizes(pStep:int, nStep:int)->(int,int):
    wk1, p = CL.SetStepAmplitudePositive(axis,pStep)
    wk2, n = CL.SetStepAmplitudeNegative(axis,nStep)
    return (p, n)

def SetBackStep(amp:int)->bool:
    wk2 = CL.SetStepAmplitudeNegative(axis,amp)
    return wk2
        
def SetFrontStep(amp:int)->bool:
    wk2 = CL.SetStepAmplitudePositive(axis,amp)
    return wk2

def GetBackStep()->int:
    wk2, n = CL.GetStepAmplitudeNegative(axis,1)
    return n
        
def GetFrontStep()->int:
    wk2, p = CL.GetStepAmplitudePositive(axis,1)
    return p
        
def Move(no_steps:int)->bool:
    return CL.RelativeMove(axis, no_steps)

def MoveForwards(no_steps:int)->bool:
    return CL.RelativeMove(axis, no_steps)

def MoveBackwards(no_steps:int)->bool:
    return CL.RelativeMove(axis, -no_steps)
    
def MotionDone()->bool:
    works = False
    moving = 4 # random int greater than 3
    works, moving = CL.GetAxisStatus(axis,1)
    if moving==0 :
        return True
    else:
        return False
    
def JogForwards()->bool:
    return CL.StartJogging(axis, 4)

def JogBackwards()->bool:
    return CL.StartJogging(axis, -4)

    
# the_key =' '
# CL.GetDeviceCount()
# Device_Keys = np.ndarray ([])
# Device_Keys = DIO.GetDeviceKeys ()
# if (not Device_Keys) :
#     print ("No devices discovered")
# else :
#     for DeviceKey in Device_Keys :
#         Key = str (DeviceKey)
#         # print ("Key = %s" % DeviceKey)
#         if (CL.Open(Key) == 0) :
#             bStatus = False
#             Version = ""
#             bStatus, Version = CL.GetFirmwareVersion (Version)
#             if (bStatus) :
#                 # print("Device ID = %s" % Version)
#                 name = 'UC8'
#                 if name in Version:
#                     print("Device ID = %s" % Version)
#                     print ("Key = %s \n" % Key)
#                     the_key = Key
#         CL.Close ()
