# Thorlabs delay stage control
# long delay stage on GHOST

from pylablib.devices import Thorlabs
# print(Thorlabs.list_kinesis_devices())
stage = Thorlabs.KinesisMotor("73869400", scale="DDS300", is_rack_system=True)

# set up the stage home
stage.home(force=False)
stage.wait_for_home()
if stage.is_homed():    
    print('Thorlabs delay initialised and homed')

# initialise to goodish position
# stage.move_to()

# move to new position and returns true if it worked
def moveTo(pos:float)->bool:
    newp = stage.get_position(scale=True) + pos
    if newp > 0.302 or newp < 0.001:
        print('Out of bounds')
        return False
    else:
        stage.move_to(newp, scale=True)
        stage.wait_move()
        return True

# returns in m
def getLocation()->float:
    return stage.get_position(scale=True)

# returns true if done
def isMoving()->bool:
    return stage.is_moving()

# returns true if at forward limit
def checkFw()->bool:
    stat = stage.get_status()
    if 'hw_fw_lim' in stat:
        print(' At forwards limit')
        return True
    else:
        return False
        
# returns true if at backward limit
def checkBkw()->bool:
    stat = stage.get_status()
    if 'hw_bk_lim' in stat:
        print(' At forwards limit')
        return True
    else:
        return False
    
# emergency stop motion
def stopMove()->None:
    stage.stop()
    
    
def closeThor()->None:
    stage.close()

#stage.close()






