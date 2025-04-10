# Choppper control for MC2000 (only) using serial
# com7 com6 com4
# 121016-05
# 100427-05 
# 091202-09
import time
import serial

old_blades =  ['MC1F2', 'MC1F10', 'MC1F15', 'MC1F30', 'MC1F60', 'MC1F100', 'MC1F57']
blades =  ['MC1F2', 'MC1F6', 'MC1F10', 'MC1F15', 'MC1F30', 'MC1F60', 'MC1F100', 'MC1F57']
escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)

def readNwrite(box:serial.serialwin32.Serial, input:str)->str:
    enter=input+'\r'
    box.write(enter.encode())
    time.sleep(1)
    out = ''
    while box.in_waiting>0:
        out += box.read().decode()
    # print((out.translate(translator)))
    return (out.translate(translator))[len(input):-2]

def hasWorked(out:str)->bool:
    if out[:13] == 'Command error':
        print(out)
        return False
    else:
        return True 

def isConnected(box)->None:
    enter='\r'
    box.write(enter.encode())
    time.sleep(1)
    out = ''
    while box.in_waiting>0:
        out += box.read().decode()
    print(out.translate(translator))
   
def getID(box)->str:
    id = readNwrite(box, 'id?')
    # print(id)
    return id
    
def getBlade(box)->str:
    b = readNwrite(box, 'blade?')
    if box == test:
        return blades[int(b)]
    elif box == pump:
        return old_blades[int(b)]

def getRef(box)->bool:  #reference mode 0== internal, 1== external
    ref = readNwrite(box, 'ref?')
    # print(ref)  
    if int(ref) == 0:
        return False
    if int(ref) == 1:
        return True
    else:
        return False
    
def getFreq(box)->str: #internal freq
    f = readNwrite(box, 'freq?')
    # print(f)
    return f
    
def getInput(box)->str: #external freq
    f = readNwrite(box, 'input?')
    # print(f)
    return f
    
def getOut(box)->None:  #output mode 0== ref, 1== actual
    print(readNwrite(box, 'output?'))      
    
def getPhase(box)->str:
    ph = readNwrite(box, 'phase?')
    # print(ph)
    return ph
    
def getNharm(box)->str:
    nh = readNwrite(box, 'nharmonic?')
    # print(nh)
    return nh
    
def getDharm(box)->str:
    dh = readNwrite(box, 'dharmonic?')
    # print(dh)
    return dh
    
def getEnable(box)->bool:   # 0== disabled, 1== enabled
    en = readNwrite(box, 'enable?')
    # print(en)
    if int(en) == 0:
        return False
    if int(en) == 1:
        return True
    else:
        return False
    
def setBlade(box, input:str)->None:
    dict = {'MC1F2':0, 'MC1F6':1, 'MC1F10':2, 'MC1F15':3, 'MC1F30':4, 'MC1F60':5, 'MC1F100':6, 'MC1F57':7}
    try:
        bl = dict[input]
        comm = 'blade='+str(bl)
        print(readNwrite(box, comm))
    except:
        print('Not a valid blade')    
        print('Valid blades are: MC1F2, MC1F6, MC1F10, MC1F15, MC1F30, MC1F60, MC1F100, MC1F57')

def setFreq(box, input:str)->None:
    comm = 'freq='+str(input)
    print(readNwrite(box, comm))      

def setInput(box, input:str)->None:
    comm = 'input='+str(input)
    print(readNwrite(box, comm))     

def setOut(box, input:str)->None:
    comm = 'blade='+str(input)
    print(readNwrite(box, comm))      

def setPhase(box, input:str)->bool:
    comm = 'phase='+str(input)
    return hasWorked(readNwrite(box, comm))      

def setNharm(box, input:str)->bool:
    comm = 'nharmonic='+str(input)
    return hasWorked(readNwrite(box, comm))  

def setDharm(box, input:str)->bool:
    comm = 'dharmonic='+str(input)
    return hasWorked(readNwrite(box, comm))    

def setEnable(box, input:str)->bool:
    comm = 'enable='+str(input)
    return hasWorked(readNwrite(box, comm))

def closeSerial()->None:
    pump.close()
    test.close()
    
    
pump = serial.Serial(port='COM4', baudrate=115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE)
test = serial.Serial(port='COM7', baudrate=115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE)
isConnected(test)
isConnected(pump)

if test.isOpen():
    print('Test chopper initialised')

if pump.isOpen():
    print('Pump chopper initialised')




    