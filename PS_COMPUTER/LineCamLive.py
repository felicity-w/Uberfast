# Line Camera for GHOST set up
runfile('C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib/SiSoPyInterface.py',
        wdir='C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib')
# import SiSoPyInterface as SSI

import sys
import time
import numpy as np
import pyqtgraph as pg
import SiSoPyInterface as SSI
from pyqtgraph.Qt import QtCore, QtGui

#Initialise the framegrabber
boardId = 0
applet = 'DualLineGray16'
camPort = SSI.PORT_A
fg = SSI.Fg_InitEx(applet, boardId, 0);
# SSI.Fg_loadConfig(fg,"C:/Users/oe-fatality64-user/Desktop/GHOST/no_laser_conf.mcf")
# SSI.Fg_loadConfig(fg,"C:/Users/oe-fatality64-user/Desktop/GHOST/pump_test.mcf")
SSI.Fg_loadConfig(fg,"C:/Users/oe-fatality64-user/Desktop/GHOST/test_only.mcf")

# SSI.Fg_loadConfig(fg,r"C:\Users\oe-fatality64-user\Desktop\Labview Code\TA_Labview_DEV\SENSOR\STEMMER\REF_CONFIG_170823 - Copy.mcf")
#Define the aquisition parameters
width = 2048

height = 4
samplePerPixel = 1
bytePerSample = 1
nbBuffers = 80000
totalBufferSize = width * height * samplePerPixel * bytePerSample * nbBuffers
nrOfPicturesToGrab = SSI.GRAB_INFINITE
rep_rate = 5000

class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QHBoxLayout())
        self.setWindowTitle("Line Camera Differential")
        self.canvas1 = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas1,0)
        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)
        self.spectra = self.canvas1.addPlot(colspan=2)
        #self.spectra.setMaximumHeight(150)
 
        #### Set Data  #####################
        self.cur_pic_nr = 0
        self.last_pic_nr=0
        self.i = 0
        self.no_of_avgs = 4
        self.spec = np.zeros((self.no_of_avgs,int(width/2)))
        self.img = "will point to last grabbed image"
        self.nImg = "will point to Numpy image/matrix"
        self.memHandle = SSI.Fg_AllocMemEx(fg, totalBufferSize, nbBuffers)
        err = SSI.Fg_AcquireEx(fg, camPort, nrOfPicturesToGrab, SSI.ACQ_STANDARD, self.memHandle)
        self.fps = 0.
        self.lastupdate = time.time()
        #### Start  #####################
        self._update()

    def _update(self):
        t = time.time()
        self.i=0
        while self.i < self.no_of_avgs:
            self.cur_pic_nr = SSI.Fg_getLastPicNumberBlockingEx(fg, self.last_pic_nr + 1, camPort, 5, self.memHandle)
            self.last_pic_nr = self.cur_pic_nr
            self.img = SSI.Fg_getImagePtrEx(fg, self.last_pic_nr, camPort, self.memHandle)
            self.nImg = SSI.getArrayFrom(self.img, width, height)
            self.spec[self.i,:] = np.mean(self.nImg[:2,1::2]*2**8 + self.nImg[:2,0::2],axis =0)
            #print(np.mean(self.nImg[:,1::2],axis =0))
            #self.spec[self.i,:] = np.mean(self.nImg[:,:],axis =0)

            self.i+=1  
        self.s = np.mean(self.spec,axis =0)
        self.spectra.plot(self.s, clear=True)
        self.i=0
        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        "Run update again after 1ms"
        QtCore.QTimer.singleShot(1, self._update)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())