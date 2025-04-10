# GhostBuster
# imports all devices: spetrometer, line camera, phigets, choppers, delay stages (atto, thor)
# imports GUI
# can run and save GHOSTs, spectra,  

import os
import sys
import time
import qdarkstyle
import numpy as np
import pyqtgraph as pg
import GhostCam as GC
import ThorDelay as TD
# import Phydgets as PH
from scipy import fftpack
import ChopperControl as CC
import AttocubeControl as ATC
import GHOST_Spectrometer as GS
from GHOST_UI import Ui_MainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
np.seterr(divide='ignore', invalid='ignore')
print('UI initialising')

class App(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)
        app.setStyleSheet(qdarkstyle.load_stylesheet())        

        "For the Measurement Control Page: "

        "Connect the push button for the Sampling Shutter  "
        self.ui.Sampling_Shutter.setCheckable(True)
        self.ui.Sampling_Shutter.clicked.connect(self.SamplingShutter)
        self.ui.Sampling_Shutter.setChecked(False)

        "Connect the push button for the Test Shutter  "
        self.ui.Test_Shutter.setCheckable(True)
        self.ui.Test_Shutter.clicked.connect(self.TestShutter)
        self.ui.Test_Shutter.setChecked(False)

        "Connect the push button for the Pump Shutter  "
        self.ui.Pump_Shutter.setCheckable(True)
        self.ui.Pump_Shutter.clicked.connect(self.PumpShutter)
        self.ui.Pump_Shutter.setChecked(False)

        "Connect the Move Sampling Delay "
        self.SamplingDelay = float(ATC.getLocation(1))
        self.ui.Sampling_Delay.setDigitCount(10)
        self.ui.Sampling_Delay.display(self.toAtto(self.SamplingDelay))
        self.ui.Move_Sampling_Delay.insert(str(1000))
        self.ui.Move_Sampling_Delay.returnPressed.connect(self.SamplingMove)

        "Connect the Move Pump Delay Small"
        self.PumpDelay = float(ATC.getLocation(0))
        self.ui.Pump_Delay.setDigitCount(10)
        self.ui.Pump_Delay.display(self.toAtto(self.PumpDelay))
        self.ui.Move_Pump_Delay.insert(str(1000))
        self.ui.Move_Pump_Delay.returnPressed.connect(self.PumpMoveSmall)

        "Connect the Move Pump Delay Big"
        self.PumpDelayThor = float(TD.getLocation())# in m 
        self.ui.Pump_Delay_Thor.setDigitCount(10)
        self.ui.Pump_Delay_Thor.display(self.toAtto(self.PumpDelayThor*1e9))
        self.ui.Move_Pump_Delay_Thor.insert(str(100))
        self.ui.Move_Pump_Delay_Thor.returnPressed.connect(self.PumpMoveBig)

        "Connect the tool button for the Incrementing Sampling Forwards "
        self.ui.Sampling_Inc_Delay.insert(str(100))
        self.ui.Inc_Sampling_Pos.clicked.connect(self.IncrementSamplingFwd)

        "Connect the tool button for the Incrementing Sampling Backwards "
        self.ui.Inc_Sampling_Neg.clicked.connect(self.IncrementSamplingBkwd)

        "Connect the tool button for the Continuous Sampling Forwards "
        self.ui.Cont_Sampling_Pos.clicked.connect(self.ContinuousSamplingFwd)

        "Connect the tool button for the Continuous Sampling Backwards "
        self.ui.Cont_Sampling_Neg.clicked.connect(self.ContinuousSamplingBkwd)

        "Connect the tool button for the Incrementing Pump Forwards "
        self.ui.Inc_Pump_Delay.insert(str(100))
        self.ui.Inc_Pump_Pos.clicked.connect(self.IncrementPumpFwd)

        "Connect the tool button for the Incrementing Pump Backwards "
        self.ui.Inc_Pump_Neg.clicked.connect(self.IncrementPumpBkwd)

        "Connect the tool button for the Continuous Pump Forwards "
        self.ui.Cont_Pump_Pos.clicked.connect(self.ContinuousPumpFwd)

        "Connect the tool button for the Continuous Pump Backwards "
        self.ui.Cont_Pump_Neg.clicked.connect(self.ContinuousPumpBkwd)

        "Connect the tool button for the Incrementing Pump Forwards Thor "
        self.ui.Inc_Pump_Delay_Thor.insert(str(100000))
        self.ui.Inc_Pump_Pos_Thor.clicked.connect(self.ThorPumpFwd)

        "Connect the tool button for the Incrementing Pump Backwards Thor "
        self.ui.Inc_Pump_Neg_Thor.clicked.connect(self.ThorPumpBkwd)

        "Connect the tool button for the Define Home Sampling "
        self.ui.Def_Home_Samp.clicked.connect(self.DefineSamplingHome)
        self.Sampling_Home = 0

        "Connect the tool button for the Go Home Sampling "
        self.ui.Go_Home_Samp.clicked.connect(self.GoSamplingHome)
        
        "Connect the tool button for the Find Reference Sampling "
        self.ui.Find_Ref_Samp.clicked.connect(self.FindSamplingRef)
        self.samp_ref = 0
        if ATC.isReferenced(1):
            self.ui.Find_Ref_Samp.setStyleSheet('color:green')

        "Connect the tool button for the Go Reference Sampling "
        self.ui.Go_Ref_Samp.clicked.connect(self.GoSamplingRef)

        "Connect the tool button for the Define Home Pump "
        self.ui.Def_Home_Pump.clicked.connect(self.DefinePumpHome)
        self.Pump_Home = 0

        "Connect the tool button for the Go Home Pump "
        self.ui.Go_Home_Pump.clicked.connect(self.GoPumpHome)

        "Connect the tool button for the Find Reference Pump "
        self.ui.Find_Ref_Pump.clicked.connect(self.FindPumpRef)
        self.pump_ref = 0
        if ATC.isReferenced(0):
            self.ui.Find_Ref_Pump.setStyleSheet('color:green')

        "Connect the tool button for the Go Reference Pump "
        self.ui.Go_Ref_Pump.clicked.connect(self.GoPumpRef)

        "Initialise the progress bar"
        self.ui.progressBarMeasurement.setValue(0)
           
        "Connect the checkbox for the Pump probe  "
        self.ui.Pump_probe_option.setCheckable(True)
        self.ui.Pump_probe_option.setChecked(False)

        "Connect the checkboxbutton for the GHOST  "
        self.ui.GHOST_option.setCheckable(True)
        self.ui.GHOST_option.setChecked(True)

        "Connect the checkbox for the delta GHOST  "
        self.ui.Delta_GHOST_option.setCheckable(True)
        self.ui.Delta_GHOST_option.setChecked(False)    
           
        "Connect the Averages for Run"
        self.ui.Averages_run.insert(str(50))
        self.ui.Averages_run.returnPressed.connect(self.ChangeAveragesRun)
        
        "Connect the Spectrometer sampling steps"
        self.ui.Steps_Spec.insert(str(500))
        self.RunSampSteps = int(self.ui.Steps_Spec.text())
        self.ui.Steps_Spec.returnPressed.connect(self.ChangeSpecSampSteps)
        
        "Connect the tool button for the Incrementing Sampling Run "
        self.ui.Sampling_Inc_Delay_2.insert(str(100))
        
        "Connect the push button for the Running Forwards "
        self.ui.Run_run.setCheckable(True)
        self.ui.Run_run.clicked.connect(self.RunFwd)
        self.ui.Run_run.setChecked(False)
        
        "Connect the push button for the Running Backwards"
        self.ui.Run_run_2.setCheckable(True)
        self.ui.Run_run_2.clicked.connect(self.RunBwd)
        self.ui.Run_run_2.setChecked(False)
        
        "Connect the push button for the Abort running "
        self.ui.Abort_run.setCheckable(True)
        self.ui.Abort_run.clicked.connect(self.StopRunTime)
        self.ui.Abort_run.setChecked(False)

        "For the measurement mini pages "
        
        "Connect the checkbox for spectrometer measurement mode"
        self.ui.measure_spec_on.setCheckable(True)
        self.ui.measure_spec_on.setChecked(False)

        "Connect the checkboxbutton for line camera measurement mode  "
        self.ui.measure_line_on.setCheckable(True)
        self.ui.measure_line_on.setChecked(True)
        
        "Connect the Spectrometer Exposure Time for a measurement"
        try:
            self.ui.Ex_Time_Spec_Measure.insert(str(GS.get_int_time()))
            self.Ex_Time_Spec_Measure = int(self.ui.Ex_Time_Spec_Measure.text())
        except:
            self.ui.Ex_Time_Spec_Measure.insert(str(0))
            self.Spec_Ex_Time_Measure = int(0)
        self.ui.Ex_Time_Spec_Measure.returnPressed.connect(self.ChangeSpecExposureMeasure)
        
        "Connect the Averages for measure sample-test "
        self.ui.Averages_measure.insert(str(50))
        self.ui.Averages_measure.returnPressed.connect(self.ChangeAveragesMeasure)
        
        "Connect the initial time measure sample-test "
        self.ui.samp_int_t.insert(str(50))
        self.ui.samp_int_t.returnPressed.connect(self.ChangeIntSample)
        
        "Connect the sweeps measure sample-test "
        self.ui.samp_sweeps.insert(str(1))
        self.ui.samp_sweeps.returnPressed.connect(self.ChangeSweepsSample)
        self.Sampling_sweeps = int(self.ui.samp_sweeps.text())
        
        "Connect the steps measure sample-test "
        self.ui.samp_steps.insert(str(50))
        self.ui.samp_steps.returnPressed.connect(self.ChangeStepsSample)
        
        "Connect the size measure sample-test "
        self.ui.samp_size.insert(str(200))
        self.ui.samp_size.returnPressed.connect(self.ChangeSizeSample)
        
        "Connect the checkbox for test-sampling mode"
        self.ui.Test_Sampling_Mode.setCheckable(True)
        self.ui.Test_Sampling_Mode.setChecked(True)

        "Connect the checkboxbutton for pump-test-sampling mode  "
        self.ui.Pump_Test_Sampling_Mode.setCheckable(True)
        self.ui.Pump_Test_Sampling_Mode.setChecked(False)

        "Connect the Location "
        self.ui.Location.returnPressed.connect(self.ChangeLocation)
        self.Path = 'C:\\Data\\GHOSTs'
        
        "Connect the File Name "
        self.ui.File_name.returnPressed.connect(self.ChangeFileName) 
        self.Name = 'GhostBuster'
        
        "Connect the push button for the start measurement "
        self.ui.Measure_Start.clicked.connect(self.StartMeasuring)

        "For the Spectrometer Control Page: "

        "Setup view box for the intensity-wavelength line plot "
        self.Spec_plot = self.ui.Spec_Live.addPlot(labels =  {'left':'Intensity', 'bottom':'Wavelength (nm)'})
        self.Spec_plot.setTitle('Spectrum')
        self.Spec_Line = self.Spec_plot.plot(clear = True)
        self.wav_region =  pg.LinearRegionItem([300, 350], bounds=[100,1200], movable=True)
        self.Spec_plot.addItem(self.wav_region)
        
        "Setup view box for the wavelength-time 2D plot "
        self.Spectrogram_plot = self.ui.Spectrogram.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time (steps)'})
        self.Spectrogram_plot.setTitle('Spectrogram')
        self.Spectrogram_Img = pg.ImageItem()
        self.histn = pg.HistogramLUTItem(fillHistogram=False)
        self.histn.setImageItem(self.Spectrogram_Img)
        self.ui.Spectrogram.addItem(self.histn,0)
        self.Spectrogram_plot.addItem(self.Spectrogram_Img)

        "Connect the push button for the Live Spectrometer  "
        self.ui.Live_Spec.setCheckable(True)
        self.ui.Live_Spec.clicked.connect(self.LiveSpec)
        self.ui.Live_Spec.setChecked(False)

        "Connect the tool button for the Freeze Spectrometer intensity "
        self.ui.Freeze_Spec.clicked.connect(self.FreezeSpec)

        "Connect the tool button for the Freeze Spectrometer intensity "
        self.ui.RmFreeze_Spec.clicked.connect(self.RemoveSpec)

        "Connect the tool button for the Freeze Spectrometer intensity "
        self.ui.Save_Spec.clicked.connect(self.SaveSpec)

        "Connect the Spectrometer Exposure Time"
        try:
            self.ui.Ex_Time_Spec.insert(str(GS.get_int_time()))
            self.Spec_Ex_Time = int(self.ui.Ex_Time_Spec.text())
        except:
            self.ui.Ex_Time_Spec.insert(str(0))
            self.Spec_Ex_Time = int(0)
        self.ui.Ex_Time_Spec.returnPressed.connect(self.ChangeSpecExposure)
        
        "For the FFT Control Page: "
        
        "Setup view box for the wavelength-time 2D plot "
        self.Spectrogram_2_plot = self.ui.Spectrogram_2.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Time (fs)'})
        self.Spectrogram_2_plot.setTitle('Spectrogram')
        self.Spectrogram_2_Img = pg.ImageItem()
        self.histn_2 = pg.HistogramLUTItem(fillHistogram=False)
        self.histn_2.setImageItem(self.Spectrogram_2_Img)
        self.ui.Spectrogram_2.addItem(self.histn_2,0)
        self.Spectrogram_2_plot.addItem(self.Spectrogram_2_Img)
        
        "Setup view box for the wavelength-freq 2D plot "
        self.Spectrogram_FFT_plot = self.ui.Spectrogram_FFT.addPlot(labels =  {'left':'Wavelength (nm)', 'bottom':'Freqency (THz)'})
        self.Spectrogram_FFT_plot.setTitle('Spectrogram FFT')
        self.Spectrogram_FFT_Img = pg.ImageItem()
        self.histn_FFT = pg.HistogramLUTItem(fillHistogram=False)
        self.histn_FFT.setImageItem(self.Spectrogram_FFT_Img)
        self.ui.Spectrogram_FFT.addItem(self.histn_FFT,0)
        self.Spectrogram_FFT_plot.addItem(self.Spectrogram_FFT_Img)
        
        "Connect the tool button for the Save Spectrogram "
        self.ui.Save_Spectrogram.clicked.connect(self.SaveSpecRun)
        
        "Connect the tool button for the Save Spectrogram FFT "
        self.ui.Save_Spec_FFT.clicked.connect(self.SaveSpecFFT)

        "For the Line Camera Control Page: "

        "Setup view box for the GHOST live plot "
        self.GHOST_plot = self.ui.Line_Ghost.addPlot(labels =  {'left':'Counts', 'bottom':'Pixels'})
        self.GHOST_plot.setTitle('GHOST')
        self.GHOST_Line = self.GHOST_plot.plot(clear = True)
        self.Fund_Line = self.GHOST_plot.plot(clear = False, pen = pg.mkPen(color=(255, 0, 0)))
        
        "Setup view box for the Line Camera live plot "
        self.Line_plot = self.ui.LineLive.addPlot(labels =  {'left':'Counts', 'bottom':'Pixels'})
        self.Line_plot.setTitle('Line Camera Live')
        self.Line_Line = self.Line_plot.plot(clear = True) 
        self.line_region =  pg.LinearRegionItem([750, 790], bounds=[0,1100], movable=True)
        self.Line_plot.addItem(self.line_region)
        self.line_region_2 =  pg.LinearRegionItem([210, 260], bounds=[0,1100], movable=True, brush=(255,0,0,50))
        self.Line_plot.addItem(self.line_region_2)
        
        "Connect the checkbox for the Line Camera pixel integration" 
        self.ui.Int_line_cam.stateChanged.connect(self.IntegrationState)

        "Connect the push button for the Connect Line Camera  "
        self.ui.Connect_Line.setCheckable(True)
        self.ui.Connect_Line.clicked.connect(self.ConnectLine)
        self.ui.Connect_Line.setChecked(False)

        "Connect the push button for the Live GHOST Camera  "
        self.ui.Live_Ghost.setCheckable(True)
        self.ui.Live_Ghost.clicked.connect(self.LiveGhost)
        self.ui.Live_Ghost.setChecked(False)

        "Connect the push button for the Live Line Camera  "
        self.ui.Live_Line_2.setCheckable(True)
        self.ui.Live_Line_2.clicked.connect(self.LiveLine)
        self.ui.Live_Line_2.setChecked(False)
        
        "Connect the tool button for the Freeze Line Camera intensity "
        self.ui.Freeze_Line.clicked.connect(self.FreezeLine)

        "Connect the tool button for the Remove Freeze Line Camera intensity "
        self.ui.RmFreeze_Line.clicked.connect(self.RemoveLine)

        "Connect the tool button for the Save Line Camera intensity "
        self.ui.Save_Line.clicked.connect(self.SaveLine)

        "For the Chopper Page: "

        "Connect the push button for the Test Chopper Run  "
        self.ui.Test_Run.setCheckable(True)
        self.ui.Test_Run.clicked.connect(self.RunTest)
        if CC.getEnable(CC.test):
            self.ui.Test_Run.setChecked(True)
            self.ui.Test_Run.setStyleSheet('color:green')
        else:
            self.ui.Test_Run.setChecked(False)
            self.ui.Test_Run.setStyleSheet('color:black')

        "Connect the push button for the Push Chopper Run  "
        self.ui.Pump_Run.setCheckable(True)
        self.ui.Pump_Run.clicked.connect(self.RunPump)
        if CC.getEnable(CC.pump):
            self.ui.Pump_Run.setChecked(True)
            self.ui.Pump_Run.setStyleSheet('color:green')
        else:
            self.ui.Pump_Run.setChecked(False)
            self.ui.Pump_Run.setStyleSheet('color:black')

        "Connect the Test Chopper Blade "
        self.ui.Test_Blade.insert(str(CC.getBlade(CC.test)))
        self.ui.Test_Blade.returnPressed.connect(self.ChangeTestBlade)

        "Connect the Pump Chopper Blade "
        self.ui.Pump_Blade.insert(str(CC.getBlade(CC.pump)))
        self.ui.Pump_Blade.returnPressed.connect(self.ChangePumpBlade)

        "Connect the Test Chopper Num "
        self.ui.Test_Num.insert(str(CC.getNharm(CC.test)))
        self.NumTest = int(self.ui.Test_Num.text())
        self.ui.Test_Num.returnPressed.connect(self.ChangeTestNum)

        "Connect the Pump Chopper Num "
        self.ui.Pump_Num.insert(str(CC.getNharm(CC.pump)))
        self.NumPump = int(self.ui.Pump_Num.text())
        self.ui.Pump_Num.returnPressed.connect(self.ChangePumpNum)

        "Connect the Test Chopper Den "
        self.ui.Test_Den.insert(str(CC.getDharm(CC.test)))
        self.DenTest = int(self.ui.Test_Den.text())
        self.ui.Test_Den.returnPressed.connect(self.ChangeTestDen)

        "Connect the Pump Chopper Den "
        self.ui.Pump_Den.insert(str(CC.getDharm(CC.pump)))
        self.DenPump = int(self.ui.Pump_Den.text())
        self.ui.Pump_Den.returnPressed.connect(self.ChangePumpDen)

        "Connect the Test input frequency "
        try:
            self.test_in = int(CC.getInput(CC.test))
        except:
            self.test_in = 0
        self.ui.Test_In.display(self.test_in)

        "Connect the pump input frequency "
        try:
            self.pump_in = int(CC.getInput(CC.pump))
        except:
            self.pump_in = 0
        self.ui.Pump_In.display(self.pump_in)

        "Connect the Test Phase slider "
        self.ui.Test_Phase_Slider.setRange(0,360)
        self.ui.Test_Phase_Slider.setValue(int(CC.getPhase(CC.test)))
        self.ui.Test_Phase_Slider.setTickInterval(1)
        self.ui.Test_Phase_Slider.sliderReleased.connect(self.ChangeTestPhase)
        self.ui.Test_Phase.display(self.ui.Test_Phase_Slider.value()) 
        self.PhaseTest = self.ui.Test_Phase_Slider.value()

        "Connect the Pump Phase slider "
        self.ui.Pump_Phase_Slider.setRange(0,360)
        self.ui.Pump_Phase_Slider.setValue(int(CC.getPhase(CC.pump)))
        self.ui.Pump_Phase_Slider.setTickInterval(1)
        self.ui.Pump_Phase_Slider.sliderReleased.connect(self.ChangePumpPhase)
        self.ui.Pump_Phase.display(self.ui.Pump_Phase_Slider.value()) 
        self.PhasePump = self.ui.Pump_Phase_Slider.value()
        
        "Connect the push button for the live on off images "
        self.ui.Live_on_off.setCheckable(True)
        self.ui.Live_on_off.clicked.connect(self.RunOnOff)
        self.ui.Live_on_off.setChecked(False)

        "Setup view box for the On images live plot "
        self.OnImg_plot = self.ui.Imges_On.addPlot(labels =  {'left':'Counts', 'bottom':'Pixels'})
        self.OnImg_plot.setTitle('On')
        self.OnImg_Line = self.OnImg_plot.plot(clear = True)

        "Setup view box for the Off images live plot "
        self.OffImg_plot = self.ui.Imges_Off.addPlot(labels =  {'left':'Counts', 'bottom':'Pixels'})
        self.OffImg_plot.setTitle('Off')
        self.OffImg_Line = self.OffImg_plot.plot(clear = True)


        "Initialise the progress bar"
        self.ui.progressBarFrog.setValue(0)
        
        "Initialise the bools"
        self.Live_spectrometer = False
        self.Live_Line = False
        self.Running = False
        self.Measuring = False
        
        "Start infinite loop"
        self._update()

    def _update(self):
        # do the updating
        "Run update again after 1ms"
        QtCore.QTimer.singleShot(1, self._update)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ChangeLocation(self)->None:
        self.Path = self.ui.Location.text()
        print(self.Path)
        
    def ChangeFileName(self)->None:
        self.Name = self.ui.File_name.text()

    def SamplingShutter(self)->None:
        print('sampling shutter open and close')

    def TestShutter(self)->None:
        print('test shutter open and close')

    def PumpShutter(self)->None:
        print('pump shutter open and close')
        
    def ChangeAveragesRun(self)->None:
        av = int(self.ui.Averages_run.text())
        if av >= 1:
            self.disp_avgs = int(self.ui.Averages_run.text())
            if hasattr(self, 'DisplayThread'):
                self.DisplayThread.no_of_avgs_ghost = self.disp_avgs
                
    def ChangeSpecSampSteps(self)->None:
        self.RunSampSteps = int(self.ui.Steps_Spec.text())

    def Progress(self, value)->None:
        self.ui.progressBarMeasurement.setValue((value+1)/self.RunSampSteps *100)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SamplingMove(self)->None:
        ATC.setTarget(1,int(self.toNanomtr(  float(self.ui.Move_Sampling_Delay.text()) +self.Sampling_Home  )))
        ATC.startMove(1)
        while ATC.isMoving(1):
            self.ui.Sampling_Delay.display(self.toAtto(float(ATC.getLocation(1))))
        self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1))-self.Sampling_Home)
           
    def PumpMoveSmall(self)->None:
        ATC.setTarget(0,int(self.toNanomtr(   float(self.ui.Move_Pump_Delay.text()) +self.Pump_Home    )))
        ATC.startMove(0)
        while ATC.isMoving(0):
            self.ui.Pump_Delay.display(self.toAtto(float(ATC.getLocation(0))) -self.Pump_Home )
        self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)

    def PumpMoveBig(self)->None:
        if TD.moveTo(self.toNanomtr(float(self.ui.Move_Pump_Delay_Thor.text()))*1e-9):
            self.ui.Move_Pump_Delay_Thor.display(self.toAtto(float(TD.getLocation())*1e9))
        else:
            pass        
        
    def IncrementSamplingFwd(self)->None:
        if not ATC.isReferenced(1):
            print(self.ui.Sampling_Inc_Delay.text())
            ATC.setForwardSteps(1, int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay.text())) / 100 ))
        else:
            ATC.setTarget(1, ATC.getLocation(1) + int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay.text()))) )
            ATC.startMove(1)
            while ATC.isMoving(1):
                self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
        while ATC.isMoving(1):
            pass
        self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home )

    def IncrementSamplingBkwd(self)->None:
        if not ATC.isReferenced(1):
            print(self.ui.Sampling_Inc_Delay.text())
            ATC.setBackSteps(1, int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay.text())) / 100 ))
        else:
            ATC.setTarget(1,  ATC.getLocation(1) - int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay.text()))) )
            ATC.startMove(1)
            while ATC.isMoving(1):
                self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
        while ATC.isMoving(1):
            pass
        self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
        
    def IncrementSamplingRun(self)->bool:
        if self.Running:
            if ATC.isReferenced(1):
                ATC.setTarget(1,  ATC.getLocation(1) + self.inc)
                ATC.startMove(1)
                while ATC.isMoving(1):
                    pass
                self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
                return True
            else:
                return False
            
    def IncrementSamplingMeasure(self)->bool:
        if self.Measuring:
            if ATC.isReferenced(1):
                ATC.setTarget(1,  ATC.getLocation(1) + self.inc)
                ATC.startMove(1)
                while ATC.isMoving(1):
                    pass
                self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
                return True
            else:
                return False        
        
    def ContinuousSamplingFwd(self)->None:
        print('continuous sampling forwards while held')

    def ContinuousSamplingBkwd(self)->None:
        print('continuous sampling backwards whilst held')

    def IncrementPumpFwd(self)->None:
        if not ATC.isReferenced(0):
            ATC.setForwardSteps(0, float(self.toNanomtr(float(self.ui.Inc_Pump_Delay.text())) / 100 ))
        else:
            ATC.setTarget(0, ATC.getLocation(0) + int(self.toNanomtr(float(self.ui.Inc_Pump_Delay.text()))) )
            ATC.startMove(0)
            while ATC.isMoving(0):
                self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0)) -self.Pump_Home)
        while ATC.isMoving(0):
            pass
        self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)

    def IncrementPumpBkwd(self)->None:
        if not ATC.isReferenced(0):
            ATC.setBackSteps(0, int(self.toNanomtr(float(self.ui.Inc_Pump_Delay.text())) / 100 ))
        else:
            ATC.setTarget(0, ATC.getLocation(0) - int(self.toNanomtr(float(self.ui.Inc_Pump_Delay.text()))) )
            ATC.startMove(0)
            while ATC.isMoving(0):
                self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)
        while ATC.isMoving(1):
            pass
        self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)

    def ContinuousPumpFwd(self)->None:
        print('continuous pump forwards while held')

    def ContinuousPumpBkwd(self)->None:
        print('continuous pump backwards whilst held')

    def ThorPumpFwd(self)->None:
        if TD.moveTo(self.toNanomtr(float(self.ui.Inc_Pump_Delay_Thor.text()))*1e-9):
            self.ui.Pump_Delay_Thor.display(self.toAtto(float(TD.getLocation())*1e9))
        else:
            pass        
        
    def ThorPumpBkwd(self)->None:
        if TD.moveTo(-self.toNanomtr(float(self.ui.Inc_Pump_Delay_Thor.text()))*1e-9):
            self.ui.Pump_Delay_Thor.display(self.toAtto(float(TD.getLocation())*1e9)) 
        else:
            pass  

    def DefineSamplingHome(self)->None:
        self.Sampling_Home = float(self.toAtto(ATC.getLocation(1)))
        self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
        print('Sampling home defined')

    def GoSamplingHome(self)->bool:
        if ATC.isReferenced(1):
            ATC.setTarget(1,  (self.toNanomtr(self.Sampling_Home)))
            ATC.startMove(1)
            while ATC.isMoving(1):
                pass
            self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)) -self.Sampling_Home)
            return True
        else:
            return False
        
    def FindSamplingRef(self)->None:
        self.RefThread = FindReference(1)
        self.RefThread.start()
        if self.RefThread.found:
            self.ui.Find_Ref_Samp.setStyleSheet('color:green')
            self.SamplingDelay = ATC.getLocation(1)
            self.ui.Sampling_Delay.display(self.toAtto(self.SamplingDelay) -self.Sampling_Home)
        else:
            self.ui.Find_Ref_Samp.setStyleSheet('color:black') 
            
    def GoSamplingRef(self)->None:
        if ATC.isReferenced(1):
            ATC.setTarget(1,self.samp_ref)
            ATC.startMove(1)
            while ATC.isMoving(1):
                self.ui.Sampling_Delay.display(self.toAtto(float(ATC.getLocation(1))) -self.Sampling_Home)
            self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1))-self.Sampling_Home)

    def DefinePumpHome(self)->None:
        self.Pump_Home = float(self.toAtto(ATC.getLocation(0)))
        self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0)) -self.Pump_Home)
        print('Pump home defined')


    def GoPumpHome(self)->None:
        if ATC.isReferenced(0):
            ATC.setTarget(0,  (self.toNanomtr(self.Pump_Home)))
            ATC.startMove(0)
            while ATC.isMoving(0):
                pass
            self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0)) -self.Pump_Home)
            return True
        else:
            return False
        
    def FindPumpRef(self)->None:          
        self.RefThread = FindReference(0)
        self.RefThread.start()
        if self.RefThread.found:
            self.ui.Find_Ref_Pump.setStyleSheet('color:green')
            self.pump_ref = ATC.getLocation(0)
            self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)
        else:
            self.ui.Find_Ref_Pump.setStyleSheet('color:black') 
        
    def GoPumpRef(self)->None:
        if ATC.isReferenced(0):
            ATC.setTarget(0,self.pump_ref)
            ATC.startMove(0)
            while ATC.isMoving(0):
                self.ui.Pump_Delay.display(self.toAtto(float(ATC.getLocation(0))) -self.Pump_Home)
            self.ui.Pump_Delay.display(self.toAtto(ATC.getLocation(0))-self.Pump_Home)
        
    def toAtto(self, dist:float)->float:
        # print('toAtto: '+str(dist) + '  '+str(dist * 2 / 0.299792458))
        return dist * 2 / 0.299792458
        
    def toNanomtr(self, time:float)->float:
        # print('tonanomtr: '+str(time) + '  '+str(time * 0.299792458 / 2))
        return time * 0.299792458 / 2
 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LiveSpec(self)->None:
        if self.ui.Live_Spec.isChecked():
            self.Live_Spectrometer = True
            self.UpdateSpec = LiveSpectrometer(self.Live_Spectrometer)
            self.UpdateSpec.Spec.connect(self.CollectSpec)
            self.UpdateSpec.start()
            self.ui.Live_Spec.setStyleSheet('color:green')
        else:
            self.Live_Spectrometer = False
            self.UpdateSpec.live = False
            self.ui.Live_Spec.setStyleSheet('color:black') 

    def CollectSpec(self, data)->None:
        if hasattr(self, 'UpdateSpec'):
            self.Spectrum = data
        else:
            self.Spectrum = np.zeros((2068, 2))
        self.PlotSpec()
            
    def PlotSpec(self)->None:
        if self.ui.Live_Spec.isChecked():
            self.Spec_Line.setData(self.Spectrum)

    def FreezeSpec(self)->None:
        print('freeze a trace from spectrometer')

    def RemoveSpec(self)->None:
        print('fremove frozen trace from spectrometer') 

    def SaveSpec(self)->None:
        # self.full_spec = GS.get_spectrum()
        self.full_spec = self.Spectrum
        pathfile = self.Path +'\\'+ self.Name +'_Spectrum.dat'
        np.savetxt(pathfile, self.full_spec, delimiter ='\t', newline = '\n', comments='' )
        print('Saving trace from spectrometer')
        
    def SaveSpecRun(self)->None:
        if hasattr(self, 'xscale'):
            head = str(self.wavlow) +'\t'+  str(self.wavup) +'\t'+ str(self.wl_step_width) +'\t'+ str(self.xscale) 
            pathfile = self.Path +'\\'+ self.Name +'_spectrogram.dat'
            np.savetxt(pathfile, self.Running_data_spec, header = head, delimiter ='\t', newline = '\n', comments='' )
            print('Saving spectrogram')

    def SaveSpecFFT(self)->None:
        if hasattr(self, 'fscale'):
            head = str(self.wavlow) +'\t'+  str(self.wavup) +'\t'+ str(self.wl_step_width) +'\t'+ str(self.fscale) 
            pathfile = self.Path +'\\'+ self.Name +'_spectrum_ghost.dat'
            np.savetxt(pathfile, self.Oscillating_spectrogram, header = head, delimiter ='\t', newline = '\n', comments='' )
            print('Saving ghost from spectrometer')
            self.GhostRemoval()
            
    def SaveSpecFROG(self)->None:
        if hasattr(self, 'fscale'):
            head = str(self.wavlow) +'\t'+  str(self.wavup) +'\t'+ str(self.wl_step_width) +'\t'+ str(self.fscale) +'\n' +str(self.RunSampSteps)+'\t'+ str(self.wl_pixels)+'\t'+self.ui.Sampling_Inc_Delay_2.text()+'\t'+ str(self.wl_step_width)+'\t' +str(self.wl_centre)
            # head = str(self.delay_steps)+'\t'+ str(self.wl_pixels)+'\t'+str(self.agilis_size)+'\t'+ str(self.wl_step_width)+'\t' +str(self.wl_centre)
            pathfile = self.Path +'\\'+ self.Name +'_spectrum_frog.dat'
            np.savetxt(pathfile, self.frog_spectrogram, header = head, delimiter ='\t', newline = '\n', comments='' )
            print('Saving frog from spectrometer')


    def ChangeSpecExposure(self)->None:
        self.UpdateSpec.live = False
        if int(self.ui.Ex_Time_Spec.text()) >= 6:
            time.sleep(self.Spec_Ex_Time/100)
            GS.set_int_time(int(self.ui.Ex_Time_Spec.text()))
            self.Spec_Ex_Time = int(self.ui.Ex_Time_Spec.text())
            print(' '+str(self.Spec_Ex_Time)+' ms')
        self.UpdateSpec.live = True
        self.UpdateSpec.start()
        
    def SetWavelengthRange(self)->None:
        self.wl_full = GS.get_all_wl()
        self.wavlow, self.wavup = self.wav_region.getRegion()
        print(str(self.wavlow) + ' to ' + str(self.wavup) )
        self.wavlow_pos = np.argwhere(self.wl_full ==  min(self.wl_full, key=lambda x:abs(x-self.wavlow)))[0][0]
        self.wavup_pos = np.argwhere(self.wl_full ==  min(self.wl_full, key=lambda x:abs(x-self.wavup)))[0][0]
        self.wl_range = self.wavup-self.wavlow
        self.wl_pixels = self.wavup_pos - self.wavlow_pos
        self.wl_step_width = self.wl_range / self.wl_pixels
        self.wl_centre = self.wavlow + (self.wl_range/2)
        
    def RunSpec(self)->None:
        self.UpdateSpec.live = False
        time.sleep(self.Spec_Ex_Time/100)
        print('running')
        while self.Running:
                # print(self.t)
                self.Progress(self.t)
                self.Running_data_spec[self.t] = GS.get_intensity()[self.wavlow_pos: self.wavup_pos]
                if not self.IncrementSamplingRun():
                    self.Running = False
                    self.ui.Run_run.setStyleSheet('color:black') 
                    self.ui.Run_run_2.setStyleSheet('color:black') 
                    print('Error::: Sampling stage not referenced')
                self.Spec_Line.setData(GS.get_spectrum())
                self.t += 1
                if self.t == self.RunSampSteps:
                    self.Running = False
                    self.ui.Run_run.setStyleSheet('color:black') 
                    self.ui.Run_run_2.setStyleSheet('color:black') 
                    self.Spectrogram_Img.setImage(self.Running_data_spec)
                    self.ui.progressBarMeasurement.setValue(0)
                    self.FFTSpectrogram()
                    
                    self.xscale = self.toAtto(np.abs(self.inc)) / 1000
                    transform = QtGui.QTransform.fromScale(self.xscale, 1)
                    self.Spectrogram_2_Img.setTransform(transform)
                    self.Spectrogram_2_Img.setImage(self.Running_data_spec)
                    self.Spectrogram_2_Img.setRect(QtCore.QRectF(0, self.wavlow, self.RunSampSteps * self.xscale, self.wl_range ))  
                    
                    self.fscale = self.ffq[-1]/(1e12)
                    transf = QtGui.QTransform.fromScale(self.fscale, 1)
                    self.Spectrogram_FFT_Img.setTransform(transf)
                    self.Spectrogram_FFT_Img.setImage(self.Oscillating_spectrogram)
                    self.Spectrogram_FFT_Img.setRect(QtCore.QRectF(0, self.wavlow, 1 * self.fscale, self.wl_range )) 
                    self.UpdateSpec.live = True
                    self.UpdateSpec.start()
                self.Spectrogram_Img.setImage(self.Running_data_spec)
                self.Spectrogram_Img.setRect(QtCore.QRectF(0, self.wavlow, self.RunSampSteps, self.wl_range ))  
                QtGui.QApplication.processEvents()
    
    def FFTSpectrogram(self)->None:
        # do fft on each frequency of the spectrogram
        self.nm2thz = 1e-12*1e18/(self.toAtto(np.abs(self.inc))) # nm to as to THz 
        print(self.toAtto(np.abs(self.inc)), self.nm2thz)
        for i in range (0,self.wl_pixels):
            self.Running_mean_spec = self.Running_data_spec[:,i] - np.mean(self.Running_data_spec[:,i])
            self.Running_pad_spec = np.pad(self.Running_mean_spec, (20,20), 'constant', constant_values=(0,0)) 
            fft_dat = fftpack.fft(self.Running_pad_spec)
            fft_dat = fftpack.fftshift(fft_dat)
            self.fft_abs = np.abs(fft_dat)
            if i == 0:
                ffreq = fftpack.fftfreq(len(self.Running_pad_spec), d=self.toAtto(np.abs(self.inc))*1e-18 )
                ffreq = fftpack.fftshift(ffreq)
                self.ffq = ffreq[np.where(ffreq>=0)]
                print(self.ffq)
                self.Oscillating_spectrogram = np.zeros((len(self.ffq), self.wl_pixels))
            self.fft = self.fft_abs[len(self.ffq):]
            self.Oscillating_spectrogram[:,i] = self.fft
            i +=1
        
    def GhostRemoval(self)->None:
        # retain only the frog oscillations at SHG frequencies
        self.frog_spectrogram = np.zeros( self.Oscillating_spectrogram.shape )
        for i in range (0,self.wl_pixels):
            curr_wl = self.wavlow + i * self.wl_step_width
            curr_freq =  1e9 *299792458 / curr_wl #Hz
            curr_freq_pos = np.where(self.ffq >= curr_freq)
            upper_wl = curr_wl + 100
            lower_wl =curr_wl - 100
            upper_freq =  1e9 * 299792458 / upper_wl #Hz
            upper_freq_pos = np.where(self.ffq >= upper_freq)
            lower_freq =  1e9 * 299792458 / lower_wl #Hz
            lower_freq_pos = np.where(self.ffq >= lower_freq)
            self.frog_spectrogram[upper_freq_pos[0][0] :lower_freq_pos[0][0],i] = self.Oscillating_spectrogram[ upper_freq_pos[0][0]:lower_freq_pos[0][0],i]
        self.SaveSpecFROG()
            
            
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ConnectLine(self)->None: 
        if self.ui.Connect_Line.isChecked():
            self.ui.Connect_Line.setStyleSheet('color:green')
            self.disp_avgs = int(self.ui.Averages_run.text())
            self.CheckPumper()
            self.CheckTestIn()
            self.ChangeTestNum()
            self.ChangePumpNum()
            self.ChangeTestDen()
            self.ChangePumpDen()
            self.lines = int((int(self.DenTest) * int(self.DenPump) / int(self.NumTest)  )/ int(self.NumPump) )
            self.DisplayThread = LineCameraDisplay(self.disp_avgs, self.pumper_on, self.laser_on, self.lines)
            self.DisplayThread.Ghost_avg.connect(self.PlotGhost)
            self.DisplayThread.Fund_avg.connect(self.PlotFund)
            self.DisplayThread.Spot.connect(self.PlotSpot)
            self.DisplayThread.Line_avg.connect(self.PlotLine)
            self.DisplayThread.A_spot.connect(self.PlotASpot)
            self.DisplayThread.On_phase.connect(self.PlotOnPhase)
            self.DisplayThread.Off_phase.connect(self.PlotOffPhase)
            self.DisplayThread.start()
        else:
            self.ui.Connect_Line.setStyleSheet('color:black') 
            self.DisplayThread.cleanup_framgrabber = True

    def LiveGhost(self)->None:
        # make line camera GHOST live
        if hasattr(self, 'DisplayThread'):
            if self.ui.Live_Ghost.isChecked():
                self.ChangeRegion()
                self.ui.Live_Ghost.setStyleSheet('color:green')
                if self.ui.Int_line_cam.isChecked():
                    self.DisplayThread.emit_ghost = False
                    self.DisplayThread.emit_spot = True
                    self.ChangeSpecSampSteps()
                    if self.ui.Fund_Plot.isChecked():
                        self.DisplayThread.emit_a_fund = True
                    if self.lines == 4:
                        self.Ghost_line_data = np.zeros((self.RunSampSteps))
                        self.Fund_line_data = np.zeros((self.RunSampSteps))
                    else:
                        self.Ghost_line_data = np.zeros((3,self.RunSampSteps))
                        self.Fund_line_data = np.zeros((3,self.RunSampSteps))
                    self.Time_delays_sampling = np.zeros((self.RunSampSteps))
                    self.GHOST_plot.setLabel("bottom", "Time")
                else:
                    self.DisplayThread.emit_spot = False
                    self.DisplayThread.emit_ghost = True
                    if self.ui.Fund_Plot.isChecked():
                        self.DisplayThread.emit_a_fund = False
                    self.GHOST_plot.setLabel("bottom", "Pixels")
            else:
                self.ui.Live_Ghost.setStyleSheet('color:black') 
                self.DisplayThread.emit_ghost = False
                self.DisplayThread.emit_spot = False
                self.DisplayThread.emit_a_fund = False

    def LiveLine(self)->None:
        # make line camera line live
        if hasattr(self, 'DisplayThread'):
            if self.ui.Live_Line_2.isChecked():
                self.ChangeRegion()
                self.ui.Live_Line_2.setStyleSheet('color:green')
                if self.ui.Int_line_cam.isChecked():
                    self.DisplayThread.emit_a_line = False
                    self.DisplayThread.emit_a_spot = True
                    self.ChangeSpecSampSteps()
                    self.Spot_line_data = np.zeros((self.RunSampSteps))
                    self.Line_plot.setLabel("bottom", "Time")
                else:
                    self.DisplayThread.emit_a_spot = False
                    self.DisplayThread.emit_a_line = True
                    self.Line_plot.setLabel("bottom", "Pixels")  
            else:
                self.ui.Live_Line_2.setStyleSheet('color:black')
                self.DisplayThread.emit_a_line = False
                self.DisplayThread.emit_a_spot = False

    def IntegrationState(self)->None:
        self.i = 0
        self.j = 0
        if hasattr(self, 'DisplayThread'):
            self.LiveGhost()
            self.LiveLine()

    def FreezeLine(self)->None: 
        print('Freeze Line camera trace') 

    def RemoveLine(self)->None:
        print('remove line camera trace') 

    def SaveLine(self)->None:
        print('save line camera trace') 
        
    def ChangeRegion(self)->None:
        self.linelow, self.lineup = self.line_region.getRegion()
        self.redlow, self.redup = self.line_region_2.getRegion()
        # print(self.linelow, self.lineup, int(self.linelow), int(self.lineup))
        if hasattr(self, 'DisplayThread'):
            self.DisplayThread.min = self.linelow
            self.DisplayThread.max = self.lineup
            self.DisplayThread.red_min = self.redlow
            self.DisplayThread.red_max = self.redup
        
    def PlotGhost(self, Ghost_avg)->None:
        if self.lines == 8:
            if self.ui.Pump_probe_option.isChecked():
                self.GHOST_Line.setData(Ghost_avg[2])
            if self.ui.GHOST_option.isChecked():
                self.GHOST_Line.setData(Ghost_avg[0])
            if self.ui.Delta_GHOST_option.isChecked():
                self.GHOST_Line.setData(Ghost_avg[1])
        else:
            self.GHOST_Line.setData(Ghost_avg)
                     
    def PlotFund(self, Fund_avg)->None:
        if self.lines == 8:
            if self.ui.Pump_probe_option.isChecked():
                self.Fund_line_data.setData(Fund_avg[2])
            if self.ui.GHOST_option.isChecked():
                self.Fund_line_data.setData(Fund_avg[0])
            if self.ui.Delta_GHOST_option.isChecked():
                self.Fund_line_data.setData(Fund_avg[1])
        else:
            if self.Measuring:
                self.Fund_line_data[self.step_counter%self.RunSampSteps] = Fund_avg
            else:
                self.Fund_line_data[self.i%self.RunSampSteps] = Fund_avg
            
    def PlotSpot(self, Spot)->None:
        self.ChangeSpecSampSteps()
        if not self.Running:
            if self.lines == 4:
                if not self.Measuring:
                    self.Ghost_line_data[self.i%self.RunSampSteps] = Spot
                    self.GHOST_Line.setData(self.Ghost_line_data)
                    if self.ui.Fund_Plot.isChecked():
                        self.Fund_Line.setData(self.Fund_line_data)
                if self.Measuring:
                    self.DisplayThread.emit_spot = False
                    if self.ui.Fund_Plot.isChecked():
                        self.DisplayThread.emit_a_fund = False
                    print('Sweep: '+str(self.sweep_counter +1)+' Step: '+str(self.step_counter+1))
                    self.Ghost_line_data[self.step_counter%self.RunSampSteps] = Spot
                    # print(Spot)
                    self.GHOST_Line.setData(self.Ghost_line_data)
                    self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)))
                    # self.Measurement_Data[self.sweep_counter, self.step_counter%self.MeasureSampSteps] = Spot
                    self.Measurement_Times[self.sweep_counter, self.step_counter%self.MeasureSampSteps] = self.toAtto(ATC.getLocation(1))
                    self.step_counter +=1
                    self.ui.progressBarMeasurement.setValue((self.step_counter +1)*100 / (self.Sampling_sweeps * self.MeasureSampSteps) )
                    # move the stage
                    if not self.IncrementSamplingMeasure():
                        self.Measuring = False
                        self.ui.progressBarMeasurement.setValue(0)
                        self.ui.Live_Ghost.setStyleSheet('color:black') 
                        self.ui.Measure_Start.setStyleSheet('color:black')
                        print('Error::: Sampling stage not referenced') 
                    if (self.step_counter)%self.MeasureSampSteps +1 == self.MeasureSampSteps:
                        self.Measurement_Data[self.sweep_counter :] = self.Ghost_line_data
                        if self.ui.Fund_Plot.isChecked():
                            print('into here 2')
                            self.Measurement_Fund[self.sweep_counter :] = self.Fund_line_data
                        # move back to start
                        if not self.RefThread.GoStart():
                            print('Error::: Sampling stage not able to go to the start position')
                            self.Measuring = False
                            self.ui.progressBarMeasurement.setValue(0)
                            self.ui.Live_Ghost.setStyleSheet('color:black') 
                            self.ui.Measure_Start.setStyleSheet('color:black')
                        self.sweep_counter +=1
                        np.savetxt(self.pathfile, self.Measurement_Data, header = self.head,  delimiter ='\t', newline = '\n', comments='' )
                        np.savetxt(self.pathfile2, self.Measurement_Times, delimiter ='\t', newline = '\n', comments='' )
                        if self.ui.Fund_Plot.isChecked():
                            np.savetxt(self.pathfile3, self.Measurement_Fund, header = self.head,  delimiter ='\t', newline = '\n', comments='' )
                        if self.sweep_counter == self.Sampling_sweeps:
                            self.DisplayThread.emit_spot = False
                            self.DisplayThread.emit_a_spot = False
                            self.ui.Live_Ghost.setStyleSheet('color:black') 
                            self.Measuring = False
                            self.ui.Measure_Start.setStyleSheet('color:black')
                            print('Measurement Finished')
                            self.ui.progressBarMeasurement.setValue(0)  
                    self.DisplayThread.emit_spot = True
                    if self.ui.Fund_Plot.isChecked():
                        self.DisplayThread.emit_a_fund = True
            elif self.lines ==8:
                self.Ghost_line_data[:,self.i%self.RunSampSteps] = Spot[:,0]
                if self.ui.Pump_probe_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[2])
                if self.ui.GHOST_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[0])
                if self.ui.Delta_GHOST_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[1])
            self.i +=1
        elif self.Running:
            self.DisplayThread.emit_spot = False
            if self.ui.Fund_Plot.isChecked():
                self.DisplayThread.emit_a_fund = False
            self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)))
            self.Time_delays_sampling[self.i%self.RunSampSteps] = self.toAtto(ATC.getLocation(1))
            if self.lines == 4:
                self.Ghost_line_data[self.i%self.RunSampSteps] = Spot
                self.GHOST_Line.setData(self.Ghost_line_data)
                if self.ui.Fund_Plot.isChecked():
                    self.Fund_Line.setData(self.Fund_line_data)
            else:
                self.Ghost_line_data[:,self.i%self.RunSampSteps] = Spot[:,0]
                if self.ui.Pump_probe_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[2])
                if self.ui.GHOST_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[0])
                if self.ui.Delta_GHOST_option.isChecked():
                    self.GHOST_Line.setData(self.Ghost_line_data[1])
            self.i +=1
            # move the stage 
            # if not self.DisplayThread.emit_a_spot: # if the live line is not moving it
            if not self.IncrementSamplingRun():
                self.Running = False
                self.ui.Run_run.setStyleSheet('color:black') 
                self.ui.Run_run_2.setStyleSheet('color:black') 
                print('Error::: Sampling stage not referenced') 
            self.DisplayThread.emit_spot = True
            if self.ui.Fund_Plot.isChecked():
                self.DisplayThread.emit_a_fund = True
            if  self.i == self.RunSampSteps:
                self.DisplayThread.emit_spot = False
                self.DisplayThread.emit_a_fund = False
                self.Running = False
                self.ui.Live_Ghost.setChecked(False)
                self.ui.Live_Line_2.setChecked(False)
                self.ui.Live_Ghost.setStyleSheet('color:black') 
                self.ui.Live_Line_2.setStyleSheet('color:black')
                self.ui.Run_run.setStyleSheet('color:black') 
                self.ui.Run_run_2.setStyleSheet('color:black')
                pathfile = self.Path +'\\'+ self.Name +'_GHOSTdata.dat'
                head  =  self.ui.Sampling_Inc_Delay_2.text()
                np.savetxt(pathfile, self.Ghost_line_data, header = head,  delimiter ='\t', newline = '\n', comments='' )
                pathfile2 = self.Path +'\\'+ self.Name +'_GHOSTtimepoints.dat'
                np.savetxt(pathfile2, self.Time_delays_sampling, header = head,  delimiter ='\t', newline = '\n', comments='' )
                if self.ui.Fund_Plot.isChecked():
                    pathfile3 = self.Path +'\\'+ self.Name +'_FUNDdata.dat'
                    np.savetxt(pathfile3, self.Fund_line_data, header = head,  delimiter ='\t', newline = '\n', comments='' )
            
    def PlotLine(self, Line_avg)->None:
        self.Line_Line.setData(Line_avg)
  
    def PlotASpot(self, A_spot)->None:
        self.ChangeSpecSampSteps()
        if not self.Running:
            self.Spot_line_data[self.j%self.RunSampSteps] = A_spot
            self.Line_Line.setData(self.Spot_line_data)
            self.j +=1
        else:
            self.DisplayThread.emit_a_spot = False
            self.ui.Sampling_Delay.display(self.toAtto(ATC.getLocation(1)))
            self.Spot_line_data[self.j] = A_spot
            self.Line_Line.setData(self.Spot_line_data)
            self.j +=1
            # move stage
            # if not self.IncrementSamplingRun():
            #     self.Running = False
            #     self.ui.Run_run.setStyleSheet('color:black') 
            #     self.ui.Run_run_2.setStyleSheet('color:black') 
            #     print('Error::: Sampling stage not referenced')
            self.DisplayThread.emit_a_spot = True
            if  self.j == self.RunSampSteps:
                self.DisplayThread.emit_a_spot = False
                self.Running = False
                self.ui.Live_Line_2.setChecked(False)
                self.ui.Live_Ghost.setChecked(False)
                self.ui.Live_Line_2.setStyleSheet('color:black') 
                self.ui.Live_Ghost.setStyleSheet('color:black') 
                self.ui.Run_run.setStyleSheet('color:black') 
                self.ui.Run_run_2.setStyleSheet('color:black') 
                
    def RunFwd(self)->None:
        self.inc = int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay_2.text())))
        self.ui.Run_run.setStyleSheet('color:green') 
        self.RunTime()
        
    def RunBwd(self)->None:
        self.inc = -int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay_2.text())))
        self.ui.Run_run_2.setStyleSheet('color:green')
        self.RunTime()
        
    def RunTime(self)->None:
        self.ChangeRegion()
        self.ChangeAveragesRun()
        self.ChangeSpecSampSteps()
        self.ui.Int_line_cam.setChecked(True)
        if hasattr(self, 'DisplayThread'):
            self.IntegrationState()
        self.Running = True
        if self.ui.Live_Spec.isChecked():
            if hasattr(self, 'DisplayThread'):
                self.DisplayThread.emit_a_line = False
                self.DisplayThread.emit_a_spot = False
                self.DisplayThread.emit_ghost = False
                self.DisplayThread.emit_spot = False
            self.SetWavelengthRange()
            self.Running_data_spec = np.zeros((self.RunSampSteps, self.wl_pixels))
            self.t = 0
            self.RunSpec()

    def StopRunTime(self)->None:
        self.Running = False
        if hasattr(self, 'DisplayThread'):
            self.DisplayThread.emit_spot = False
            self.DisplayThread.emit_a_spot = False
        self.ui.Live_Ghost.setChecked(False)
        self.ui.Live_Line_2.setChecked(False)
        self.ui.Live_Ghost.setStyleSheet('color:black') 
        self.ui.Live_Line_2.setStyleSheet('color:black') 
        self.ui.Run_run.setStyleSheet('color:black') 
        self.ui.Run_run_2.setStyleSheet('color:black') 
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RunTest(self)->None: 
        if self.ui.Test_Run.isChecked():
            CC.setEnable(CC.test,1)
            self.ui.Test_Run.setStyleSheet('color:green')
        else:
            CC.setEnable(CC.test,0)
            self.ui.Test_Run.setStyleSheet('color:black') 
        
    def RunPump(self)->None:
        if self.ui.Pump_Run.isChecked():
            CC.setEnable(CC.pump,1)
            self.ui.Pump_Run.setStyleSheet('color:green')
        else:
            CC.setEnable(CC.pump,0)
            self.ui.Pump_Run.setStyleSheet('color:black')

    def ChangeTestBlade(self)->None:
        CC.setBlade(test,self.ui.Test_Blade.text()) 

    def ChangePumpBlade(self)->None: 
        CC.setBlade(test,self.ui.Pump_Blade.text()) 
        
    def CheckPumper(self)->None:
        # self.pumper_on = True
        try:
            self.pump_in = int(CC.getInput(CC.pump))
            if self.pump_in == 0:
                self.pumper_on = False
            else:
                self.pumper_on = True
        except:
            self.pump_in = 0
            self.pumper_on = False
        self.ui.Pump_In.display(self.pump_in)
            
    def CheckTestIn(self)->None:
        try:
            self.test_in = int(CC.getInput(CC.test))
            if self.test_in == 0:
                self.laser_on = False
            else:
                self.laser_on = True
        except:
            self.test_in = 0
            self.laser_on = False
        self.ui.Test_In.display(self.test_in)

    def CheckPumpIn(self)->None:
        try:
            self.pump_in = int(CC.getInput(CC.pump))
        except:
            self.pump_in = 0
        self.ui.Pump_In.display(self.pump_in)

    def ChangeTestNum(self)->None:
        if CC.setNharm(CC.test,self.ui.Test_Num.text()):
            self.NumTest = self.ui.Test_Num.text()
        else:
            self.ui.Test_Num.insert(self.NumTest)
        
    def ChangeTestDen(self)->None:
        if CC.setDharm(CC.test,self.ui.Test_Den.text()):
            self.DenTest = self.ui.Test_Den.text()
        else:
            self.ui.Test_Den.insert(self.DenTest)

    def ChangePumpNum(self)->None:
        if CC.setNharm(CC.pump,self.ui.Pump_Num.text()):
            self.NumPump = self.ui.Pump_Num.text()
        else:
            self.ui.Pump_Num.insert(self.NumPump)

    def ChangePumpDen(self)->None:
        if CC.setDharm(CC.pump,self.ui.Pump_Den.text()):
            self.DenPump = self.ui.Pump_Den.text()
        else:
            self.ui.Pump_Den.insert(self.DenPump)

    def ChangeTestPhase(self)->None:
        if CC.setPhase(CC.test,self.ui.Test_Phase_Slider.value()):
            self.PhaseTest = self.ui.Test_Phase_Slider.value()
            self.ui.Test_Phase.display(self.ui.Test_Phase_Slider.value()) 
        else:
            self.ui.Test_Phase_Slider.insert(self.PhaseTest)
        
    def ChangePumpPhase(self)->None:
        if CC.setPhase(CC.pump,self.ui.Pump_Phase_Slider.value()):
            self.PhasePump = self.ui.Pump_Phase_Slider.value()
            self.ui.Pump_Phase.display(self.ui.Pump_Phase_Slider.value()) 
        else:
            self.ui.Pump_Phase_Slider.insert(self.PhasePump)
            
    def RunOnOff(self)->None:
        if self.ui.Live_on_off.isChecked():
            self.ChangeRegion()
            self.ui.Live_on_off.setStyleSheet('color:green')
            self.DisplayThread.emit_on = True
            self.DisplayThread.emit_off = True
        else:
            self.ui.Live_on_off.setStyleSheet('color:black')
            self.DisplayThread.emit_on = False
            self.DisplayThread.emit_off = False
            
    def PlotOnPhase(self, On_phase)->None:
        if hasattr(self, 'DisplayThread'):
            self.ChangeRegion()
            self.OnImg_Line.setData(On_phase)
            
    def PlotOffPhase(self, Off_phase)->None:
        if hasattr(self, 'DisplayThread'):
            self.ChangeRegion()
            self.OffImg_Line.setData(Off_phase)
  
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ChangeSpecExposureMeasure(self)->None:
        self.Spec_Ex_Time_Measure = int(self.ui.Ex_Time_Spec_measure.text())
        self.Ex_Time_Spec.insert(self.Spec_Ex_Time_Measure)
        self.ChangeSpecExposure()
    
    def ChangeAveragesMeasure(self)->None:
        if hasattr(self, 'DisplayThread'):
            av = int(self.ui.Averages_measure.text())
            if av >=1:
                self.disp_avgs = av
                self.DisplayThread.no_of_avgs_ghost = self.disp_avgs
                self.ui.Averages_run.clear()
                self.ui.Averages_run.insert(str(self.disp_avgs))
            
    def ChangeIntSample(self)->None:
        self.Sampling_start = self.Sampling_Home + int(self.ui.samp_int_t.text()) # in as
        
    def ChangeStepsSample(self)->None:
        self.ui.Steps_Spec.clear()
        self.ui.Steps_Spec.insert(self.ui.samp_steps.text())
        self.MeasureSampSteps = int(self.ui.samp_steps.text())
        self.RunSampSteps = int(self.ui.Steps_Spec.text())
        
    def ChangeSizeSample(self)->None:
        self.ui.Sampling_Inc_Delay_2.clear()
        self.ui.Sampling_Inc_Delay_2.insert(self.ui.samp_size.text())
        self.MeasureSampSize = int(self.ui.samp_size.text())
        self.inc = -int(self.toNanomtr(float(self.ui.Sampling_Inc_Delay_2.text()))) # as forwards in t is back for attocube
        
    def ChangeSweepsSample(self)->None:
        self.Sampling_sweeps = int(self.ui.samp_sweeps.text())
        
    def StartMeasuring(self)->None:
        self.ChangeIntSample()
        self.ChangeStepsSample()
        self.ChangeSizeSample()
        self.ChangeSweepsSample()
        if hasattr(self, 'DisplayThread'):
            self.DisplayThread.emit_a_line = False
            self.DisplayThread.emit_a_spot = False
            self.DisplayThread.emit_ghost = False
            self.DisplayThread.emit_a_fund = False
            self.DisplayThread.emit_spot = False
            self.DisplayThread.emit_on = False
            self.DisplayThread.emit_off = False
        self.Running = False
        self.Measuring = True
        self.ui.Measure_Start.setStyleSheet('color:green')
        self.ui.Live_Ghost.setStyleSheet('color:black') 
        self.ui.Live_Line_2.setStyleSheet('color:black') 
        self.ui.Live_on_off.setStyleSheet('color:black')
        # go to start location
        if hasattr(self, 'RefThread'):      
            if self.RefThread.GoStart():
                pass
            else:
                print('Error, stage not able to go to the start position')
        else:
            print('Stage not referenced')
        if self.ui.measure_spec_on.isChecked():
            self.ChangeSpecExposureMeasure()
            self.SetWavelengthRange()
            self.MeasureTSSpec()
        if self.ui.measure_line_on.isChecked():
            self.ChangeAveragesMeasure()
            self.ChangeRegion()
            self.IntegrationState()
            if self.ui.Test_Sampling_Mode.isChecked() and self.lines == 4:
                self.Measurement_Data = np.empty((self.Sampling_sweeps, self.MeasureSampSteps)) # sweeps, steps
                self.Measurement_Times = np.empty((self.Sampling_sweeps, self.MeasureSampSteps))
                self.Ghost_line_data = np.zeros((self.RunSampSteps))
                if self.ui.Fund_Plot.isChecked():
                    self.Fund_line_data = np.zeros((self.RunSampSteps))
                    self.Measurement_Fund = np.empty((self.Sampling_sweeps, self.MeasureSampSteps)) 
                self.MeasureTSLine()
            elif self.ui.Pump_Test_Sampling_Mode.isChecked() and self.lines == 8:
                self.Measurement_Data = np.empty((self.Sampling_sweeps, 3, self.MeasureSampSteps)) # sweeps, option, steps
                self.Measurement_Times = np.empty((self.Sampling_sweeps, 3, self.MeasureSampSteps)) 
                self.MeasurePTSLine()
            else:
                print('Error: are the choppers configured for this measurement mode!?')
                
    def MeasureTSLine(self)->None:
        print('measuring TS')
        self.pathfile = self.Path +'\\'+ self.Name +'_GHOSTdata.dat'
        self.pathfile2 = self.Path +'\\'+ self.Name +'_GHOSTtimepoints.dat'
        self.pathfile3 = self.Path +'\\'+ self.Name +'_GHOSTfundamentals.dat'
        self.head  =  str(self.MeasureSampSize)
        if self.Running:
            self.Running = False
        self.sweep_counter = 0
        self.step_counter = 0
        self.DisplayThread.emit_spot = True
        if self.ui.Fund_Plot.isChecked():
            self.DisplayThread.emit_a_fund = True
        self.ui.Live_Ghost.setStyleSheet('color:green') 

    def MeasurePTSLine(self)->None:
        print('measuring PTS')
        self.DisplayThread.emit_spot = True
        if self.Running:
            self.Running = False
        
    def MeasureTSSpec(self)->None:
        print('to measure TS')
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def ResetFG(self)->None:
        if hasattr(self,'DisplayThread'):
            self.DisplayThread.LineCameraAcq.cleanup_framegrabber = True
    
    def closeEvent(self, event)->None:
        if hasattr(self,'DisplayThread'):
            self.DisplayThread.LineCameraAcq.cleanup_framegrabber = True
        if hasattr(self,'UpdateSpec'):
            self.UpdateSpec.live = False
        CC.closeSerial()
        TD.closeThor()
        event.accept()

# TODO:
    # when num and denom are changed re load the connection to line camera
    # when pump or test choppers turned off re load the connection to the line camera
    # Connect the continuous atto, thor move buttons
    # Connect the freeze and defrost buttons
    # Connect the measurment save params
    # function for doing measuremnt and saving it
    # add in sweeps
    # as running spectrometer update location
    # actual and target frequencies of GHOSt anad SHG on FFT plot
    # go to ref thread
    # move display connect finds into display class init       
    

class LiveSpectrometer(QtCore.QThread):
    line_done = False
    Spec = QtCore.pyqtSignal(np.ndarray)
    def __init__(self, live):
        super().__init__()
        self.live = live
        
    def run(self):
        # live spectrometer
        while self.live:
            self.Spec.emit(GS.get_spectrum())

    
class FindReference(QtCore.QThread):
    found = False
    def __init__(self, axis):
        super().__init__()
        self.axis = axis
        
    def run(self):
        if ATC.findReference(self.axis):
            found = True
            thisapp.ui.Find_Ref_Samp.setStyleSheet('color:green')
            thisapp.ui.Sampling_Delay.display(thisapp.toAtto(ATC.getLocation(1)))
            thisapp.samp_ref  = ATC.getRefPos(1)
            ATC.setTarget(1,0)
            ATC.dev.control.setControlFrequency(1, 99000)
            print(ATC.getFreq(1))

    def GoStart(self):
        if ATC.isReferenced(self.axis):
            ATC.setTarget(self.axis, (thisapp.toNanomtr(thisapp.Sampling_start)) )
            ATC.startMove(self.axis)
            while ATC.isMoving(self.axis):
                pass
            thisapp.ui.Sampling_Delay.display(thisapp.toAtto(ATC.getLocation(1)) -thisapp.Sampling_Home)
            return True
        else:
            return False
        
    # def Move(self):
        


class LineCameraDisplay(QtCore.QThread):
    Ghost_avg = QtCore.pyqtSignal(np.ndarray)
    Fund_avg = QtCore.pyqtSignal(np.ndarray)
    Spot = QtCore.pyqtSignal(np.ndarray)
    Line_avg = QtCore.pyqtSignal(np.ndarray)
    A_spot = QtCore.pyqtSignal(np.float64)
    On_phase = QtCore.pyqtSignal(np.ndarray)
    Off_phase = QtCore.pyqtSignal(np.ndarray)
    def __init__(self,no_of_avg_ghost, pumper_on, laser_on, line_factor):
        super().__init__()
        self.emit_ghost = False
        self.emit_a_fund = False
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
        self.min = 710
        self.max = 760
        self.red_min = 210
        self.red_max = 260
        self.new_img_no = 0
        self.old_img_no = 0
        self.pixels= 2048
        self.h_line_stack = np.zeros((self.lines_per_img, self.pixels))
        self.test_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.test_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.test_on_pump_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.test_on_pump_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.test_off_pump_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.test_off_pump_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.one = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.two = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.three = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.four = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.five = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.six = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2))) 
        self.seven = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.eight = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
        self.avg_line = np.zeros((int(self.max-self.min)))
        self.line_spot = 0.
        if self.lines_per_img == 4:
            self.avg_on = np.zeros((int(self.pixels/2)))
            self.avg_off = np.zeros((int(self.pixels/2)))
            self.avg_ghost  = np.zeros((int(self.max-self.min)))
            self.avg_fund = np.zeros((int(self.red_max-self.red_min)))
            self.avg_spot = np.zeros((1))
        if self.lines_per_img == 8:
            self.avg_on = np.zeros((8))
            self.avg_off = np.zeros((8)) 
            self.avg_ghost  = np.zeros((3,int(self.max-self.min)))
            self.avg_fund = np.zeros((3,int(self.red_max-self.red_min)))
            self.avg_spot = np.zeros((3))

    def run(self):
        self.LineCameraAcq = GC.LineCameraAquisition(self.pump_on, self.laser_on, self.lines_per_img )
        self.LineCameraAcq.start()
        while not self.LineCameraAcq.cleanup_framegrabber:
            # analysis and manipulation of aqu array
            self.counter = 0
            while self.counter < self.no_of_avgs_ghost:
                #Catch a change in the number of averages disp class
                if self.no_of_avgs_ghost != np.shape(self.test_on)[0]:
                    self.test_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.test_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.test_on_pump_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.test_on_pump_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.test_off_pump_on = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.test_off_pump_off = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                                                      
                    self.one = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.two = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.three = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.four = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.five = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.six = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.seven = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                    self.eight = np.zeros((self.no_of_avgs_ghost,int(self.pixels/2)))
                # get image in
                self.h_line_stack = self.LineCameraAcq.data_block
                # pixel overflow
                if self.lines_per_img == 4:
                    self.test_on[self.counter,:] = np.mean(self.h_line_stack[:int(self.lines_per_img/2),1::2]*2**8 + self.h_line_stack[:int(self.lines_per_img/2),0::2], axis = 0)
                    self.test_off[self.counter,:] = np.mean(self.h_line_stack[int(self.lines_per_img/2):,1::2]*2**8 + self.h_line_stack[int(self.lines_per_img/2):,0::2], axis = 0)
                if self.lines_per_img == 8:
                    self.test_on_pump_on[self.counter,:] = np.mean(self.h_line_stack[:int(self.lines_per_img/4),1::2]*2**8 + self.h_line_stack[:int(self.lines_per_img/4),0::2], axis = 0)
                    self.test_off_pump_on[self.counter,:] = np.mean(self.h_line_stack[int(self.lines_per_img/4):2*int(self.lines_per_img/4),1::2]*2**8 + self.h_line_stack[int(self.lines_per_img/4):2*int(self.lines_per_img/4),0::2], axis = 0)
                    self.test_on_pump_off[self.counter,:] = np.mean(self.h_line_stack[2*int(self.lines_per_img/4):3*int(self.lines_per_img/4),1::2]*2**8 + self.h_line_stack[2*int(self.lines_per_img/4):3*int(self.lines_per_img/4),0::2], axis = 0)
                    self.test_off_pump_off[self.counter,:] = np.mean(self.h_line_stack[3*int(self.lines_per_img/4):4*int(self.lines_per_img/4),1::2]*2**8 + self.h_line_stack[3*int(self.lines_per_img/4):4*int(self.lines_per_img/4),0::2], axis = 0)
                    
                    self.one[self.counter,:] = (self.h_line_stack[0,1::2]*2**8 + self.h_line_stack[0,0::2])
                    self.two[self.counter,:] = (self.h_line_stack[1,1::2]*2**8 + self.h_line_stack[1,0::2])
                    self.three[self.counter,:] = (self.h_line_stack[2,1::2]*2**8 + self.h_line_stack[2,0::2])
                    self.four[self.counter,:] =  (self.h_line_stack[3,1::2]*2**8 + self.h_line_stack[3,0::2])
                    self.five[self.counter,:] = (self.h_line_stack[4,1::2]*2**8 + self.h_line_stack[4,0::2])
                    self.six[self.counter,:] = (self.h_line_stack[5,1::2]*2**8 + self.h_line_stack[5,0::2])
                    self.seven[self.counter,:] = (self.h_line_stack[6,1::2]*2**8 + self.h_line_stack[6,0::2])
                    self.eight[self.counter,:] =  (self.h_line_stack[7,1::2]*2**8 + self.h_line_stack[7,0::2])
                
                self.counter +=1
            # signal emitted from here if the bools allow ->needs if statements from app class
            # then do the averaging for the ons and off
            if self.lines_per_img == 4:
                if self.emit_ghost:
                    self.avg_ghost = np.mean((self.test_on - self.test_off )/ self.test_off**(0.75) , axis=0)
                    self.Ghost_avg.emit(self.avg_ghost)
                if self.emit_spot:
                    self.avg_spot = np.mean( np.mean((self.test_on - self.test_off )/ self.test_off**(0.75) , axis=0)[int(self.min):int(self.max)], axis=0)
                    self.Spot.emit(np.array(self.avg_spot))
                if self.emit_a_fund:
                    self.avg_fund = np.mean( np.mean(((self.test_on -self.test_off )/self.test_off) , axis=0)[int(self.red_min):int(self.red_max)],axis=0)
                    self.Fund_avg.emit(np.array(self.avg_fund))
                if self.emit_a_line:
                    self.avg_line = np.mean((self.test_on + self.test_off)/2, axis=0)
                    self.Line_avg.emit(self.avg_line)
                if self.emit_a_spot:
                    self.line_spot = np.mean(np.mean((self.test_on + self.test_off)/2, axis=0)[int(self.min):int(self.max)], axis=0)
                    self.A_spot.emit(self.line_spot)
                if self.emit_on:
                    self.avg_on = np.mean(self.test_on , axis=0)
                    self.On_phase.emit(self.avg_on)
                if self.emit_off:
                    self.avg_off = np.mean(self.test_off , axis=0)
                    self.Off_phase.emit(self.avg_off)
            if self.lines_per_img == 8:
                if self.emit_ghost:
                    self.avg_ghost_gs = np.mean(((self.test_on_pump_off - self.test_off_pump_off )/ self.test_off_pump_off**(0.75)), axis=0)
                    # self.avg_ghost_es = np.mean((self.test_on_pump_on - self.test_off_pump_on )/ self.test_off_pump_on**(0.75) , axis=0)
                    self.avg_ghost_delta = np.mean((self.test_on_pump_on - self.test_off_pump_on )/ self.test_off_pump_on**(0.75) - ((self.test_on_pump_off - self.test_off_pump_off )/ self.test_off_pump_off**(0.75)), axis=0)
                    self.pump_probe = np.mean( (self.test_on_pump_on-self.test_on_pump_off)/self.test_on_pump_off, axis=0)
                    self.avg_ghost = np.vstack((self.avg_ghost_gs, self.avg_ghost_delta, self.pump_probe ))
                    self.Ghost_avg.emit(self.avg_ghost)
                if self.emit_spot:
                    self.avg_spot_gs = np.mean( np.mean( (self.test_on_pump_off - self.test_off_pump_off )/ self.test_off_pump_off**(0.75), axis=0)[int(self.min):int(self.max)], axis=0)
                    self.avg_spot_delta = np.mean( np.mean((self.test_on_pump_on - self.test_off_pump_on )/ self.test_off_pump_on**(0.75) - ((self.test_on_pump_off - self.test_off_pump_off )/ self.test_off_pump_off**(0.75)), axis=0)[int(self.min):int(self.max)] , axis=0)
                    self.pump_probe_spot = np.mean(np.mean((self.test_on_pump_on-self.test_on_pump_off)/self.test_on_pump_off, axis=0)[int(self.min):int(self.max)], axis=0)
                    self.avg_spot = np.vstack((self.avg_spot_gs, self.avg_spot_delta, self.pump_probe_spot))
                    self.Spot.emit(self.avg_spot)
                if self.emit_a_line:
                    self.avg_line = np.mean((self.test_on_pump_on + self.test_off_pump_on)/2 + (self.test_on_pump_off + self.test_off_pump_off)/2, axis=0)
                    self.Line_avg.emit(self.avg_line)
                if self.emit_a_spot:
                    self.line_spot = np.mean(np.mean((self.test_on_pump_on + self.test_off_pump_on)/2 + (self.test_on_pump_off + self.test_off_pump_off)/2, axis=0)[int(self.min):int(self.max)], axis=0)
                    self.A_spot.emit(self.line_spot)
                if self.emit_on:
                    # self.avg_on = np.mean((self.test_on_pump_on + self.test_on_pump_off)/2 , axis=0)
                    # self.On_phase.emit(self.avg_on)
                    self.avg_on = np.asarray([  np.mean(self.one[:,int(self.min):int(self.max)]), np.mean(self.two[:,int(self.min):int(self.max)]), np.mean(self.three[:,int(self.min):int(self.max)]), np.mean(self.four[:,int(self.min):int(self.max)]), np.mean(self.five[:,int(self.min):int(self.max)]), np.mean(self.six[:,int(self.min):int(self.max)])  , np.mean(self.seven[:,int(self.min):int(self.max)]), np.mean(self.eight[:,int(self.min):int(self.max)])  ])
                    self.On_phase.emit(self.avg_on)
                if self.emit_off:
                    self.avg_off = np.mean((self.test_off_pump_on + self.test_off_pump_off)/2, axis=0)
                    self.Off_phase.emit(self.avg_off)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())