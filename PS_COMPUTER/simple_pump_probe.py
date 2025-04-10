#tes pump-probe

# IMPORT modules
runfile('C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib/SiSoPyInterface.py', wdir='C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib')

import SiSoPyInterface as s
import sys
import time
import numpy as np
import matplotlib.pyplot as plt

#Initialise the framegrabber

boardId = 0
applet = 'DualLineGray16'
camPort = s.PORT_A

fg = s.Fg_InitEx(applet, boardId, 0);

s.Fg_loadConfig(fg,"C:/Users/kreel_admin/Desktop/SpecPy/pump_test.mcf")
exposure = 1
s.Fg_setParameterWithFloat(fg, s.FG_EXPOSURE, exposure, camPort)


#Define the aquisition parameters
width =2048
height = 8
samplePerPixel = 1
bytePerSample = 1
nbBuffers = 10000
totalBufferSize = width * height * samplePerPixel * bytePerSample * nbBuffers
nrOfPicturesToGrab = 10000

#Handle memory allocation

memHandle = s.Fg_AllocMemEx(fg, totalBufferSize, nbBuffers)

# start acquisition
err = s.Fg_AcquireEx(fg, camPort, nrOfPicturesToGrab, s.ACQ_STANDARD, memHandle)
    
cur_pic_nr = 0
last_pic_nr = 0
img = "will point to last grabbed image"
nImg = "will point to Numpy image/matrix"


fig = plt.figure(figsize = (15,8))
ax = fig.add_subplot(111)
line1, = ax.plot(np.zeros(1024), 'r-') # Returns a tuple of line objects, thus the comma
ax.set_ylim(-1e-2,1e-2)

rep_rate = 5000
display_rep_rate = 35

spec_on = np.zeros((int(rep_rate/display_rep_rate),1024))
spec_off = np.zeros((int(rep_rate/display_rep_rate),1024))
i =0

while cur_pic_nr < nrOfPicturesToGrab:
    cur_pic_nr = s.Fg_getLastPicNumberBlockingEx(fg, last_pic_nr + 1, camPort, 5, memHandle)
    last_pic_nr = cur_pic_nr
    img = s.Fg_getImagePtrEx(fg, last_pic_nr, camPort, memHandle)
    nImg = s.getArrayFrom(img, width, height)
    spec_on[i,:] = np.sum(nImg[:2,1::2]*2**8 + nImg[:2,0::2],axis =0)
    spec_off[i,:] = np.sum(nImg[2:,1::2]*2**8 + nImg[2:,0::2],axis =0)
    i+=1
    if i >= int(rep_rate/display_rep_rate):
        line1.set_ydata(np.sum(spec_on,axis =0)/np.sum(spec_off,axis =0) -1)
        fig.canvas.draw()
        fig.canvas.flush_events()
        i=0
    
        
print("Acquisition stopped")

# Clean up
if (fg != None):
	s.Fg_stopAcquire(fg, camPort)
	s.Fg_FreeMemEx(fg, memHandle)
	s.Fg_FreeGrabber(fg)

print("Exited.")
    

