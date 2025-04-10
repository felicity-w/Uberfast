# Attroller - Attocube conttroller
# uses ACS and AMC from attocube github

import AMC
import time

# IP = '172.24.59.6
ipadress='192.168.1.1'
dev = AMC.Device(ipadress)
dev.connect()

def getClosedLoop(axis:int)->bool:  # false open loop, true closed loop
    return dev.control.getControlMove(axis)

def setClosedLoop(axis:int)->None:  # turn into a closed loop system
    print('turn into closed loop system')
    
def olStatus(axis:int)->int:    #0==NUM, 1==open loop positioner, 2== nopositioner, 3=RES, 4==IDS-CL
    return dev.status.getOlStatus(axis)
    
def getFreq(axis:int)->int:
    return dev.control.getControlFrequency(axis)

def isReferenced(axis:int)->bool:   # find out if we are referenced
    return dev.status.getStatusReference(axis)

def findReference(axis:int)->bool:
    if dev.status.getStatusReference(axis):
        print('Stage referenced')
        return True
    else:
        dev.control.setControlFrequency(1, 1999000)
        dev.control.searchReferencePosition(axis)
        while not isReferenced(axis):
            print(getLocation(axis))
            pass
    print('Stage referenced')
    return True
    
def goToRef(axis:int)->None:    # only if there is valid reference found
    dev.move.moveReference(axis)
    
def getRefPos(axis:int)->int:   # in nm  only if there is valid reference found
    return dev.control.getReferencePosition(axis)

    
def isMoving(axis:int)->bool:    #is the stage moving, 0==idle, 1==moving, 2==driving
    if dev.status.getStatusMoving(axis) == 0:
        return False
    else:
        return True

def isRanged(axis:int)->bool:   # is the stage in range of target, true==yes, false==not
    return dev.status.getStatusTargetRange(axis)

def getTargetRange(axis:int)->int:  # in nm
    return dev.control.getControlTargetRange(axis)

def setTargetRange(axis:int, target:int)->int:  # target range in nm
    return dev.control.setControlTargetRange(axis, target)
    
def startMove(axis:int)->None:
    dev.control.setControlMove(axis, True)
    
def stopMove(axis:int)->None:
    dev.control.setControlMove(axis, False)
    
def setBackSteps(axis:int, N:int)->None:    # sets how many steps backwards
    dev.move.setNSteps(axis, False, N) 

def setForwardSteps(axis:int, N:int)->None:    # sets how many steps forwards
    dev.move.setNSteps(axis, True, N) 
    
def stepAmplitude(axis:int, A:int)->None:   # 45000 = 1500nm , # 20000 = 100nm,300nm, # 4500 = 1nm #
    dev.control.setControlAmplitude(axis, A)
    
def stepForward(axis:int)->None:
    dev.move.setNSteps(axis, False, 1)
    
def stepBackward(axis:int)->None:
    dev.move.setNSteps(axis, True, 1)
    
def isMovingBack(axis:int)->bool:   #true==moving, False==Stopped
    return dev.move.getControlContinuousBkwd(axis)

def isMovingFwd(axis:int)->bool:   #true==moving, False==Stopped
    return dev.move.getControlContinuousFwd(axis)

def contBkwd(axis:int)->None:
    dev.move.setControlContinuousBkwd(axis, True)
    
def contFwd(axis:int)->None:
    dev.move.setControlContinuousFwd(axis, True)

def getTarget(axis:int)->int:
    return dev.move.getControlTargetPosition(1)

def setTarget(axis:int, target:int)->None:
     if target<9e6 and target>-9e6:
         dev.move.setControlTargetPosition(axis, target)   
     else:
        print('Out of bounds [9e6,-9e6]')

def getLocation(axis:int)->int:
    return dev.move.getPosition(axis)

def checkFwd(axis:int)->bool:
     stat = dev.status.getFullCombinedStatus(axis)
     if 'forward limit reached' in stat:
         print(' At forwards limit')
         return True
     else:
         return False

def checkBkwd(axis:int)->bool:
     stat = dev.status.getFullCombinedStatus(axis)
     if 'backward limit reached' in stat:
         print(' At backwards limit')
         return True
     else:
         return False

# pump delay stage
if dev.status.getStatusConnected(0):
    dev.control.setActorParametersByName(0, 'ECSx3030')
    dev.control.setControlAmplitude(0, 45000) # set amplitude
    dev.control.setControlFrequency(0, 1000000) # set Frequency
    dev.control.setControlOutput(0, True)
    print('Pump stage initialised')
# sampling delay stage
if dev.status.getStatusConnected(1):
    dev.control.setActorParametersByName(1, 'ECSx3030') 
    dev.control.setControlAmplitude(1, 45000) # set amplitude mV for the actuator signal (max 49V) #20000 = 100mu.m,, # 4500 = 1mu.m #
    dev.control.setControlFrequency(1, 99000) # set Frequency mHz for the actuator (mm steps sizes)
    # dev.control.setControlFixOutputVoltage(1, 35000) #sets DC level voltage in mV
    dev.control.setControlOutput(1, True)
    print('Sampling stage initialised')
    
# def getPushLocation()->int:  #in nm?
#     return dev.move.getPosition(0)

# def getSamplingLocation()->int:  #in nm?
#     return dev.move.getPosition(1)

# def movePush(x)->None:
#     if x<5e6 and x >-5e6:
#         dev.move.setControlTargetPosition(0, x)
#     else:
#         print('Out of bounds')
    
# def moveSampling(y)->None:
#     if y<5e6 and y>-5e6:
#         dev.move.setControlTargetPosition(1, y)
#     else:
#         print('Out of bounds')

# dev.control.setControlTargetRange(0, 10)# Activates TargetRange Status to true if position is within 100nm to the target position
# print('range 0 set')
# #dev.move.setControlTargetPosition(0, 0) # set Target Position to 1µm
# dev.control.setControlTargetRange(1, 10) # Activates TargetRange Status to true if position is within 100nm to the target position
# print('range 1 set')
# #dev.move.setControlTargetPosition(1, 0) # set Target Position to 1µm
# dev.control.setControlMove(0, True)
# dev.control.setControlMove(1, True)
# dev.move.setControlEotOutputDeactive(0, False) 
# dev.move.setControlEotOutputDeactive(1, False)
    
# Close connection
# dev.close()