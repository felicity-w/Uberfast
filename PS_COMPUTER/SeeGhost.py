# class for line camera disply on GHOST
import numpy as np 
from pyqtgraph.Qt import QtCore

class LineCameraDisplay(QtCore.QThread):
    Ghost_avg = QtCore.pyqtSignal(np.ndarray)
    Spot = QtCore.pyqtSignal(np.float64)
    Line_avg = QtCore.pyqtSignal(np.ndarray)
    A_spot = QtCore.pyqtSignal(np.float64)
    On_phase = QtCore.pyqtSignal(np.ndarray)
    Off_phase = QtCore.pyqtSignal(np.ndarray)
    def __init__(self,no_of_avg_ghost, pumper_on, laser_on, line_factor):
        super().__init__()
        self.emit_ghost = False
        self.emit_spot = False
        self.emit_a_line = False
        self.emit_a_spot = False
        self.emit_on = False
        self.emit_off = False
        self.no_of_frozen_lines = 0
        self.no_of_avgs_ghost = no_of_avg_ghost
        if pumper_on:
            self.lines_per_img = line_factor
            self.pump_on = True
        else:
            self.lines_per_img = 4
            self.pump_on = False
        self.laser_on = laser_on
        self.new_img_no = 0
        self.old_img_no = 0
        self.h_line_stack = np.zeros((self.lines_per_img, 2048))
        self.test_on = np.zeros((self.no_of_avgs_ghost,1024)) 
        self.test_off = np.zeros((self.no_of_avgs_ghost,1024))
        self.test_on_pump_on = np.zeros((self.no_of_avgs_ghost,1024)) 
        self.test_on_pump_off = np.zeros((self.no_of_avgs_ghost,1024)) 
        self.test_off_pump_on = np.zeros((self.no_of_avgs_ghost,1024))
        self.test_off_pump_off = np.zeros((self.no_of_avgs_ghost,1024))
        self.avg_ghost  = np.zeros((1024))
        self.avg_spot  = 0.
        self.avg_line = np.zeros((1024))
        self.line_spot = 0.
        self.avg_on = np.zeros((1024))
        self.avg_off = np.zeros((1024))

    def run(self):
        self.LineCameraAcq = GC.LineCameraAquisition(self.pump_on, self.laser_on, self.lines_per_img )
        self.LineCameraAcq.start()
        while not self.LineCameraAcq.cleanup_framegrabber:
            # analysis and manipulation of aqu array
            self.counter = 0
            while self.counter < self.no_of_avgs_ghost:
                #Catch a change in the nuber of averages disp class
                if self.no_of_avgs_ghost != np.shape(self.test_on)[0]:
                    self.test_on = np.zeros((self.no_of_avgs_ghost,1024))
                    self.test_off = np.zeros((self.no_of_avgs_ghost,1024))
                # get image in
                self.h_line_stack = self.LineCameraAcq.data_block
                # pixel overflow
                self.test_on[self.counter,:] = np.mean(self.h_line_stack[:int(self.lines_per_img/2),1::2]*2**8 + self.h_line_stack[:int(self.lines_per_img/2),0::2], axis = 0)
                self.test_off[self.counter,:] = np.mean(self.h_line_stack[int(self.lines_per_img/2):,1::2]*2**8 + self.h_line_stack[int(self.lines_per_img/2):,0::2], axis = 0)
                self.counter +=1
            # signal emitted from here if the bools allow ->needs if statements from app class
            # then do the averaging for the ons and off
            if self.emit_ghost:
                self.avg_ghost = np.mean((self.test_on - self.test_off )/ self.test_off**(0.75) , axis=0)
                self.Ghost_avg.emit(self.avg_ghost)
            if self.emit_spot:
                self.avg_spot = np.mean( np.mean((self.test_on - self.test_off )/ self.test_off**(0.75) , axis=0) , axis=0)
                self.Spot.emit(self.avg_spot)
            if self.emit_a_line:
                self.avg_line = np.mean((self.test_on + self.test_off)/2, axis=0)
                self.Line_avg.emit(self.avg_line)
            if self.emit_a_spot:
                self.line_spot = np.mean(np.mean((self.test_on + self.test_off)/2, axis=0), axis=0)
                self.A_spot.emit(self.line_spot)
            if self.emit_on:
                self.avg_on = np.mean(self.test_on , axis=0)
                self.On_phase.emit(self.avg_on)
            if self.emit_off:
                self.avg_off = np.mean(self.test_off , axis=0)
                self.Off_phase.emit(self.avg_off)