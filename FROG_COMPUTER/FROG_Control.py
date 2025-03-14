# FROG Main interface
import os
import sys
import time
import qdarkstyle
import numpy as np
import colorcet as cc
import pyqtgraph as pg
from scipy import fftpack
import AgilisConnect as AC
#import PulseRetrieval as PR
import FROG_Spectrometer as FS
from scipy.signal import find_peaks
from Frogometer_UI import Ui_MainWindow
# from scipy.interpolate import interp1d
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
np.seterr(divide='ignore', invalid='ignore')


class App(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self) 
        app.setStyleSheet(qdarkstyle.load_stylesheet())

        "For the Measurement Control Page: "
        "Initialise the "
        
        "Setup view box for the intensity-wavelength line plot "
        self.Intensity_SHG_plot = self.ui.Intensity_SHG.addPlot(labels =  {'left':'Intensity', 'bottom':'Wavelength (nm)'})
        self.Intensity_SHG_plot.setTitle('Spectrum')
        self.Intensity_SHG_Line = self.Intensity_SHG_plot.plot(clear = True)
        self.wav_region =  pg.LinearRegionItem([300, 400], bounds=[100,1200], movable=True)
        self.Intensity_SHG_plot.addItem(self.wav_region)
        self.calib_line = pg.InfiniteLine(550,angle=90, bounds=[100,1200],movable=True)
        self.Intensity_SHG_plot.addItem(self.calib_line)
        self.SHG_line = pg.InfiniteLine(283,angle=90, bounds=[100,1200],movable=True)
        self.Intensity_SHG_plot.addItem(self.SHG_line)
        
        "Setup view box for the new spectrogram 2D plot "
        self.New_spec_plot = self.ui.New_spec.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time'})
        self.New_spec_plot.setTitle('New')
        self.New_spec_img = pg.ImageItem()
        self.histn = pg.HistogramLUTItem(fillHistogram=False)
        self.histn.setImageItem(self.New_spec_img)
        self.ui.New_spec.addItem(self.histn,0)
        self.New_spec_plot.addItem(self.New_spec_img)

        "Setup view box for the old spectrogram 2D plot "
        self.Old_spec_plot = self.ui.Old_spec.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time'})
        self.Old_spec_plot.setTitle('Old')
        self.Old_spec_img = pg.ImageItem()
        self.histo = pg.HistogramLUTItem(fillHistogram=False)
        self.histo.setImageItem(self.Old_spec_img)
        self.ui.Old_spec.addItem(self.histo,0)
        self.Old_spec_plot.addItem(self.Old_spec_img)
        
        "Connect the Location "
        self.ui.Location.returnPressed.connect(self.ChangeLocation)
        self.Path = 'D:\\Data'
        
        "Connect the File Name "
        self.ui.File_name.returnPressed.connect(self.ChangeFileName) 
        self.Name = 'NoNameIdiot'
        
        "Connect the Exposure time "
        self.ui.ExposureTime.insert(str(FS.get_int_time()))
        self.ExTime = int(self.ui.ExposureTime.text())
        self.ui.ExposureTime.returnPressed.connect(self.ChangeExposureTime)
        
        "Connect the Delay steps "
        self.ui.DelaySteps.insert(str(300))
        self.delay_steps = int(self.ui.DelaySteps.text())
        self.ui.DelaySteps.returnPressed.connect(self.ChangeDelaySteps)
        
        "Connect the push button for the live display "
        self.ui.Live.setCheckable(True)
        self.ui.Live.clicked.connect(self.DisplayLiveSpectrum)
        self.ui.Live.setChecked(False)
              
        "Connect the tool button for the Forwards stage motion "
        self.ui.Forward.clicked.connect(self.IncrementForwards)
        
        "Connect the tool button for the fast Forwards stage motion "
        self.ui.Forward_Fast.clicked.connect(self.IncrementForwardsFast)
        
        "Connect the tool button for the Backwards stage motion "
        self.ui.Back.clicked.connect(self.IncrementBackwards)
        
        "Connect the tool button for the fast Backwards stage motion "
        self.ui.Back_Fast.clicked.connect(self.IncrementBackwardsFast)
        
        "Connect the tool button for Setting Home "
        self.ui.Set_Home.clicked.connect(self.SetHome)
        
        "Connect the tool button for the go Home stage motion "
        self.ui.Go_Home.clicked.connect(self.GoHome)
                
        "Connect the tool button for the save spectrum "
        self.ui.SaveSpectrum.clicked.connect(self.SaveSpec)
        
        "Connect the tool button for the Run from Centre stage motion "
        self.ui.Run_Home.clicked.connect(self.RunFromCentre)
        
        "Connect the tool button for the Run from Back stage motion "
        self.ui.Run_Back.clicked.connect(self.RunFromBack)
        
        "Connect the tool button for the Run from Front stage motion "
        self.ui.Run_Front.clicked.connect(self.RunFromFront)
        
        "Connect the tool button for the Run from Back stage motion "
        self.ui.Run_Calib_Back.clicked.connect(self.RunCalibFromBack)
        
        "Connect the tool button for the Run from Front stage motion "
        self.ui.Run_Calib_Front.clicked.connect(self.RunCalibFromFront)

        "Connect the push button for the Select path "
        self.ui.SelectPath.clicked.connect(self.ChangeLocationPop)
        
        "Connect the tool button for the Abort measurement "
        self.ui.Abort.clicked.connect(self.Abort)
        
        
        "For the Calibration Control Page: "
        "Initialise the "
        
        "Setup view box for the raw back calibration plot "        
        self.Calib_raw_back_plot = self.ui.Calib_raw_bk.addPlot(labels =  {'left':'Intensity', 'bottom':'Steps'})
        self.Calib_raw_back_plot.setTitle('Oscillations')
        self.Calib_raw_back_line = self.Calib_raw_back_plot.plot(clear = False)
        self.SHG_raw_back_line = self.Calib_raw_back_plot.plot(clear = False)
        
        "Setup view box for the raw front calibration plot "
        self.Calib_raw_front_plot = self.ui.Calib_raw_ft.addPlot(labels =  {'left':'Intensity', 'bottom':'Steps'})
        self.Calib_raw_front_plot.setTitle('Oscillations')
        self.Calib_raw_front_line = self.Calib_raw_front_plot.plot(clear = False)
        self.SHG_raw_front_line = self.Calib_raw_front_plot.plot(clear = False)
        
        "Setup view box for the fft back calibration plot "
        self.Calib_fft_back_plot = self.ui.Calib_fft_bk.addPlot(labels =  {'left':'Amplitude', 'bottom':'Frequency (THz)'})
        self.Calib_fft_back_plot.setTitle('FFT')
        
        "Setup view box for the fft front calibration plot "
        self.Calib_fft_front_plot = self.ui.Calib_fft_ft.addPlot(labels =  {'left':'Amplitude', 'bottom':'Frequency (THz)'})
        self.Calib_fft_front_plot.setTitle('FFT')
        
        "Connect the Back amplitude "
        self.ui.Back_Amplitude.insert(str(AC.GetBackStep()))
        self.BkAmp = int(self.ui.Back_Amplitude.text())
        self.ui.Back_Amplitude.returnPressed.connect(self.SetAmplitudeBack)
        
        "Connect the Front amplitude "
        self.ui.Front_Amplitude.insert(str(AC.GetFrontStep()))
        self.FtAmp = int(self.ui.Front_Amplitude.text())
        self.ui.Front_Amplitude.returnPressed.connect(self.SetAmplitudeFront)
        
        "Connect the tool button for the Update back calibration "
        self.ui.UpdateBack.clicked.connect(self.DoUpdateBack)
        
        "Connect the tool button for the Update Front Calibration  "
        self.ui.UpdateFront.clicked.connect(self.DoUpdateFront)

        
        "Initialise the progress bar"
        self.ui.ProgressBar.setValue(0)
        
        "For the Frogging Control Page: "
        "Initialise the "
        
        "Setup view box for the intensity-wavelength plot "
        self.Intensity_wav_plot = self.ui.Intensity_Wavelength.addPlot(labels =  {'left':'Intensity', 'bottom':'Wavelength (nm)'})
        self.Intensity_wav_plot.setTitle('Frequency')
        self.Intensity_Wav_Line = self.Intensity_wav_plot.plot(clear = True)
        
        "Setup view box for the intensity-time plot "
        self.Intensity_time_plot = self.ui.Intensity_Time.addPlot(labels =  {'left':'Intensity', 'bottom':'Time'})
        self.Intensity_time_plot.setTitle('Time')
        self.Intensity_Time_Line = self.Intensity_time_plot.plot(clear = True)
        
        "Setup view box for the manipulation 2D plot "
        self.Manip_plot = self.ui.Spec_Manipulation.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time'})
        self.Manip_plot.setTitle('Measurement')
        
        "Setup view box for the retrieved 2D plot "
        self.Retrieved = self.ui.Retrieved.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time'})
        self.Retrieved.setTitle('Retrieved')
        
        "Connect the tool button for the set ROI manipulation "
        self.ui.Set_ROI.clicked.connect(self.SetROI)
        
        "Connect the tool button for the reset ROI manipulation "
        self.ui.Reset_ROI.clicked.connect(self.ResetROI)
        
        "Connect the tool button for the C manipulation "
        self.ui.C.clicked.connect(self.DoC)
        
        "Connect the tool button for the E manipulation "
        self.ui.E.clicked.connect(self.DoE)
        
        "Connect the tool button for the F manipulation "
        self.ui.F.clicked.connect(self.DoF)
        
        "Connect the tool button for submitting manipulation "
        self.ui.Submit.clicked.connect(self.SubmitOriginal)
        
        "Connect the tool button for stopping reconstruction "
        self.ui.Stop.clicked.connect(self.StopReconstruction)
        
        "Initialise the bools "
        self.measurement_is_running = False
        self.calib_is_running = False
        self.calib_ran_from_back = False
        self.BeenRun = False 
        
        "Initialise the step conversion data "
        # self.agilis_size = 1.06
        self.agilis_step = 1
        self.agilis_size_b = {}
        self.agilis_size_f = {}
        self.agilis_size_b = {24:0.14, 35:1.06, 25:1.06, 31:1.06 }
        self.agilis_size_f = {19:0.14, 35:1.06, 25:1.06, 31:1.06 }
        
        "Start infinite loop"
        self._update()
    
        
        
    def _update(self):
        # do the updating
        if self.ui.Live.isChecked():
            self.Intensity_SHG_Line.setData(FS.get_spectrum())
            
        # to run a measurement
            if self.measurement_is_running:
                if self.BeenRun:
                    self.Old_spec_img.setImage(self.Old_measurement_data)
                    self.Old_spec_img.setRect(QtCore.QRectF(0, self.Old_wavlow, self.Old_delay_steps, self.Old_wl_range))
                print(self.t)
                self.Progress()
                self.data_stream = FS.get_intensity() 
                self.data_stream_trunc = self.data_stream[self.wavlow_pos: self.wavup_pos]
                self.Measurement_data[self.t] = self.data_stream_trunc
                AC.Move(self.ac_steps)
                #self.Intensity_SHG_Line.setData(self.data_stream)
                self.Intensity_SHG_Line.setData(FS.get_spectrum())
                self.t+=1
                if self.t == self.delay_steps:
                    self.measurement_is_running = False
                    self.Old_measurement_data = self.Measurement_data
                    self.PlottingSpec()
                    self.SaveData()
                    self.ui.ProgressBar.setValue(0)
                self.New_spec_img.setImage(self.Measurement_data)
                self.New_spec_img.setRect(QtCore.QRectF(0, self.wavlow, self.delay_steps, self.wl_range))

        
        # to run a calibration
            if self.calib_is_running:
                # print(self.t)
                self.Progress()
                self.data_stream = FS.get_intensity()
                self.data_stream_calib = self.data_stream[self.caliwav_pos]
                self.Calibration_data[self.t] = self.data_stream_calib
                self.data_stream_shg = self.data_stream[self.SHG_pos]
                self.SHG_data[self.t] = self.data_stream_shg
                AC.Move(self.ac_steps)
                # time.sleep((self.ExTime + 10)/1000)
                self.PlotOscillations()
                self.t+=1
                if self.t == self.delay_steps:
                    self.calib_is_running = False
                    self.ui.Run_Calib_Back.setStyleSheet('color:black')
                    self.ui.Run_Calib_Front.setStyleSheet('color:black')
                    self.FindConversion()
                    self.SaveCalibration()
                    self.PlotCalibration()
                    self.ui.ProgressBar.setValue(0)
        
        "Run update again after 1ms"
        QtCore.QTimer.singleShot(1, self._update)
                

    def PlottingSpec(self)->None:
        self.BeenRun = True
        self.Old_wavlow = self.wavlow
        self.Old_delay_steps = self.delay_steps
        self.Old_wl_range = self.wl_range
       
    def SaveData(self)->None:
        head = str(self.delay_steps)+'\t'+ str(self.wl_pixels)+'\t'+str(self.agilis_size)+'\t'+ str(self.wl_step_width)+'\t' +str(self.wl_centre)
        pathfile = self.Path +'\\'+ self.Name +'.dat'
        np.savetxt(pathfile, self.Measurement_data, header = head, delimiter ='\t', newline = '\n', comments='' )
        print('Saving')
        
    def SaveSpec(self)->None:
        self.full_spec = FS.get_spectrum()
        pathfile = self.Path +'\\'+ self.Name +'_Spectrum.dat'
        np.savetxt(pathfile, self.full_spec, delimiter ='\t', newline = '\n', comments='' )
        print('Saving')

    def ChangeLocation(self)->None:
        self.Path = self.ui.Location.text()
        print(self.Path)
        
    def ChangeLocationPop(self):
        # os.chdir("C:/Users/")
        # os.chdir('C:/Users/')
        # os.chdir('C:/Users')
        # os.chdir('C://Users')
        # os.chdir('C:\\Data')
        # self.filepath = str(QtWidgets.QFileDialog.getExistingDirectory(self,'Select Directory', os.getcwd()))
        # dirt = str(QtWidgets.QFileDialog.getExistingDirectory(None, 'Select project folder:', os.getcwd(), QtWidgets.QFileDialog.ShowDirsOnly))
        # self.ui.Path.clear()
        # self.ui.Path.insert(os.path.abspath(self.filepath))
        # self.Path.clear()
        # os.chdir("D:/Data/")
        # self.filepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select project folder:'))#, os.getcwd(), QtWidgets.QFileDialog.ShowDirsOnly))
        #self.ui.Path.clear()
        #self.ui.Path.insert(os.path.abspath(self.filepath))
        #print(Path)
        print('this function does nothing')
        
       
    def ChangeFileName(self)->None:
        self.Name = self.ui.File_name.text()
        
    def ChangeExposureTime(self)->None:
        self.ExTime = int(self.ui.ExposureTime.text())
        print(' '+str(self.ExTime)+' ms')
        FS.set_int_time(self.ExTime)
        
    def ChangeDelaySteps(self)->None:
        self.delay_steps = int(self.ui.DelaySteps.text())
        print(' '+str(self.delay_steps)+' steps')
        
    def DisplayLiveSpectrum(self)->None:
        if self.ui.Live.isChecked():
            self.ui.Live.setStyleSheet('color:green')
        else:
            self.ui.Live.setStyleSheet('color:black')
        
    def IncrementForwards(self)->None:
        self.ui.Forward.setStyleSheet('color:green')
        if AC.MoveForwards(self.agilis_step):
            print(' Moved '+str(self.agilis_step)+' steps forwards')
            self.ui.Forward.setStyleSheet('color:black')
        else:
            print('Did not move')
            self.ui.Forward.setStyleSheet('color:black')
            
    def IncrementBackwards(self)->None:
        self.ui.Back.setStyleSheet('color:green')
        if AC.MoveBackwards(self.agilis_step):
            print(' Moved '+str(self.agilis_step)+' steps backwards')
            self.ui.Back.setStyleSheet('color:black')
        else:
            print('Did not move')
            self.ui.Back.setStyleSheet('color:black')
            
    def IncrementForwardsFast(self)->None:
        self.ui.Forward_Fast.setStyleSheet('color:green')
        if AC.MoveForwards(15):
            print(' Moved '+str(self.agilis_step)+' *15 steps forwards')
            self.ui.Forward_Fast.setStyleSheet('color:black')
        else:
            print('Did not move')
            self.ui.Forward_Fast.setStyleSheet('color:black')
            
    def IncrementBackwardsFast(self)->None:
        self.ui.Back_Fast.setStyleSheet('color:green')
        if AC.MoveBackwards(15):
            print(' Moved '+str(self.agilis_step)+' *15 steps backwards')
            self.ui.Back_Fast.setStyleSheet('color:black')
        else:
            print('Did not move')
            self.ui.Back_Fast.setStyleSheet('color:black')
    
    def SetHome(self)->None:
        if AC.SetHome():
            print('Home point set')
            
    def GoHome(self)->None:
        if AC.GoHome():
            print('At home')
            
    def RunFromCentre(self)->None:
        self.SetHome()
        print('Runing from centre')
        steps_to_go = self.agilis_step*self.delay_steps//2
        for i in range(0,steps_to_go):
            AC.MoveBackwards(1)
            i+=1
        self.agilis_size = self.agilis_size_f[AC.GetFrontStep()]
        self.RunMeasurement(self.agilis_step)
        
    def RunFromBack(self)->None:
        self.SetHome()
        print('Runing from back')
        self.agilis_size = self.agilis_size_f[AC.GetFrontStep()]
        self.RunMeasurement(self.agilis_step)
        
    def RunFromFront(self)->None:
        self.SetHome()
        print('Runing from front')
        self.agilis_size = self.agilis_size_b[AC.GetBackStep()]
        self.RunMeasurement(-self.agilis_step)
       
    def RunMeasurement(self, steps:int)->None:
        self.SetWavelengthRange()
        self.ChangeDelaySteps()
        self.ChangeExposureTime()
        #self.ChangeFileName()
        self.Measurement_data = np.zeros((self.delay_steps, self.wl_pixels))
        self.ac_steps = steps
        self.measurement_is_running = True
        self.t = 0
            
    def SetWavelengthRange(self)->None:
        self.wl_full = FS.get_all_wl()
        self.wavlow, self.wavup = self.wav_region.getRegion()
        print(str(self.wavlow) + ' to ' + str(self.wavup) )
        self.wavlow_pos = np.argwhere(self.wl_full ==  min(self.wl_full, key=lambda x:abs(x-self.wavlow)))[0][0]
        self.wavup_pos = np.argwhere(self.wl_full ==  min(self.wl_full, key=lambda x:abs(x-self.wavup)))[0][0]
        self.wl_range = self.wavup-self.wavlow
        self.wl_pixels = self.wavup_pos - self.wavlow_pos
        self.wl_step_width = self.wl_range / self.wl_pixels
        self.wl_centre = self.wavlow + (self.wl_range/2)
 
    def Abort(self)->None:
        self.measurement_is_running = False
        self.calib_is_running = False
        print('Aborted')    

    def Progress(self)->None:
        self.ui.ProgressBar.setValue((self.t+1)/self.delay_steps *100)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Calib funcs
    def SetCalibLine(self)->None:
        self.wl_all = FS.get_all_wl()
        self.calibwav = self.calib_line.value() # in nm
        print('calib wl: '+str(self.calibwav))
        self.caliwav_pos = np.argwhere(self.wl_all ==  min(self.wl_all, key=lambda x:abs(x-self.calibwav)))[0][0] # pixel no.
        
    def SetSHGLine(self)->None: 
        self.wl_all = FS.get_all_wl()
        self.SHG = self.SHG_line.value() # in nm
        print('calib wl: '+str(self.SHG))
        self.SHG_pos = np.argwhere(self.wl_all ==  min(self.wl_all, key=lambda x:abs(x-self.SHG)))[0][0] # pixel no.

    def RunCalibFromBack(self)->None:
        self.ui.Run_Calib_Back.setStyleSheet('color:green')
        self.SetHome()
        self.calib_ran_from_back = True
        print('running from back')
        self.RunCalibOnly(self.agilis_step)

    def RunCalibFromFront(self)->None:
        self.ui.Run_Calib_Front.setStyleSheet('color:green')
        self.SetHome()
        self.calib_ran_from_back = False
        print('running from front')
        self.RunCalibOnly(-self.agilis_step)
        
    def RunCalibOnly(self, steps:int)->None:
        self.SetCalibLine()
        self.SetSHGLine()
        self.ChangeDelaySteps()
        self.Calibration_data = np.zeros(self.delay_steps)
        self.SHG_data = np.zeros(self.delay_steps) 
        self.t = 0
        self.ac_steps = steps
        self.calib_is_running = True
    
    def RunCalibToo(self)->None:
        self.SetCalibLine()
        self.ChangeDelaySteps()
        self.Calibration_data = np.zeros(self.delay_steps)  
        self.also_calib_runnning = True
    
    def FindConversion(self)->None:
        self.goal_freq = 299792458*1e9*1e-12/self.calibwav # goal freq
        self.agilis_conv = 1.06
        self.fs2thz = 1e-12*1e15/(self.agilis_conv) # fs to THz
        self.Calibration_data_mean = self.Calibration_data - np.mean(self.Calibration_data)
        self.calib_pad = np.pad(self.Calibration_data_mean, (20,20), 'constant', constant_values=(0,0)) 
        
        fft_cdat = fftpack.fft(self.calib_pad)
        fft_cdat = fftpack.fftshift(fft_cdat)
        self.fft_abs = np.abs(fft_cdat)
        
        ffq_0 = fftpack.fftfreq(len(self.calib_pad))*self.fs2thz 
        ffq_0= fftpack.fftshift(ffq_0)
        ffq_pos = ffq_0[np.where(ffq_0 >= 0)]
        ffq_zero = np.where(ffq_0 == ffq_pos[0])
        ffq_loc = int(ffq_zero[0])
        
        self.fft = self.fft_abs[ffq_loc:]
        loc = np.where(self.fft == max(self.fft))
        self.ratio = self.goal_freq/ffq_pos[loc[0][0]]
        
        print(len(self.fft_abs), len(ffq_0), len(ffq_pos), len(self.fft))
        print(loc[0][0], ffq_pos[loc[0][0]], self.ratio)
        
        ffreq =  fftpack.fftfreq(len(self.calib_pad)) *self.fs2thz *self.ratio
        ffreq = fftpack.fftshift(ffreq)
        self.ffq = ffreq[np.where(ffreq>=0)]
        
        print(self.goal_freq/self.ffq[loc[0][0]])
        
        if self.calib_ran_from_back: # if run from back then update front amp conv
            self.ui.Front_Amp_calib.display(self.agilis_conv/self.ratio)
        else:
            self.ui.Back_Amp_calib.display(self.agilis_conv/self.ratio)
        print('goal: '+str(self.goal_freq)+' THz')
        print('found: '+str(self.ffq[loc[0][0]]))
        print('new conv: ' +str(self.agilis_conv/self.ratio))
        
    def DoUpdateBack(self)->None:
         # if run from back then update front amp conv
         self.agilis_size_f[AC.GetFrontStep()] = self.agilis_conv/self.ratio
    ""
         
    def DoUpdateFront(self)->None:
        # if run from front then update back amp conv
        self.agilis_size_b[AC.GetBackStep()] = self.agilis_conv/self.ratio
            
    def SaveCalibration(self)->None:
        # takes no. of steps, the wl goal, the current step size
        if self.calib_ran_from_back:
            self.agilis_size =self.agilis_conv/self.ratio
            head = str(self.delay_steps)+'\t'+ str(self.calibwav)+'\t'+str(self.agilis_size) 
            pathfile = self.Path +'\\'+ self.Name +'_bk_Calibration.dat'
        else:
            self.agilis_size = self.agilis_conv/self.ratio
            head = str(self.delay_steps)+'\t'+ str(self.calibwav)+'\t'+str(self.agilis_size) 
            pathfile = self.Path +'\\'+ self.Name +'_fr_Calibration.dat'
        np.savetxt(pathfile, self.Calibration_data, header = head, delimiter ='\t', newline = '\n', comments='' )
        print('Saving')
        
    def PlotOscillations(self)->None:
        if self.calib_ran_from_back:
            self.Calib_raw_back_line.setData(self.Calibration_data)
            self.SHG_raw_back_line.setData(self.SHG_data)
        else:
            self.Calib_raw_front_line.setData(self.Calibration_data)
            self.SHG_raw_front_line.setData(self.SHG_data)
        
    def PlotCalibration(self)->None:
        if self.calib_ran_from_back:
            if self.ui.Back_all.isChecked():
                self.Calib_raw_back_line.setData(self.Calibration_data)            
                self.Calib_fft_back_line = self.Calib_fft_back_plot.plot(clear = False)
                self.Calib_fft_back_line.setData(self.ffq, self.fft)
            else:
                self.Calib_raw_back_line.setData(self.Calibration_data)            
                self.Calib_fft_back_line = self.Calib_fft_back_plot.plot(clear = True)
                self.Calib_fft_back_line.setData(self.ffq, self.fft)
        else:
            if self.ui.Front_all.isChecked():
                self.Calib_raw_front_line.setData(self.Calibration_data)
                self.Calib_fft_front_line = self.Calib_fft_front_plot.plot(clear = False)
                self.Calib_fft_front_line.setData(self.ffq, self.fft)
            else:
                self.Calib_raw_front_line.setData(self.Calibration_data)
                self.Calib_fft_front_line = self.Calib_fft_front_plot.plot(clear = True)
                self.Calib_fft_front_line.setData(self.ffq, self.fft)
        self.goal_line_b = pg.InfiniteLine(self.goal_freq, angle=90, movable=False)
        self.goal_line_f = pg.InfiniteLine(self.goal_freq, angle=90, movable=False)
        self.Calib_fft_back_plot.addItem(self.goal_line_b)
        self.Calib_fft_front_plot.addItem(self.goal_line_f)
        # add in vertical lines for goal wl  
   
    def SetAmplitudeBack(self)->None:
        amp = int(self.ui.Back_Amplitude.text())
        if AC.SetBackStep(amp):
            print('Back step amp: '+str(amp))
        
    def SetAmplitudeFront(self)->None:
        amp = int(self.ui.Front_Amplitude.text())
        if AC.SetFrontStep(amp):
            print('Front step amp: '+str(amp))
            
   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FROG X page

# button to convert to differnt delay stage
# new step size box
# change all functions to if stateemnts if they include agilis 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    def SetROI(self)->None:
        # set ROI for manipulation
        print('ROI set')
        
    def ResetROI(self)->None:
        # reset ROI for manipulation
        print('ROI reset')
        
    def DoC(self)->None:
        # do C manipulation
        print('C manip ')
        
    def DoE(self)->None:
        # do E manipulation
        print('E manip ')
        
    def DoF(self)->None:
        # do F manipulation
        print('F manip ')
        
    def SubmitOriginal(self)->None:
        # submit manipulation
        print('Submitted ')
        
    def StopReconstruction(self)->None:
        # stop optimisation
        print('Stopped ')
    
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
        
        