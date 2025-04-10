# Line Camera for GHOST set up
import sys
import time
import numpy as np
# runfile('C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib/SiSoPyInterface.py',
#         wdir='C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib')
import SiSoPyInterface as SSI
# import SiSoPyInterface as SSI
from pyqtgraph.Qt import QtCore
print('Line camera interface initialised')


# FrameGrabber parameters
boardId = 0
applet = 'DualLineGray16'
camPort = SSI.PORT_A
FG = SSI.Fg_InitEx(applet, boardId, 0);
# Aquisition parameters
height = 4
width = 2048
samplePerPixel = 1
bytePerSample = 1
noBuffers = 40000
picsToGrab = SSI.GRAB_INFINITE

# def FrameGrabber(pumper_on:bool, laser_on:bool, line_f:int)->None:
#     if pumper_on and laser_on:
#         if line_f == 8:
#             SSI.Fg_loadConfig(self.FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/pump_on.mcf")
#         elif line_f == 4:
#             SSI.Fg_loadConfig(self.FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/test_only.mcf")
#     if not pumper_on and not laser_on:
#         SSI.Fg_loadConfig(self.FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/laser_off_conf.mcf")

# def BufferSetup(pumper_on:bool, line_f:int)->None:
#     if pumper_on :
#         totalBufferSize = width * line_f * samplePerPixel * bytePerSample * noBuffers
#     else:
#         totalBufferSize = width * height * samplePerPixel * bytePerSample * nbBuffers
#     memHandle = SSI.Fg_AllocMemEx(FG, totalBufferSize, noBuffers)
#     err = SSI.Fg_AcquireEx(FG, camPort, picsToGrab, SSI.ACQ_STANDARD, memHandle)  
   
# def Transfer(pumper_on:bool, line_f:int)->(int, int, np.ndarray):
#     new_img_no = SSI.Fg_getLastPicNumberBlockingEx(FG, old_img_no + 1, camPort, 5, memHandle)
#     old_img_no= new_img_no
#     image_pnt = SSI.Fg_getImagePtrEx(FG, old_img_no, camPort, memHandle)
#     if pumper_on:
#         h_line_stack = SSI.getArrayFrom(image_pnt, width, line_f)
#     else:
#         h_line_stack = SSI.getArrayFrom(image_pnt, width, height)
#     print(type(h_line_stack))
#     return new_img_no, old_img_no, h_line_stack

class LineCameraAquisition(QtCore.QThread):
    def __init__(self, pumper_on, laser_on, line_factor): 
        super().__init__()
        self.cleanup_framegrabber = False
        self.old_img_no = 0
        self.new_img_no = 0
        if pumper_on:
            if line_factor == 8:
                self.data_block = np.zeros((8, width))
            if line_factor == 4:
                self.data_block = np.zeros((4, width))
        else:
            self.data_block = np.zeros((4, width))
        self.pump_on = pumper_on
        self.laser_on = laser_on
        self.line_f = line_factor
        self.FrameGrabber()
        self.BufferSetup()
        print(self.pump_on, self.laser_on, self.line_f)
            
    def FrameGrabber(self)->None:
        if self.laser_on:
            if self.pump_on:
                if self.line_f == 8:
                    SSI.Fg_loadConfig(FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/pump_test.mcf")
                    print('using pump_test')
                elif self.line_f == 4:
                    SSI.Fg_loadConfig(FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/test_only.mcf")
                    print('using test_only')
            else:
                SSI.Fg_loadConfig(FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/test_only.mcf")
                print('using test_only')
        else:
            SSI.Fg_loadConfig(FG,"C:/Users/oe-fatality64-user/Desktop/GHOST/laser_off_conf.mcf")
            print('using laser_off')

    def BufferSetup(self)->None:
        if self.pump_on :
            totalBufferSize = width * self.line_f * samplePerPixel * bytePerSample * noBuffers
        else:
            totalBufferSize = width * height * samplePerPixel * bytePerSample * noBuffers
        self.memHandle = SSI.Fg_AllocMemEx(FG, totalBufferSize, noBuffers)
        err = SSI.Fg_AcquireEx(FG, camPort, picsToGrab, SSI.ACQ_STANDARD, self.memHandle)  
       
    def Transfer(self)->(int, int, np.ndarray):
        self.new_img_no = SSI.Fg_getLastPicNumberBlockingEx(FG, self.old_img_no + 1, camPort, 5, self.memHandle)
        self.old_img_no= self.new_img_no
        image_pnt = SSI.Fg_getImagePtrEx(FG, self.old_img_no, camPort, self.memHandle)
        if self.pump_on:
            h_line_stack = SSI.getArrayFrom(image_pnt, width, self.line_f)
        else:
            h_line_stack = SSI.getArrayFrom(image_pnt, width, height)
        return self.new_img_no, self.old_img_no, h_line_stack

    def run(self):
        while not self.cleanup_framegrabber:
            # grab block from camera put into buffer
            self.new_img_no, self.old_img_no, self.data_block = self.Transfer()
        SSI.Fg_stopAcquire(FG, camPort)
        SSI.Fg_FreeMemEx(FG, self.memHandle)
        SSI.Fg_FreeGrabber(FG)
        print('Disconnected Line Camera')
