# from pycromanager import Bridge
import os
import sys
import time
import numpy as np
import pyqtgraph as pg
# import breeze_resources
# import MercuryControl as MC
# import AttocubeController as AC
# import TAM_Phidgets3 as phidget
# import DLS_Interface as longdelay_cryo
# from scipy.interpolate import interp1d
# from pathlib import Path,PureWindowsPath
# import NewportNPCInterface as Z_controller
from Blunderscope_cryo_UI import Ui_MainWindow
# import Blunderscope_processing_functions as bpf
# import PI_shortstage_interface as PI_shortstage
from pyqtgraph.Qt import QtCore, QtGui,QtWidgets
# from SendSlackNotifs import SendSlackNotification
# import NewportESP301Interface as longdelay_highNA


# runfile('C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib/SiSoPyInterface.py', wdir='C:/Program Files/SiliconSoftware/Runtime5.4.3/SDKWrapper/PythonWrapper/python36/lib')

# import SiSoPyInterface as s

np.seterr(divide='ignore', invalid='ignore')

class App(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)
        #self.ui.centralwidget.setStyleSheet('background-color:black')
    
        file = QtCore.QFile(":/dark/stylesheet.qss")
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.ui.centralwidget.setStyleSheet(stream.readAll())
        
        "Initialise the diplay shots variabke"
        self.shots_to_avg_disp = 1
        self.ui.Shots_to_avg_display.insert(str(self.shots_to_avg_disp))
        
        self.TAM_Measurement_underway = False
        self.ui.Number_of_sweeps.insert(str(2))
        self.ui.Number_of_averages.insert(str(150))
        
        "Initialise Averaging for Fit variables"
        self.averages_dTT_fit = 100
        self.dk_guess = -0.5
        self.dn_guess = -0.5
        self.z_guess = 0
        self.SampleThickness = 100
        self.BandpassWavelength = 750
        self.SampleRI = 1.8
        self.sigma_guess = 150
        self.ui.DTT_fit_averages.insert(str(self.averages_dTT_fit))
        self.ui.DTT_dk_guess.insert(str(self.dk_guess))
        self.ui.DTT_dn_guess.insert(str(self.dn_guess))
        self.ui.DTT_sigma_guess.insert(str(self.sigma_guess))
        self.ui.DTT_z_guess.insert(str(self.z_guess))
        self.ui.BandpassWavelength.insert(str(self.BandpassWavelength))
        self.ui.SampleThickness.insert(str(self.SampleThickness))
        self.ui.SampleRI.insert(str(self.SampleRI))
        
        "Initialising Display parameters (set to 0!)"
        self.roi_size_camera = 512
        self.c_x =0
        self.c_y =0
        self.dx = 0
        self.dy = 0

        self.im_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.im_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        
        self.im_disp = np.zeros((self.shots_to_avg_disp,self.roi_size_camera,self.roi_size_camera))
        self.disp_counter = 0
        
        self.image_array_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_array_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_diff_norm = np.zeros((self.roi_size_camera,self.roi_size_camera))

        'Initialise the delays to zero'
        self.ui.CurrentDelay.setDigitCount(7)
        self.ui.CurrentDelay.display(0)
        self.ui.CurrentDelay_2.setDigitCount(7)
        self.ui.CurrentDelay_2.display(0)
        
        "Initialise the framegrabber for the spectrometer"
        self.ui.Shots_to_avg_display_spec.insert(str(150))
        self.no_of_avgs_spec = int(self.ui.Shots_to_avg_display_spec.text())
        
        "Setup view box for the DTT images"
        self.dTT_image_view = self.ui.DTT_image.addViewBox()
        self.dTT_image_view.setAspectLocked(True)
        self.dTT_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        
        "Setup view box for the DTT image slices"        
        self.dTT_image_section_plot = self.ui.DTT_Section.addPlot()
        
        "Setup view box for the static images"        
        self.static_image_view = self.ui.Thunder_Image.addViewBox()
        self.static_image_view.setAspectLocked(True)
        self.static_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
               
        "Setup view box for the pump on images"        
        self.pumpon_image_view = self.ui.DTT_image_on.addViewBox()
        self.pumpon_image_view.setAspectLocked(True)
        self.pumpon_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        
        "Setup view box for the pump off images"        
        self.pumpoff_image_view = self.ui.DTT_image_off.addViewBox()
        self.pumpoff_image_view.setAspectLocked(True)
        self.pumpoff_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        
        "Setup view box for the shots histogram"        
        self.ShotsHist_image_view = self.ui.Shots_Histogram.addPlot()
                
        "Setup view box for the spectrometer differential spectra"
        self.DTT_spec_plot = self.ui.DTT_spectrum.addPlot()
        self.DTT_spec_plot_spec = self.DTT_spec_plot.plot(clear=True)
        
        "Setup view box for the spectrometer static spectra counts"
        self.static_spec_plot = self.ui.Spectrum_counts.addPlot()
              
        "Setup view box for the calib snap"
        self.calib_snap = self.ui.Spectrum_Calib.addPlot()
        self.calib_snap_plot = self.calib_snap.plot(clear = False)
        self.calib_peak_line= pg.InfiniteLine(0,angle=90,movable=True)
        self.calib_snap.addItem(self.calib_peak_line,clear = False)     
        
        "Setup view box for the calib points and fit"
        self.spec_calib_plot= self.ui.CalibrationPlot.addPlot()
        self.spec_calib_plot_fit = self.spec_calib_plot.plot(clear = False)
        self.spec_calib_points = self.spec_calib_plot.plot(clear = False)        
                
        "Setup view box for the spectrometer static spectra statistics"
        self.static_statistics_spec_plot = self.ui.Spectrum_stats.addPlot()
        self.static_statistics_spec_plot.setLogMode(False, True)
        
        "Setup view box for the Thunder Snapped Image on the Spectrometer Tab"        
        self.ThunderSnapped_SpecTab_image_view = self.ui.Snapped_Image_Thunder_SpecTab.addViewBox()
        self.ThunderSnapped_SpecTab_image_view.setAspectLocked(True)
        self.ThunderSnapped_SpecTab_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))     
        
        "Default value for the ChopperPhase Threshold LineEdit"
        self.ui.Set_ChopperPhaseIntensity.insert(str(100))
        
        "Connect the ChopperPhase Shot NUmber LineEdit"
        self.ui.Set_NumberofShots.insert(str(100))
                
        "Setup dTT  image plot"
        self.img1 = pg.ImageItem(border='w')
        self.dTT_image_view.addItem(self.img1)
        
        "Setup histogram for dTT"
        self.ui.DTT_image.nextColumn()
        self.hist1 = pg.HistogramLUTItem(fillHistogram=False)
        self.hist1.setImageItem(self.img1)
        self.ui.DTT_image.addItem(self.hist1,0)
        
        "Setup static image plot"
        self.img2 = pg.ImageItem(border='w')
        self.static_image_view.addItem(self.img2)
        
        "Setup pump on plot"
        self.img_on = pg.ImageItem(border='w')
        self.pumpon_image_view.addItem(self.img_on)
        
        "Setup pump off plot"
        self.img_off= pg.ImageItem(border='w')
        self.pumpoff_image_view.addItem(self.img_off)
        
        "Setup histogram for static"
        self.ui.Thunder_Image.nextColumn()
        self.hist2 = pg.HistogramLUTItem(fillHistogram=False)
        self.hist2.setImageItem(self.img2)
        self.ui.Thunder_Image.addItem(self.hist2,0)
        
        "Setup ROI for Thunder dTT"
        self.roi = pg.ROI([self.roi_size_camera/4, self.roi_size_camera/4], [self.roi_size_camera/2, self.roi_size_camera/2])
        self.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.dTT_image_view.addItem(self.roi)
        self.roi.setZValue(10)  # make sure ROI is drawn above image
        
        "Setup histogram for pump_on"
        self.ui.DTT_image_on.nextColumn()
        self.hist1_on = pg.HistogramLUTItem(fillHistogram=False)
        self.hist1_on.setImageItem(self.img_on)
        self.ui.DTT_image_on.addItem(self.hist1_on,0)
    
        "Setup histogram for pump_off"
        self.ui.DTT_image_off.nextColumn()
        self.hist1_off = pg.HistogramLUTItem(fillHistogram=False)
        self.hist1_off.setImageItem(self.img_off)
        self.ui.DTT_image_off.addItem(self.hist1_off,0)
        
        "Setup the Thunder Static Snapped Image plot for Spectrometer"
        self.ThunderSnappedImage_forSpecTab = pg.ImageItem(border='w')
        self.ThunderSnapped_SpecTab_image_view.addItem(self.ThunderSnappedImage_forSpecTab)
        
        "Setup histogram for Thunder Static Snapped Image plot for Spectrometer"
        self.ui.Snapped_Image_Thunder_SpecTab.nextColumn()
        self.hist_snapped_Thunder_specTab = pg.HistogramLUTItem(fillHistogram=False)
        self.hist_snapped_Thunder_specTab.setImageItem(self.ThunderSnappedImage_forSpecTab)
        self.ui.Snapped_Image_Thunder_SpecTab.addItem(self.hist_snapped_Thunder_specTab)
        
        "initialise the global variables for thunder"
        self.flip_sign_i = 0
        self.pause =0
        self.averaging_index = 0
        self.display_averaging_index_thunder = 0
        self.Set_Center_Thunderbtn_state = False
        self.dTT_thunder_c_x = 0
        self.dTT_thunder_c_y = 0
        self.start_Calib_Chopper= False
        self.shots_counter = 0
        self.global_time_zero_highNAnewport = 0
        self.global_time_zero_shortstage = 0
        self.global_time_zero_cryo = 0
        
        "Initialise the Stage Variables"        
        # self.x_pos_stage = AC.return_x_position()
        # self.y_pos_stage = AC.return_y_position()        
        
        "Initialise x,y increment"
        self.ui.Set_increment_xy.insert(str(1000))
        self.ui.Set_increment_xy_3.insert(str(1000))
        
        "Initialise z increment"
        self.ui.Set_increment_z.insert(str(1))
        self.ui.Set_increment_z_3.insert(str(1))
  
        # "Find the z positioner current position on the high NA"
        # try:
        #     self.z_pos = Z_controller.return_z_position(0)
        # except:
        #      Z_controller.close()
        #      Z_controller.openport()
        #      self.z_pos = Z_controller.return_z_position(0)
             
        "initialise the on and off data to be zeros"
        self.dataon = self.image_array_on
        self.dataoff = self.image_array_off
#        self.data_diffnorm =  bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.image_diff_norm,self.roi_size_camera)

        "Connect the Thunder Live Button"
        self.ui.Thunder_Live.setCheckable(True)
        self.ui.Thunder_Live.clicked.connect(self.Display_Live_Thunder)
        self.ui.Thunder_Live.setChecked(False)
        
        "Connect the Thunder Live Button"
        self.ui.Thunder_static_Live.setCheckable(True)
        self.ui.Thunder_static_Live.clicked.connect(self.Display_Live_Thunder_static)
        self.ui.Thunder_static_Live.setChecked(False)
        
        "Connect the Thunder Roi Selection"
        self.ui.Set_ROI_Thunder.setCheckable(True)
        self.ui.Set_ROI_Thunder.clicked.connect(self.setcamroi_btnstate)
        
        "Connect the Thunder Reset ROI Button"
        self.ui.ReSet_ROI_Thunder.setCheckable(True)
        self.ui.ReSet_ROI_Thunder.clicked.connect(self.resetcamroi_btnstate)
        
        "Connect Thunder Flip Sign Button"
        self.ui.Flip_sign_Thunder.setCheckable(True)
        self.ui.Flip_sign_Thunder.clicked.connect(self.flipsign_btnstate)
        
        "Connect Thunder Flip Sign Button for Chopper"
        self.ui.Flip_sign_Thunder_2.setCheckable(True)
        self.ui.Flip_sign_Thunder_2.clicked.connect(self.flipsign_btnstate)
        
        "Connect Different DTT Sectioning Checkboxes"
        self.ui.Flip_sign_Thunder.setCheckable(True)
        self.ui.Flip_sign_Thunder.clicked.connect(self.flipsign_btnstate)
        
        "Connect the Exposure LineEdit ThunderTab"
        self.ui.Set_Exposure_Thunder.returnPressed.connect(self.ChangeExposure)
        
        "Connect the Exposure LineEdit Spectrometer Tab"
        self.ui.Set_Exposure_Thunder_2.returnPressed.connect(self.ChangeExposure_SnapThunder_SpectrometerTab)
        
        "Connect the Gain LineEdit"
        self.ui.Set_Gain_Thunder.returnPressed.connect(self.ChangeGain)
        
        "Connect the Shots to Avg and Display LineEdit"
        self.ui.Shots_to_avg_display.returnPressed.connect(self.ChangeShotstoAvg)
    
        "Connect the Gain LineEdit"
        self.ui.Set_Gain_Thunder.returnPressed.connect(self.ChangeGain)
        
        "Connect the delay entry for Thunder"
        self.ui.SetDelay.returnPressed.connect(self.MoveStage_ThunderTab)
        
        "Connect the delay entry for Spectrometer"
        self.ui.SetDelay_2.returnPressed.connect(self.MoveStage_SpectrometerTab)
        
        "Connect the set center Thunder Button"
        self.ui.Set_Center_Thunder.setCheckable(True)
        self.ui.Set_Center_Thunder.clicked.connect(self.Set_Center_Thunderbtn)
        
        "Connect the Fitting Button for Thunder"
        self.ui.DTT_Fit.setCheckable(True)
        self.ui.DTT_Fit.clicked.connect(self.Initialise_DTT_Averaging)
        self.ui.DTT_Fit.setChecked(False)
        
        "Connect the Mouse CLick for center selection in dTT"
        self.ui.DTT_image.scene().sigMouseClicked.connect(self.mouseClicked)
        
        "Connect the Mouse CLick for pixel selection in phase meas"
        self.ui.DTT_image_on.scene().sigMouseClicked.connect(self.mouseClicked_forPhase)
        
        "Fill in the x and y positon LEDs ThunderTab"
       # self.ui.x_position_display.display(AC.return_x_position()/1000)
        self.ui.x_position_display.setStyleSheet("""QLCDNumber { background-color: green; color: white; }""")
        #self.ui.y_position_display.display(AC.return_y_position()/1000)
        self.ui.y_position_display.setStyleSheet("""QLCDNumber { background-color: green; color: white; }""")
        
        "Fill in the x and y positon LEDs SpectrometerTab"
        # self.ui.x_position_display_3.display(AC.return_x_position()/1000)
        # self.ui.x_position_display_3.setStyleSheet("""QLCDNumber { background-color: green; color: white; }""")
        # self.ui.y_position_display_3.display(AC.return_y_position()/1000)
        # self.ui.y_position_display_3.setStyleSheet("""QLCDNumber { background-color: green; color: white; }""")
        
        "Fill in the z voltage LED  ThunderTab"
        #self.ui.z_voltage_display.display(self.z_pos) 
        #self.ui.z_voltage_display.setStyleSheet("""QLCDNumber { background-color: blue; color: white; }""")
        
        "Fill in the z voltage LED SpecTab"
        #self.ui.z_voltage_display_3.display(self.z_pos) 
        #self.ui.z_voltage_display_3.setStyleSheet("""QLCDNumber { background-color: blue; color: white; }""")
        
        "Connect the Lareral Movement Buttons ThunderTab"
        self.ui.Atto_up.clicked.connect(self.Move_Attocube_Up_Thunder)
        self.ui.Atto_down.clicked.connect(self.Move_Attocube_Down_Thunder)
        self.ui.Atto_left.clicked.connect(self.Move_Attocube_Left_Thunder)
        self.ui.Atto_right.clicked.connect(self.Move_Attocube_Right_Thunder)
        
        "Connect the Lareral Movement Buttons SpectrometerTab"
        self.ui.Atto_up_3.clicked.connect(self.Move_Attocube_Up_Spec)
        self.ui.Atto_down_3.clicked.connect(self.Move_Attocube_Down_Spec)
        self.ui.Atto_left_3.clicked.connect(self.Move_Attocube_Left_Spec)
        self.ui.Atto_right_3.clicked.connect(self.Move_Attocube_Right_Spec)
        
        "Connect the Z-Positioner Buttons ThunderTab"        
        self.ui.Nanopositioner_down.clicked.connect(self.Move_Z_Nanopositioner_Down_Thunder)
        self.ui.Nanopositioner_up.clicked.connect(self.Move_Z_Nanopositioner_Up_Thunder)
        
        "Connect the Z-Positioner Buttons SpectrometerTab"        
        self.ui.Nanopositioner_down_3.clicked.connect(self.Move_Z_Nanopositioner_Down_Spec)
        self.ui.Nanopositioner_up_3.clicked.connect(self.Move_Z_Nanopositioner_Up_Spec)
           
        "Connect the Chopper Phase Calib Live Button"
        self.ui.Start_Chopper_Phase_Calib.setCheckable(True)
        self.ui.Start_Chopper_Phase_Calib.clicked.connect(self.StartChopperCalib)
        self.ui.Start_Chopper_Phase_Calib.setChecked(True)
        
        "Connect the Chopper Phase Calib Live Button"
        self.ui.MeasureShots.setCheckable(True)
        self.ui.MeasureShots.clicked.connect(self.StartChopperHistogramCalib)
        
        "Connect the Plot Residue Button Button"
        self.ui.Plot_residuals.setCheckable(True)
        self.ui.Plot_residuals.clicked.connect(self.DisplayResiduals)
        self.ui.Plot_residuals.setChecked(False)
        
        "Connect the Plot Averages Button Button"
        self.ui.Plot_average.setCheckable(True)
        self.ui.Plot_average.clicked.connect(self.DisplayAverage)
        self.ui.Plot_average.setChecked(False)
        
        "Set Fitting Progress Bar to Zero"
        self.ui.FittingProgressBar.setValue(0*100)
        
        "Connect the buttons for the stage motion incrmeents Thunder"
        self.ui.Increment_time_positive.clicked.connect(self.IncrementDelayStagePos_ThunderTab)
        self.ui.Increment_time_negative.clicked.connect(self.IncrementDelayStageNeg_ThunderTab)      
        
        "Connect the buttons for the stage motion incrmeents Spectromerer"
        self.ui.Increment_time_positive_2.clicked.connect(self.IncrementDelayStagePos_SpectrometerTab)
        self.ui.Increment_time_negative_2.clicked.connect(self.IncrementDelayStageNeg_SpectrometerTab)
        
        "Initialise the increment value Thunder"
        self.ui.Set_increment_delay.insert(str(200))
        
        "Initialise the increment value Spec"
        self.ui.Set_increment_delay_2.insert(str(200))
        
        "Connect the Define Home Button for Thunder"
        self.ui.Define_home.clicked.connect(self.DefineHome_Thunder)
        
        "Connect the Define Home Button for Spectrometer"
        self.ui.Define_home_2.clicked.connect(self.DefineHome_Spec)
        
        'Connect the pump phidget button for Thunder'
        self.ui.PumpShutter.setCheckable(True)
        self.ui.PumpShutter.clicked.connect(self.ShutterPump)
        self.ui.PumpShutter.setChecked(False)
        
        'Connect the pump phidget button for Spectrometer'
        self.ui.PumpShutter_2.setCheckable(True)
        self.ui.PumpShutter_2.clicked.connect(self.ShutterPump_2)
        self.ui.PumpShutter_2.setChecked(False)
        
        'Connect the probe phidget button for Thunder'
        self.ui.ProbeShutter.setCheckable(True)
        self.ui.ProbeShutter.clicked.connect(self.ShutterProbe)
        self.ui.ProbeShutter.setChecked(False)       
        
        'Connect the probe phidget button for Spectrometer'
        self.ui.ProbeShutter_2.setCheckable(True)
        self.ui.ProbeShutter_2.clicked.connect(self.ShutterProbe_2)
        self.ui.ProbeShutter_2.setChecked(False)     
        
        'Connect the redWL phidget button for Thunder'
        self.ui.NIR_Stage_Shutter.setCheckable(True)
        self.ui.NIR_Stage_Shutter.clicked.connect(self.ShutterNIR)
        self.ui.NIR_Stage_Shutter.setChecked(False)
        
        'Connect the redWL phidget button for Spectrometer'
        self.ui.NIR_Stage_Shutter_2.setCheckable(True)
        self.ui.NIR_Stage_Shutter_2.clicked.connect(self.ShutterNIR_2)
        self.ui.NIR_Stage_Shutter_2.setChecked(False)
        
        'Connect the visWL phidget button for Thunder'
        self.ui.Vis_Stage_Shutter.setCheckable(True)
        self.ui.Vis_Stage_Shutter.clicked.connect(self.ShutterVis)
        self.ui.Vis_Stage_Shutter.setChecked(False)
        
        'Connect the visWL phidget button for Spectrometer'
        self.ui.Vis_Stage_Shutter_2.setCheckable(True)
        self.ui.Vis_Stage_Shutter_2.clicked.connect(self.ShutterVis_2)
        self.ui.Vis_Stage_Shutter_2.setChecked(False)
        
        'Connect the blueWL phidget button for Thunder'
        self.ui.Blue_Stage_Shutter.setCheckable(True)
        self.ui.Blue_Stage_Shutter.clicked.connect(self.ShutterBlue)
        self.ui.Blue_Stage_Shutter.setChecked(False)
        
        'Connect the blueWL phidget button for Spectrometer'
        self.ui.Blue_Stage_Shutter_2.setCheckable(True)
        self.ui.Blue_Stage_Shutter_2.clicked.connect(self.ShutterBlue_2)
        self.ui.Blue_Stage_Shutter_2.setChecked(False)
        
        "Connect the Live Spectrometer Differential Button"
        self.ui.Spectrometer_DTT_Live.setCheckable(True)
        self.ui.Spectrometer_DTT_Live.clicked.connect(self.Spectrometer_live_dtt)
        self.ui.Spectrometer_DTT_Live.setChecked(False)
        
        "Connect the Live Spectrometer Spectrum Button"
        self.ui.Spectrometer_Spectrum_Live.setCheckable(True)
        self.ui.Spectrometer_Spectrum_Live.clicked.connect(self.Spectrometer_live_static)
        self.ui.Spectrometer_Spectrum_Live.setChecked(False)
        
        "Connect the Spectrometer Freeze Button"
        self.ui.Spectrometer_Freeze.setCheckable(True)
        self.ui.Spectrometer_Freeze.setChecked(False)
        
        "Connect the Spectrometer Freeze ClearAll Button"
        self.ui.Spectrometer_Freeze_ClearAll.setCheckable(True)
        self.ui.Spectrometer_Freeze_ClearAll.setChecked(False)
        
        "Connect the shot clock for the spectrometer"
        self.ui.Shots_to_avg_display_spec.returnPressed.connect(self.ChangeNumberOfShots_Spec)
        
        "Connect the Camera Acquisition Button"
        self.ui.Thunder_Acquisition.setCheckable(True)
        self.ui.Thunder_Acquisition.clicked.connect(self.ToggleCameraAcq)
        self.ui.Thunder_Acquisition.setChecked(False)
        
        "Connect the Spectrometer Acquisition Button"
        self.ui.Spectrometer_Acquisition.setCheckable(True)
        self.ui.Spectrometer_Acquisition.clicked.connect(self.ToggleSpectrometerAcq)
        self.ui.Spectrometer_Acquisition.setChecked(False)
        
        "Connect the Thunder Snap Image Button"
        self.ui.Thunder_Snap_SpecTab.setCheckable(True)
        self.ui.Thunder_Snap_SpecTab.clicked.connect(self.ThunderSnapSpecTab)
        self.ui.Thunder_Snap_SpecTab.setChecked(False)
        
        'Connect the epoch selector'
        self.ui.Set_Number_of_Epochs.returnPressed.connect(self.Setup_timefile)
        self.ui.Set_Number_of_Epochs_2.returnPressed.connect(self.Setup_timefile_2)
        
        'Connect the Add Epoch Button'
        self.ui.Add_Epoch.setCheckable(True)
        self.ui.Add_Epoch.clicked.connect(self.Add_Epoch)
        self.ui.Add_Epoch.setChecked(False)
        self.ui.Add_Epoch_2.setCheckable(True)
        self.ui.Add_Epoch_2.clicked.connect(self.Add_Epoch_2)
        self.ui.Add_Epoch_2.setChecked(False)
        
        'Connect the TAM Measurement Button'
        self.ui.Start_Measurement_2.setCheckable(False)
        self.ui.Start_Measurement_2.clicked.connect(self.Measure_Spectra)
        
        'Connect the TA Measurement Button'
        self.ui.Start_Measurement.setCheckable(False)
        self.ui.Start_Measurement.clicked.connect(self.Measure_TAM)
        
        'Connect the LoadTimeFile Button'
        self.ui.Load_Timefile.clicked.connect(self.Load_TimeFile)
        
        'Connect the SaveTimeFile Button'
        self.ui.Save_Timefile.clicked.connect(self.Save_TimeFile)

        'Connect the LoadTimeFile Button'
        self.ui.Load_Timefile_2.clicked.connect(self.Load_TimeFile_2)
        
        'Connect the SaveTimeFile Button'
        self.ui.Save_Timefile_2.clicked.connect(self.Save_TimeFile_2)

        'Setup the spec measurement button'
        self.Spec_Measurement_underway =False       
        
        'Connect the Spectrometer Specturm Calib Live Button'
        self.ui.SpectrumSnapCalib.setCheckable(True)
        self.ui.SpectrumSnapCalib.clicked.connect(self.SpecCalibSnap)
        self.ui.SpectrumSnapCalib.setChecked(False)
        
        'Connect the FindPeak  button for the Spectreometer Calib'
        self.ui.FindPeak.clicked.connect(self.SpecCalibFindPeak)
        
        'Connect the AddPoint button for the Spectrometer Calib'
        self.ui.AddPointtoCalib.clicked.connect(self.SpecCalibAddpoint)
        
        'Connect the LoadCalib button for the Spectrometer Claib'
        self.ui.LoadCalib.clicked.connect(self.SpecCalibLoadFile)
        
        'Connect the SaveCalib button for the Spectrometer Claib'
        self.ui.SaveCalib.clicked.connect(self.SpecCalibSaveFile)
        
        'Connect the Calibrate Button for the Spectrometer Calib'
        self.ui.FitCalibrationCurve.clicked.connect(self.SpecCalibFitCalib)
        self.calib_wavelengths =[]
        self.calib_pixels = []
        
        "Connect the open z button"
        self.ui.OpenZ.setCheckable(True)
        self.ui.OpenZ.clicked.connect(self.OpenZPositioner)
        self.ui.OpenZ.setChecked(False)
        self.ui.OpenZ.setStyleSheet('color:red')
        
        "Connect the Position button"
        self.ui.Load_PositionFile.clicked.connect(self.Load_PositionFile)
        
        "Connect the powermeter positioning buttons"
        self.ui.Power_meter_increase.clicked.connect(self.Power_meter_increase)
        self.ui.Power_meter_decrease.clicked.connect(self.Power_meter_decrease)
        self.power_meter_pos = 70
        self.ui.power_meter_display.display(self.power_meter_pos)
        
        "Connect the powerwheel positioning buttons"
        self.ui.Power_wheel_increase.clicked.connect(self.Power_wheel_increase)
        self.ui.Power_wheel_decrease.clicked.connect(self.Power_wheel_decrease)
        self.power_wheel_pos = 100
        self.ui.power_wheel_display.display(self.power_wheel_pos)
        
        "Connect the FFT_Filter button"
        self.ui.Set_FFT_Filter.setCheckable(True)
        self.ui.Set_FFT_Filter.clicked.connect(self.FFT_Filter)
        self.ui.FFT_filter_radius.returnPressed.connect(self.Set_FTT_Filter_radius)
        self.FFT_Filter_radius = 11
        
        "Connect the FFT_Filter button"
        self.ui.Load_time_zero.clicked.connect(self.Load_time_zero)
        
        "For the Cryo Control Page: "
        "Setup view box for the temp-time plot "
        self.TempTime_plot = self.ui.Temp_Time.addPlot(labels =  {'left':'Temp', 'bottom':'Time'})
        self.TempTime_line = self.TempTime_plot.plot()
        
        "Setup view box for the temp-time plot "
        self.FlowTime_plot = self.ui.Flow_Time.addPlot(labels =  {'left':'Flow', 'bottom':'Time'})
        self.FlowTime_line= self.FlowTime_plot.plot()
        
        "Setup view box for the temp-time plot "
        self.HeatTime_plot = self.ui.Heat_Time.addPlot(labels =  {'left':'Heater Voltage', 'bottom':'Time'})
        self.HeatTime_line = self.HeatTime_plot.plot()

        "Connect the push button for the Live display "
        self.ui.Live_cryo.setCheckable(True)
        self.ui.Live_cryo.clicked.connect(self.DisplayLiveCryoSpectrum)
        self.ui.Live_cryo.setChecked(False)
        
        "Connect the SetPoint "
        self.ui.Set_SetPoint.returnPressed.connect(self.ChangeSetPoint)
        
        "Connect the FlowPoint "
        self.ui.Set_FlowPoint.returnPressed.connect(self.ChangeFlowPoint)
        
        "Connect the HeatPoint "
        self.ui.Set_HeatPoint.returnPressed.connect(self.ChangeHeatPoint)
        
        "Connect the GFSF "
        self.ui.Set_GFSF.returnPressed.connect(self.ChangeGFSF)
        
        "Connect the Gear "
        self.ui.Set_Gear.returnPressed.connect(self.ChangeGear)
        
        "Connect the TVES "
        self.ui.Set_TVES.returnPressed.connect(self.ChangeTVES)
        
        "Connect the TES "
        self.ui.Set_TES.returnPressed.connect(self.ChangeTES)
        
        "Connect the P in PID "
        self.ui.Set_P.returnPressed.connect(self.ChangeP)
        
        "Connect the I in PID "
        self.ui.Set_I.returnPressed.connect(self.ChangeI)
        
        "Connect the D in PID "
        self.ui.Set_D.returnPressed.connect(self.ChangeD)

        "Initialise LCD screens "
        # p, u = MC.gas.gfsf
        # self.ui.Current_GFSF.display(float(p))
        # p1, u1 = MC.gas.gear
        # self.ui.Current_GEAR.display(float(p1))
        # p2, u2 = MC.gas.tes
        # self.ui.Current_GEAR.display(float(p2))
        # p3, u3 = MC.gas.tves
        # self.ui.Current_GEAR.display(float(p3))
        # tr = 0.0
        # ts = 0.0
        # h = 0.0
        # self.ui.Current_RoomTemp.display(tr)
        # self.ui.Current_SurfaceTemp.display(0)
        # self.ui.Current_Humidity.display(h)
        # td = tr -22 + 0.2*h
        # self.ui.Current_DewTemp.display(td)
        # if td < ts:
        #     self.ui.Current_DewTemp.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
        
        "Start infinite loop"
        self._update()
        
    "Define the update function"
    def _update(self):
        if self.ui.Thunder_Live.isChecked() and not self.TAM_Measurement_underway:
            if self.shots_to_avg_disp > 50:
                self.ui.progressBar_displayshots.setValue((self.disp_counter + 1)/self.shots_to_avg_disp*100)
            else:
                self.ui.progressBar_displayshots.setValue(0)
        else:
            self.ui.progressBar_displayshots.setValue(0)
            
        if self.pause == 1:
            time.sleep(100e-3)
            self.pause = 0

        "Pull consecutive images and subtract and normalise if the acquisition in on"
        if self.ui.Thunder_Acquisition.isChecked() and hasattr(self,'core') and not self.TAM_Measurement_underway:
            self.dataon =  bpf.produce_consecutive_flattened_images(self.core,self.dataon,self.dataoff,self.flip_sign_i )[0]
            self.dataoff =  bpf.produce_consecutive_flattened_images(self.core,self.dataon,self.dataoff,self.flip_sign_i )[1]
            self.data_diffnorm =  bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.data_diffnorm,self.roi_size_camera)
            self.im_disp[self.disp_counter,:]=self.data_diffnorm
            self.data_staticnorm =  bpf.produce_norm_image( self.dataon, self.dataoff, self.data_diffnorm,self.roi_size_camera)
        
        self.disp_counter +=1
        
        "Set image to the current one"
        if self.disp_counter == self.shots_to_avg_disp:
            if  self.ui.Thunder_Acquisition.isChecked() and self.ui.Thunder_Live.isChecked() and not self.DisplayResiduals() and not self.DisplayAverage() and not self.TAM_Measurement_underway:
                if self.FFT_Filter():
                    self.img_forFFT =np.mean(self.im_disp,axis = 0)
                    self.img_FFT = np.fft.fftshift(np.fft.fft2(self.img_forFFT))
                    self.center_FFT=(int(self.img_forFFT.shape[0]/2),int(self.img_forFFT.shape[1]/2)) # center of spectrum should be (64,64) otherwise use find_max
                    self.img_LowPassCenter = self.img_FFT*bpf.butterworthLP(self.FFT_Filter_radius,self.img_forFFT.shape,4,self.center_FFT)
                    self.img_inverse_LowPass = np.fft.ifft2(np.fft.ifftshift(self.img_LowPassCenter))
                    self.imagetoshow = np.real(self.img_inverse_LowPass)
                else:
                    self.imagetoshow = np.mean(self.im_disp,axis = 0)
                self.img1.setImage(self.imagetoshow)
                "Set the cross-section of DDT"
                self.roi_crosssection = self.roi.getArrayRegion(self.imagetoshow, self.img1)
                
                if self.ui.Vertical_avg_box.isChecked() == True:
                    self.live_dTT = self.dTT_image_section_plot.plot(clear=True)
                    self.live_dTT.setData(np.mean(self.roi_crosssection,axis=1))
                if self.ui.Horizontal_avg_box.isChecked() == True:
                    self.live_dTT = self.dTT_image_section_plot.plot(clear=True)
                    self.live_dTT.setData(np.mean(self.roi_crosssection,axis=0))
                if self.ui.Radial_avg_box.isChecked() == True:
                    a,b = bpf.radial_profile(self.roi_crosssection, (-int(self.roi.pos()[1])+self.dTT_thunder_c_y,-int(self.roi.pos()[0])+self.dTT_thunder_c_x))
                    self.live_dTT = self.dTT_image_section_plot.plot(clear=True)
                    self.live_dTT.setData(np.append(-a[::-1],a),np.append(b[::-1],b))
                if hasattr(self, 'avgs_temp'):
                    self.avg_DTT = self.dTT_image_section_plot.plot(clear = False)
                    self.roi_crosssection_avgs = self.roi.getArrayRegion( self.avgs_temp, self.img1)
                    if self.ui.Horizontal_avg_box.isChecked() == True:
                        self.avg_DTT.setData(np.mean(self.roi_crosssection_avgs,axis =0),pen=('r'))
                    if self.ui.Vertical_avg_box.isChecked() == True:
                        self.avg_DTT.setData(np.mean(self.roi_crosssection_avgs,axis =1),pen=('r'))
                    if self.ui.Radial_avg_box.isChecked() == True:
                        a_avg,b_avg = bpf.radial_profile(self.roi_crosssection_avgs, (-int(self.roi.pos()[1])+self.dTT_thunder_c_y,-int(self.roi.pos()[0])+self.dTT_thunder_c_x))
                        self.avg_DTT.setData(np.append(-a_avg[::-1],a_avg),np.append(b_avg[::-1],b_avg),pen=('r'))
           
            self.disp_counter = 0
            
        if self.ui.Thunder_static_Live.isChecked() and not self.TAM_Measurement_underway:
            self.img2.setImage(self.data_staticnorm)

        "Switch displayed image to residuals if the button is pressed"
        if self.DisplayResiduals() and not self.DisplayAverage() and not self.TAM_Measurement_underway:
            self.img1.setImage(self.ComputeResidues())
            
        "Switch displayed image to average if the button is pressed"
        if self.DisplayAverage() and hasattr(self,'fitted_output') and not self.DisplayResiduals() and not self.TAM_Measurement_underway:
            self.img1.setImage(self.fitted_output)
            
        "Set up the phase images"
        if self.StartChopperCalib():
            self.img_on.setImage(np.reshape(self.dataon,(self.roi_size_camera,self.roi_size_camera)))
            self.img_off.setImage(np.reshape(self.dataoff,(self.roi_size_camera,self.roi_size_camera)))

        "Setup averaging if the fitting button is pressed"
        if self.ui.DTT_Fit.isChecked() and not self.TAM_Measurement_underway:
            if self.averaging_index  == self.averages_dTT_fit:
                self.avgs_temp = self.DTT_FittingRoutine()
            self.avg_image_array_on[self.averaging_index,:] = self.dataon
            self.avg_image_array_off[self.averaging_index,:] = self.dataoff
            self.ui.FittingProgressBar.setValue(self.averaging_index/int(self.ui.DTT_fit_averages.text())*100)
            self.averaging_index +=1

        if self.start_Calib_Chopper== True and not self.TAM_Measurement_underway:
            if np.reshape(self.dataon,(self.roi_size_camera,self.roi_size_camera))[int(self.chopperphase_pix_x),int(self.chopperphase_pix_y)] > float(self.ui.Set_ChopperPhaseIntensity.text()):
                self.chopperphasehist[0]+=1
                print('on')
            if np.reshape(self.dataoff,(self.roi_size_camera,self.roi_size_camera))[int(self.chopperphase_pix_x),int(self.chopperphase_pix_y)] > float(self.ui.Set_ChopperPhaseIntensity.text()): 
                print('off')
                self.chopperphasehist[1]+=1
            self.shots_counter +=1
            if self.shots_counter > int(self.ui.Set_NumberofShots.text()):
                self.shots_counter = 0
                self.StartChopperHistogramCalib()
            self.ShotsHist_image_view.setYRange(0,int(self.ui.Set_NumberofShots.text()) ,padding=0)
            print(self.chopperphasehist)
            self.ShotsHist_image_view.plot(self.chopperphasehist,clear=True)
            
        if self.TAM_Measurement_underway:
            'Room Light Background block pump and probe'
            'Pre time zero PL background'
            if self.delaytimes.ndim > 1:
                self.delaytimes = self.delaytimes[0,:]
                self.dynamic_averaging = True
            
            if self.stage_moved is False:                    
                if  self.ui.HighNA_NewportStage_Box.isChecked() == True:
                    longdelay_highNA.MovetoTime(self.delaytimes[self.i_time ] +self.global_time_zero_highNAnewport)
                    while not longdelay_highNA.MotionDone():
                        pass
                    self.ui.CurrentDelay.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
                if self.ui.Cryo_NewportStage_Box.isChecked() == True:
                    longdelay_cryo.MovetoTime(self.delaytimes[self.i_time ] + self.global_time_zero_cryo)
                    self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
                    while not longdelay_cryo.MotionDone():
                        pass
                if self.ui.PIStage_Box.isChecked() == True:
                    PI_shortstage.MovetoTime(self.delaytimes[self.i_time ] +self.global_time_zero_shortstage)
                    self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
                    while not PI_shortstage.MotionDone():
                        pass
                self.stage_moved = True
                
            self.dataon =  bpf.produce_consecutive_flattened_images(self.core,self.dataon,self.dataoff,self.flip_sign_i )[0]
            self.dataoff =  bpf.produce_consecutive_flattened_images(self.core,self.dataon,self.dataoff,self.flip_sign_i )[1]
            self.data_diffnorm =  bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.data_diffnorm,self.roi_size_camera)
            self.im_meas_avg[self.i_avgs,:,:] = bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.data_diffnorm,self.roi_size_camera)
            self.im_meas_avg_on[self.i_avgs,:,:] = np.reshape(self.dataon,(self.roi_size_camera,self.roi_size_camera))
            self.im_meas_avg_off[self.i_avgs,:,:] = np.reshape(self.dataoff,(self.roi_size_camera,self.roi_size_camera))
            
            self.i_avgs +=1
            
            if hasattr(self,'dynamic_averaging'): #enter here if doing dynamic averaging
                if self.i_avgs == self.TAM_measurement_no_of_avgs_array[self.i_time]:
                    A=np.mean(self.im_meas_avg[:self.TAM_measurement_no_of_avgs_array[self.i_time],:,:],axis =0)
                    self.im_meas_data[self.i_sweep,self.i_time,:,:] = A
                    self.i_avgs = 0
                    self.stage_moved = False
                    if self.ui.Thunder_Live.isChecked():
                        self.img1.setImage(A)
                    print('Dyn Avg Sweep number = ',self.i_sweep, 'Timepoint = ', self.delaytimes[self.i_time], ' fs')
                    self.i_time +=1
                    self.ui.MeasurementProgressBar.setValue((self.i_time + 1)*(self.i_sweep+1)/(self.TAM_measurement_no_of_sweeps*self.TAM_measurement_no_of_timepoints)*100)

            else:#enter here normally
                if self.i_avgs == self.TAM_measurement_no_of_avgs:
                    self.im_meas_data[self.i_sweep,self.i_time,:,:] = np.mean(self.im_meas_avg,axis =0)
                    self.im_meas_data_on[self.i_sweep,self.i_time,:,:] = np.mean(self.im_meas_avg_on,axis =0)
                    self.im_meas_data_off[self.i_sweep,self.i_time,:,:] = np.mean(self.im_meas_avg_off,axis =0)
                    self.i_avgs = 0
                    self.stage_moved = False
                    if self.ui.Thunder_Live.isChecked():
                        self.img1.setImage(np.mean(self.im_meas_avg,axis =0))
                    print('Sweep number = ',self.i_sweep, 'Timepoint = ', self.delaytimes[self.i_time], ' fs')
                    self.i_time +=1
                    self.ui.MeasurementProgressBar.setValue((self.i_time + 1)*(self.i_sweep+1)/(self.TAM_measurement_no_of_sweeps*self.TAM_measurement_no_of_timepoints)*100)
                
            if self.i_time == self.TAM_measurement_no_of_timepoints:
                self.i_time =0
                self.i_avgs = 0
                self.stage_moved = False
                np.save(self.temp_path_measurement,self.im_meas_data)
                np.save(self.temp_path_measurement + '_ON',self.im_meas_data_on)
                np.save(self.temp_path_measurement + '_OFF',self.im_meas_data_off)
                np.save(self.temp_path_measurement + '_delaytimes',self.delaytimes)
                self.i_sweep+=1
                
            if self.i_sweep == self.TAM_measurement_no_of_sweeps:
                if hasattr(self,'measurement_positions'):#enter here if doing position scans
                    self.i_pos +=1
                    if self.i_pos == self.number_of_positions:
                        
                        self.ui.MeasurementProgressBar.setValue(0)
                        np.save(self.temp_path_measurement,self.im_meas_data_pos)
                        np.save(self.temp_path_measurement + '_delaytimes',self.delaytimes)
                        np.savetxt(self.temp_path_measurement + '_measuredpositions',self.measurement_positions_real)
                        self.TAM_Measurement_underway = False
                        self.ui.Start_Measurement.setStyleSheet('color:black')
                        self.ui.Load_PositionFile.setStyleSheet('color:black')
                        self.ui.Start_Measurement.setCheckable(False)
                        delattr(self, 'measurement_positions')
                        self.i_pos ==0
                    else:
                        self.im_meas_data_pos[self.i_pos,:,:,:,:] = self.im_meas_data
                        x_real = AC.return_x_position()
                        y_real = AC.return_y_position()
                        dx_pos = self.measurement_positions[self.i_pos,0]
                        dy_pos = self.measurement_positions[self.i_pos,1]
                        AC.move_x_position_incr(x_real + dx_pos)
                        AC.move_y_position_incr(y_real + dy_pos)
                        self.measurement_positions_real[self.i_pos,0] = AC.return_x_position()
                        self.measurement_positions_real[self.i_pos,1] = AC.return_y_position()
                        self.i_sweep = 0
                        print(self.i_pos)
                else: #enter here normally
                    self.ui.MeasurementProgressBar.setValue(0)
                    SendSlackNotification()
                    np.save(self.temp_path_measurement,self.im_meas_data)
                    np.save(self.temp_path_measurement + '_ON',self.im_meas_data_on)
                    np.save(self.temp_path_measurement + '_OFF',self.im_meas_data_off)
                    np.save(self.temp_path_measurement + '_delaytimes',self.delaytimes)
                    self.CloseWLStages()
                    self.TAM_Measurement_underway = False
                    self.ui.Start_Measurement.setStyleSheet('color:black')
                    self.ui.Start_Measurement.setCheckable(False)
                    self.TAM_Measurement_underway = False    


        # "Cryo control implementation: "
        # # if connected to MercuryITC
        # if MC.m.connect():
        #     if self.ui.Live_Cryo.isChecked():
        #         t, u1 = MC.temp.temp
        #         f, u2 = MC.gas.flow
        #         h, u3 = MC.heater.volt
        #         self.TempTime_line.setData(float(t))
        #         self.FlowTime_line.setData(float(f))
        #         self.HeatTime_line.setDate(float(h))
                

        "Helps avoid having threads"
        QtCore.QTimer.singleShot(1, self._update)

    def Display_Live_Thunder(self):
        if self.ui.Thunder_Live.isChecked():
            self.ui.Thunder_Live.setStyleSheet('color:green')
        else:
            self.ui.Thunder_Live.setStyleSheet('color:black')
    
    def Display_Live_Thunder_static(self):
        if self.ui.Thunder_static_Live.isChecked():
            self.ui.Thunder_static_Live.setStyleSheet('color:green')
        else:
            self.ui.Thunder_static_Live.setStyleSheet('color:')
        
    def setcamroi_btnstate(self):
        self.pause = 1
        self.core.stop_sequence_acquisition()
        self.roi_size_camera = int(np.mean([self.roi.getArrayRegion(self.data_diffnorm, self.img1).shape[0],self.roi.getArrayRegion(self.data_diffnorm, self.img1).shape[1]]))
        self.c_x = self.c_x +  int(self.roi.pos()[1])
        self.c_y = self.c_y + int(self.roi.pos()[0])
        self.core.set_roi(self.c_x,self.c_y,self.roi_size_camera,self.roi_size_camera)
        self.im_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.im_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.core.start_continuous_sequence_acquisition(1) #Block the calling thread for 1ms        
        self.image_array_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_array_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_diff_norm = np.zeros((self.roi_size_camera,self.roi_size_camera))
        self.dataon = self.image_array_on
        self.dataoff = self.image_array_off
        self.data_diffnorm = bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.image_diff_norm,self.roi_size_camera)
        self.im_disp = np.zeros((self.shots_to_avg_disp,self.roi_size_camera,self.roi_size_camera))
        self.dTT_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.static_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.roi.setPos([self.roi_size_camera/4, self.roi_size_camera/4])
        self.roi.setSize([self.roi_size_camera/2, self.roi_size_camera/2])

    def resetcamroi_btnstate(self):
        self.pause = 1
        self.core.stop_sequence_acquisition()
        self.roi_size_camera = 512
        self.c_x = 0
        self.c_y = 0
        self.core.set_roi(self.c_x,self.c_y,self.roi_size_camera,self.roi_size_camera)
        self.im_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.im_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.core.start_continuous_sequence_acquisition(1) #Block the calling thread for 1ms        
        self.image_array_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_array_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
        self.image_diff_norm = np.zeros((self.roi_size_camera,self.roi_size_camera))
        self.dataon = self.image_array_on
        self.dataoff = self.image_array_off
        self.data_diffnorm = bpf.produce_diff_norm_image( self.dataon, self.dataoff, self.image_diff_norm,self.roi_size_camera)
        self.im_disp = np.zeros((self.shots_to_avg_disp,self.roi_size_camera,self.roi_size_camera))
        self.dTT_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.static_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.roi.setPos([self.roi_size_camera/4, self.roi_size_camera/4])
        self.roi.setSize([self.roi_size_camera/2, self.roi_size_camera/2])
        
    #Setup button state release for flipsign
    def flipsign_btnstate(self):
        if self.ui.Flip_sign_Thunder.isChecked():
            self.flip_sign_i = 1
        else:
            self.flip_sign_i = 0  
            
    def ChangeExposure_SnapThunder_SpectrometerTab(self):
        self.exposure = float(self.ui.Set_Exposure_Thunder_2.text())
        self.core.set_exposure(self.exposure)
        self.pause = 1
        print('Exposure set to ',self.core.get_exposure())
              
    def ChangeExposure(self):
        self.exposure = float(self.ui.Set_Exposure_Thunder.text())
        if self.exposure <51:
            self.pause = 1
            self.core.stop_sequence_acquisition()
            self.core.set_exposure(self.exposure)
            self.core.start_continuous_sequence_acquisition(1)
            print('Exposure set to ',self.core.get_exposure())
        else:
            print('Sorry, not compatible with the 30Hz choppper')
        
    def ChangeGain(self):
        self.gain = float(self.ui.Set_Gain_Thunder.text())
        self.pause = 1
        self.core.stop_sequence_acquisition()
        self.core.set_property('Camera-1','MultiplierGain',self.gain)
        self.core.start_continuous_sequence_acquisition(1)
        print(self.core.get_property('Camera-1','MultiplierGain'))
        
    def ChangeShotstoAvg(self):
        self.disp_counter = 0
        self.shots_to_avg_disp = int(self.ui.Shots_to_avg_display.text())
        self.im_disp =   np.zeros((self.shots_to_avg_disp,self.roi_size_camera,self.roi_size_camera))
        
    def MoveStage_ThunderTab(self):
        if  self.ui.HighNA_NewportStage_Box.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = float(self.ui.SetDelay.text())  +self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            print(longdelay_highNA.ReturnTime()-self.global_time_zero_highNAnewport)
            self.ui.CurrentDelay.display(float(longdelay_highNA.ReturnTime()-self.global_time_zero_highNAnewport))
        if self.ui.Cryo_NewportStage_Box.isChecked() == True:
            print('Using Long Delay cryo')
            self.x = float(self.ui.SetDelay.text())  +self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box.isChecked() == True:
            self.x = float(self.ui.SetDelay.text())  +self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
            print('Using Short Stage')
                    
    def MoveStage_SpectrometerTab(self):
        if  self.ui.HighNA_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = float(self.ui.SetDelay_2.text())  +self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
        if self.ui.Cryo_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay cryo')
            self.x = float(self.ui.SetDelay_2.text())  +self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box_2.isChecked() == True:
            self.x = float(self.ui.SetDelay_2.text())  +self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay_2.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
            print('Using Short Stage')
            
    def IncrementDelayStagePos_ThunderTab(self):
        self.x =   self.ui.CurrentDelay.value() + float(self.ui.Set_increment_delay.text()) 
        if  self.ui.HighNA_NewportStage_Box.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = self.x + self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            self.ui.CurrentDelay.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
        if self.ui.Cryo_NewportStage_Box.isChecked() == True:
            print('Using Long Delay cryo')
            self.x = self.x+self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box.isChecked() == True:
            self.x = self.x+self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)- self.global_time_zero_shortstage)
            print('Using Short Stage')
            
    def IncrementDelayStagePos_SpectrometerTab(self):
        self.x =   self.ui.CurrentDelay_2.value() + float(self.ui.Set_increment_delay_2.text()) 
        if  self.ui.HighNA_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = self.x + self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
        if self.ui.Cryo_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay cryo')
            self.x = self.x+self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box_2.isChecked() == True:
            self.x = self.x+self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay_2.display(np.round(PI_shortstage.ReturnTime(),1)- self.global_time_zero_shortstage)
            print('Using Short Stage')  
            
    def IncrementDelayStageNeg_ThunderTab(self):
        self.x =  self.ui.CurrentDelay.value() - float(self.ui.Set_increment_delay.text()) 
        if  self.ui.HighNA_NewportStage_Box.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = self.x  + self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            self.ui.CurrentDelay.display(np.round(longdelay_highNA.ReturnTime(),1)  - self.global_time_zero_highNAnewport)
        if self.ui.Cryo_NewportStage_Box.isChecked() == True:
            print('Using Long Delay cryo')
            self.x =self.x+ self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box.isChecked() == True:
            self.x = self.x + self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)- self.global_time_zero_shortstage)
            print('Using Short Stage')
            
    def IncrementDelayStageNeg_SpectrometerTab(self):
        self.x =   self.ui.CurrentDelay_2.value() - float(self.ui.Set_increment_delay_2.text()) 
        if  self.ui.HighNA_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay high NA')
            self.x = self.x + self.global_time_zero_highNAnewport
            longdelay_highNA.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
        if self.ui.Cryo_NewportStage_Box_2.isChecked() == True:
            print('Using Long Delay cryo')
            self.x = self.x+self.global_time_zero_cryo
            longdelay_cryo.MovetoTime(self.x)
            self.ui.CurrentDelay_2.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
        if self.ui.PIStage_Box_2.isChecked() == True:
            self.x = self.x+self.global_time_zero_shortstage
            PI_shortstage.MovetoTime(self.x)
            time.sleep(50e-3)
            self.ui.CurrentDelay_2.display(np.round(PI_shortstage.ReturnTime(),1)- self.global_time_zero_shortstage)
            print('Using Short Stage')    
            
    def DefineHome_Thunder(self):
        if  self.ui.HighNA_NewportStage_Box.isChecked() == True:
            self.SetGlobalTimeZero_highNA_newport_Thunder()
        if self.ui.Cryo_NewportStage_Box.isChecked() == True:
            self.SetGlobalTimeZero_cryo_longdelay_Thunder()
        if self.ui.PIStage_Box.isChecked() == True:
            self.SetGlobalTimeZero_shortstage_Thunder()
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_highNA_newport.npy",np.round(longdelay_highNA.ReturnTime(),1))
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_shortstage.npy",np.round(PI_shortstage.ReturnTime(),1))   
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_cryo_longdelay.npy",np.round(longdelay_cryo.ReturnTime(),1))       
        
    def SetGlobalTimeZero_highNA_newport_Thunder(self):
        self.global_time_zero_highNAnewport = self.ui.CurrentDelay.value() + self.global_time_zero_highNAnewport
        self.ui.CurrentDelay.display(np.round(longdelay_highNA.ReturnTime(),1)  - self.global_time_zero_highNAnewport) 
        
    def SetGlobalTimeZero_shortstage_Thunder(self):
        self.global_time_zero_shortstage = self.ui.CurrentDelay.value() + self.global_time_zero_shortstage
        self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)      
        
    def SetGlobalTimeZero_cryo_longdelay_Thunder(self):
        self.global_time_zero_cryo= self.ui.CurrentDelay.value() + self.global_time_zero_cryo
        self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)  - self.global_time_zero_cryo)
          
    def Load_time_zero(self):
        self.ui.Load_time_zero.setStyleSheet('color:green')
        try:
            self.global_time_zero_highNAnewport = np.load("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_highNA_newport.npy")
            longdelay_highNA.MovetoTime(self.global_time_zero_highNAnewport)
            self.ui.CurrentDelay.display(np.round(longdelay_highNA.ReturnTime(),1)  - self.global_time_zero_highNAnewport)
        except:
            print('no file for highNA')
        try:
            self.global_time_zero_shortstage = np.load("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_shortstage.npy")
            PI_shortstage.MovetoTime(self.global_time_zero_shortstage)
            self.ui.CurrentDelay.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
        except:
            print('no file for shortstage')
        try:
            self.global_time_zero_cryo = np.load("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_cryo_longdelay.npy")
            longdelay_cryo.MovetoTime(self.global_time_zero_cryo )
            self.ui.CurrentDelay.display(np.round(longdelay_cryo.ReturnTime(),1)  - self.global_time_zero_cryo)
        except:
            print('no file for cryo')
        
    def DefineHome_Spec(self):
        if  self.ui.HighNA_NewportStage_Box_2.isChecked() == True:
            self.SetGlobalTimeZero_highNA_newport_Spec()
        if self.ui.Cryo_NewportStage_Box_2.isChecked() == True:
            self.SetGlobalTimeZero_cryo_longdelay_Spec()
        if self.ui.PIStage_Box_2.isChecked() == True:
            self.SetGlobalTimeZero_shortstage_Spec()
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_highNA_newport.npy",np.round(longdelay_highNA.ReturnTime(),1))
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_shortstage.npy",np.round(PI_shortstage.ReturnTime(),1))   
        np.save("C:\PyRunTAM\LastTimeZero\GlobalTimeZero_cryo_longdelay.npy",np.round(longdelay_cryo.ReturnTime(),1))  
            
    def SetGlobalTimeZero_highNA_newport_Spec(self):
        self.global_time_zero_highNAnewport = self.ui.CurrentDelay_2.value() + self.global_time_zero_highNAnewport
        self.ui.CurrentDelay_2.display(np.round(longdelay_highNA.ReturnTime(),1)  - self.global_time_zero_highNAnewport)
        
    def SetGlobalTimeZero_shortstage_Spec(self):
        self.global_time_zero_shortstage = self.ui.CurrentDelay_2.value() + self.global_time_zero_shortstage
        self.ui.CurrentDelay_2.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
         
    def SetGlobalTimeZero_cryo_longdelay_Spec(self):
        self.global_time_zero_cryo= self.ui.CurrentDelay_2.value() + self.global_time_zero_cryo
        self.ui.CurrentDelay_2.display(np.round(longdelay_cryo.ReturnTime(),1)  - self.global_time_zero_cryo)
         
    def mouseClicked(self,event):
        if self.Set_Center_Thunderbtn_state == False:
            self.dTT_thunder_c_x = self.dTT_image_view.mapSceneToView(event.scenePos()).x()
            self.dTT_thunder_c_y = self.dTT_image_view.mapSceneToView(event.scenePos()).y()
            self.ui.c_x_thunder.display(self.dTT_thunder_c_x)
            self.ui.c_y_thunder.display(self.dTT_thunder_c_y)
            
    def Set_Center_Thunderbtn(self):
        if self.ui.Set_Center_Thunder.isChecked():
            self.ui.c_x_thunder.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.c_y_thunder.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.Set_Center_Thunderbtn_state = True
        else:
            self.ui.c_x_thunder.setStyleSheet("""QLCDNumber { background-color: white; color: black; }""")
            self.ui.c_y_thunder.setStyleSheet("""QLCDNumber { background-color: white; color: black; }""")
            self.Set_Center_Thunderbtn_state = False
         
    def DTT_FittingRoutine(self):
        if self.ui.DTT_fit_Gaussian.isChecked():
            self.avg_image_diff_norm = np.mean(np.reshape(self.avg_image_array_on/self.avg_image_array_off - 1,(self.averages_dTT_fit,self.roi_size_camera,self.roi_size_camera)),axis =0)
            self.ui.DTT_Fit.setChecked(False)
            self.dk_guess = float(self.ui.DTT_dk_guess.text())
            self.sigma_guess = float(self.ui.DTT_sigma_guess.text())/55.5
            try:
                self.fit_output,self.fitted_output = bpf.FitGauss(np.nan_to_num(self.avg_image_diff_norm), self.dTT_thunder_c_y, self.dTT_thunder_c_x, self.dk_guess,self.sigma_guess)
            except:
                self.fit_output = np.asarray([-1,-1,-1,-1,-1])
            self.ui.DTT_fitted_dk.display(self.fit_output[0])
            self.ui.DTT_fitted_sigma.display((self.fit_output[3] + self.fit_output[4])/2 * 55.5)
            self.ui.c_x_thunder.display(self.fit_output[2])
            self.ui.c_y_thunder.display(self.fit_output[1])
            self.ui.c_x_thunder.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.c_y_thunder.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_fitted_dk.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_fitted_sigma.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.averaging_index = 0
            self.ui.DTT_Fit.setStyleSheet('color:black')
            return self.fitted_output
        if self.ui.DTT_Fit_3D.isChecked():
            self.avg_image_diff_norm = np.mean(np.reshape(self.avg_image_array_on/self.avg_image_array_off - 1,(self.averages_dTT_fit,self.roi_size_camera,self.roi_size_camera)),axis =0)
            self.avg_radial_profile_x = bpf.radial_profile(self.avg_image_diff_norm , (self.dTT_thunder_c_y,self.dTT_thunder_c_x))[0]
            self.avg_radial_profile_y = bpf.radial_profile(self.avg_image_diff_norm , (self.dTT_thunder_c_y,self.dTT_thunder_c_x))[1]
            self.ui.DTT_Fit.setChecked(False)
            self.BandpassWavelength = float(self.ui.BandpassWavelength.text())*1e-3
            self.SampleThickness = float(self.ui.SampleThickness.text())*1e-3
            self.SampleRI = float(self.ui.SampleRI.text())
            self.z_guess = float(self.ui.DTT_z_guess.text())*1e-3
            self.dk_guess = float(self.ui.DTT_dk_guess.text())
            self.dn_guess = float(self.ui.DTT_dn_guess.text())
            self.sigma_guess = float(self.ui.DTT_sigma_guess.text())*1e-3
            self.averaging_index = 0
            try:
                self.fit_value_3D = bpf.fit_3D(self.avg_radial_profile_x,self.avg_radial_profile_y,self.z_guess,self.dk_guess,self.dn_guess,self.sigma_guess,self.BandpassWavelength,self.SampleThickness,self.SampleRI)
            except:
                self.fit_value_3D  = np.asarray([-1,-1,-1,-1])
            self.ui.DTT_fitted_dk.display(self.fit_value_3D[1])
            self.ui.DTT_fitted_dn.display(self.fit_value_3D[2])
            self.ui.DTT_fitted_sigma.display(self.fit_value_3D[3]*1e3)
            self.ui.DTT_fitted_z.display(self.fit_value_3D[0])
            self.ui.DTT_fitted_dk.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_fitted_sigma.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_fitted_dn.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_fitted_z.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            self.ui.DTT_Fit.setStyleSheet('color:black')
            self.fitted_output = self.ConstructRadSymmImg()
            return self.fitted_output
                
    def ConstructRadSymmImg(self):
        x = np.arange(0,np.shape(self.avg_image_diff_norm)[0],step =1) - self.dTT_thunder_c_y
        y = np.arange(0,np.shape(self.avg_image_diff_norm)[1],step =1) - self.dTT_thunder_c_x
        X,Y = np.meshgrid(x*55.5e-3,y*55.5e-3)
        R = np.abs(np.sqrt(X**2 + Y**2))
        Image = (np.abs(bpf.ReturnImageEField(self.BandpassWavelength,self.SampleThickness,self.SampleRI,*self.fit_value_3D)[3])**2/np.abs(bpf.ReturnImageEField(self.BandpassWavelength,self.SampleThickness,self.SampleRI,0,0,0,self.fit_value_3D[3])[3])**2) - 1
        x_image = bpf.ReturnImageEField(self.BandpassWavelength,self.SampleThickness,self.SampleRI,*self.fit_value_3D)[2]
        f_DTT = interp1d(x_image,Image,bounds_error=None,fill_value ='extrapolate')
        return f_DTT(R)
        
    def Initialise_DTT_Averaging(self):
        self.ui.DTT_Fit.setStyleSheet('color:green')
        self.averages_dTT_fit = int(self.ui.DTT_fit_averages.text())
        self.avg_image_array_on = np.zeros((self.averages_dTT_fit,self.roi_size_camera*self.roi_size_camera))
        self.avg_image_array_off = np.zeros((self.averages_dTT_fit,self.roi_size_camera*self.roi_size_camera))
        self.avg_image_diff_norm = np.zeros((self.roi_size_camera,self.roi_size_camera))
        self.averaging_index = 0
        
    def Move_Attocube_Up_Thunder(self):
        self.y_pos_stage = AC.return_y_position() + float(self.ui.Set_increment_xy.text())
        AC.move_y_position_incr(self.y_pos_stage)
        self.ui.y_position_display.display(AC.return_y_position()/1000)
        print(AC.return_y_position()/1000)

    def Move_Attocube_Down_Thunder(self):
        self.y_pos_stage = AC.return_y_position() - float(self.ui.Set_increment_xy.text())
        AC.move_y_position_incr(self.y_pos_stage)
        self.ui.y_position_display.display(AC.return_y_position()/1000)
        print(AC.return_y_position()/1000)
        
    def Move_Attocube_Left_Thunder(self):
        self.x_pos_stage = AC.return_x_position() - float(self.ui.Set_increment_xy.text())
        AC.move_x_position_incr(self.x_pos_stage)
        self.ui.x_position_display.display(AC.return_x_position()/1000)
        print(AC.return_x_position()/1000)
        
    def Move_Attocube_Right_Thunder(self):
        self.x_pos_stage = AC.return_x_position() + float(self.ui.Set_increment_xy.text())
        AC.move_x_position_incr(self.x_pos_stage)
        self.ui.x_position_display.display(AC.return_x_position()/1000)
        print(AC.return_x_position()/1000)
        
    def Move_Z_Nanopositioner_Up_Thunder(self):
        if self.ui.HighNA_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(0)
            self.z_pos = self.z_pos + float(self.ui.Set_increment_z.text())
            Z_controller.move_to_z_position(0,self.z_pos)
            self.ui.z_voltage_display.display(self.z_pos)
        if self.ui.Cryo_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(1)
            self.z_pos = self.z_pos + float(self.ui.Set_increment_z.text())
            Z_controller.move_to_z_position(1,self.z_pos)
            self.ui.z_voltage_display.display(self.z_pos)
        
    def Move_Z_Nanopositioner_Down_Thunder(self):
        if self.ui.HighNA_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(0)
            self.z_pos = self.z_pos - float(self.ui.Set_increment_z.text())
            Z_controller.move_to_z_position(0,self.z_pos)
            self.ui.z_voltage_display.display(self.z_pos)
        if self.ui.Cryo_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(1)
            self.z_pos = self.z_pos - float(self.ui.Set_increment_z.text())
            Z_controller.move_to_z_position(1,self.z_pos)
            self.ui.z_voltage_display.display(self.z_pos)
        
    def Move_Attocube_Up_Spec(self):
        self.y_pos_stage = self.y_pos_stage + float(self.ui.Set_increment_xy_3.text())
        AC.move_y_position_incr(self.y_pos_stage)
        self.ui.y_position_display_3.display(AC.return_y_position()/1000)

    def Move_Attocube_Down_Spec(self):
        self.y_pos_stage = self.y_pos_stage - float(self.ui.Set_increment_xy_3.text())
        AC.move_y_position_incr(self.y_pos_stage)
        self.ui.y_position_display_3.display(AC.return_y_position()/1000)
        
    def Move_Attocube_Left_Spec(self):
        self.x_pos_stage = self.x_pos_stage - float(self.ui.Set_increment_xy_3.text())
        AC.move_x_position_incr(self.x_pos_stage)
        self.ui.x_position_display_3.display(AC.return_x_position()/1000)
        
    def Move_Attocube_Right_Spec(self):
        self.x_pos_stage = self.x_pos_stage + float(self.ui.Set_increment_xy_3.text())
        AC.move_x_position_incr(self.x_pos_stage)
        self.ui.x_position_display_3.display(AC.return_x_position()/1000)
        
    def Move_Z_Nanopositioner_Up_Spec(self):
        if self.ui.HighNA_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(0)
            self.z_pos = self.z_pos + float(self.ui.Set_increment_z_3.text())
            Z_controller.move_to_z_position(0,self.z_pos)
            self.ui.z_voltage_display_3.display(self.z_pos)
        if self.ui.Cryo_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(1)
            self.z_pos = self.z_pos + float(self.ui.Set_increment_z_3.text())
            Z_controller.move_to_z_position(1,self.z_pos)
            self.ui.z_voltage_display_3.display(self.z_pos)
        
    def Move_Z_Nanopositioner_Down_Spec(self):
        if self.ui.HighNA_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(0)
            self.z_pos = self.z_pos - float(self.ui.Set_increment_z_3.text())
            Z_controller.move_to_z_position(0,self.z_pos)
            self.ui.z_voltage_display_3.display(self.z_pos)
        if self.ui.Cryo_Zpos_Box.isChecked():
            self.z_pos = Z_controller.return_z_position(1)
            self.z_pos = self.z_pos - float(self.ui.Set_increment_z_3.text())
            Z_controller.move_to_z_position(1,self.z_pos)
            self.ui.z_voltage_display_3.display(self.z_pos)
        
    def Power_meter_increase(self):
        self.power_meter_pos = self.power_meter_pos + float(self.ui.Set_increment_powermeter.text())
        phidget.set_powermeter(self.power_meter_pos)
        self.ui.power_meter_display.display(self.power_meter_pos)
        
    def Power_meter_decrease(self):
        self.power_meter_pos = self.power_meter_pos - float(self.ui.Set_increment_powermeter.text())
        phidget.set_powermeter(self.power_meter_pos)
        self.ui.power_meter_display.display(self.power_meter_pos)
        
    def Power_wheel_increase(self):
        self.power_wheel_pos = self.power_wheel_pos + float(self.ui.Set_increment_powerwheel.text())
        phidget.set_powerwheel(self.power_wheel_pos)
        self.ui.power_wheel_display.display(self.power_wheel_pos)
            
    def Power_wheel_decrease(self):
        self.power_wheel_pos = self.power_wheel_pos - float(self.ui.Set_increment_powerwheel.text())
        phidget.set_powerwheel(self.power_wheel_pos)
        self.ui.power_wheel_display.display(self.power_wheel_pos)
        
    def StartChopperCalib(self):
        if self.ui.Start_Chopper_Phase_Calib.isChecked():
            self.ui.Start_Chopper_Phase_Calib.setStyleSheet('color:black')
            return False
        self.ui.Start_Chopper_Phase_Calib.setStyleSheet('color:green')
        self.pumpon_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.pumpoff_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        return True
    
    def mouseClicked_forPhase(self,event):
        self.chopperphase_pix_x = self.pumpon_image_view.mapSceneToView(event.scenePos()).x()
        self.chopperphase_pix_y = self.pumpon_image_view.mapSceneToView(event.scenePos()).y()
        self.ui.ChopperPhase_pix_x.display(self.chopperphase_pix_x)
        self.ui.ChopperPhase_pix_y.display(self.chopperphase_pix_y)
           
    def StartChopperHistogramCalib(self):
        self.chopperphasehist = np.zeros(2)
        if self.ui.MeasureShots.isChecked():
            self.start_Calib_Chopper= True
        else:
            self.start_Calib_Chopper= False
            
    def ComputeResidues(self):
        if self.ui.DTT_fit_Gaussian.isChecked():
            self.xtemp = np.arange(0,np.shape(self.avg_image_diff_norm)[0],1)
            self.xdata_tuple = np.meshgrid(self.xtemp , self.xtemp )
            self.computed_residuals = np.reshape(np.nan_to_num(self.avg_image_diff_norm).ravel() - bpf.twoD_Gaussian(self.xdata_tuple,*self.fit_output),(np.shape(self.avg_image_diff_norm)[0],np.shape(self.avg_image_diff_norm)[0]))
        if self.ui.DTT_Fit_3D.isChecked():
            self.xtemp = np.arange(0,np.shape(self.avg_image_diff_norm)[0],1)
            self.xdata_tuple = np.meshgrid(self.xtemp , self.xtemp )
            self.computed_residuals = np.nan_to_num(self.avg_image_diff_norm) - self.fitted_output
        return self.computed_residuals
    
    def ReturnAverages(self):
        return np.nan_to_num(self.avg_image_diff_norm)
    
    def FFT_Filter(self):
        if self.ui.Set_FFT_Filter.isChecked():
            self.ui.Set_FFT_Filter.setStyleSheet('color:orange')
            return True
        else:
            self.ui.Set_FFT_Filter.setStyleSheet('color:black')
            return False
            
    def Set_FTT_Filter_radius(self):
        self.FFT_Filter_radius = float(self.ui.FFT_filter_radius.text())
    
    def DisplayResiduals(self):
        if self.ui.Plot_residuals.isChecked():
            self.ui.Plot_residuals.setStyleSheet('color:green')
            return True
        self.ui.Plot_residuals.setStyleSheet('color:black')
        return False
    
    def DisplayAverage(self):
        if self.ui.Plot_average.isChecked():
            self.ui.Plot_average.setStyleSheet('color:green')
            return True
        self.ui.Plot_average.setStyleSheet('color:black')
        return False

    def ShutterPump(self):
        if self.ui.PumpShutter.isChecked():
            self.ui.PumpShutter.setStyleSheet('color:green')
            phidget.setpos(1,[0])
            return True
        else:
            self.ui.PumpShutter.setStyleSheet('color:black')
            phidget.setpos(0,[0])
            return False
            
    def ShutterProbe(self):
        if self.ui.ProbeShutter.isChecked():
            self.ui.ProbeShutter.setStyleSheet('color:green')
            phidget.setpos(1,[1])
            return True
        else:
            self.ui.ProbeShutter.setStyleSheet('color:black')
            phidget.setpos(0,[1])
            return False
            
    def ShutterNIR(self):
        if self.ui.NIR_Stage_Shutter.isChecked():
            self.ui.NIR_Stage_Shutter.setStyleSheet('color:red')
            phidget.setpos(1,[3])
            return True
        else:
            self.ui.NIR_Stage_Shutter.setStyleSheet('color:black')
            phidget.setpos(0,[3])
            return False
            
    def ShutterVis(self):
        if self.ui.Vis_Stage_Shutter.isChecked():
            self.ui.Vis_Stage_Shutter.setStyleSheet('color:green')
            phidget.setpos(1,[4])
            return True
        else:
            self.ui.Vis_Stage_Shutter.setStyleSheet('color:black')
            phidget.setpos(0,[4])
            return False
            
    def ShutterBlue(self):
        if self.ui.Blue_Stage_Shutter.isChecked():
            self.ui.Blue_Stage_Shutter.setStyleSheet('color:blue')
            phidget.setpos(1,[6])
            return True
        else:
            self.ui.Blue_Stage_Shutter.setStyleSheet('color:black')
            phidget.setpos(0,[6])
            return False
        
    def ShutterPump_2(self):
        if self.ui.PumpShutter_2.isChecked():
            self.ui.PumpShutter_2.setStyleSheet('color:green')
            phidget.setpos(1,[0])
            return True
        else:
            self.ui.PumpShutter_2.setStyleSheet('color:black')
            phidget.setpos(0,[0])
            return False
            
    def ShutterProbe_2(self):
        if self.ui.ProbeShutter_2.isChecked():
            self.ui.ProbeShutter_2.setStyleSheet('color:green')
            phidget.setpos(1,[1])
            return True
        else:
            self.ui.ProbeShutter_2.setStyleSheet('color:black')
            phidget.setpos(0,[1])
            return False
            
    def ShutterNIR_2(self):
        if self.ui.NIR_Stage_Shutter_2.isChecked():
            self.ui.NIR_Stage_Shutter_2.setStyleSheet('color:red')
            phidget.setpos(1,[3])
            return True
        else:
            self.ui.NIR_Stage_Shutter_2.setStyleSheet('color:black')
            phidget.setpos(0,[3])
            return False
            
    def ShutterVis_2(self):
        if self.ui.Vis_Stage_Shutter_2.isChecked():
            self.ui.Vis_Stage_Shutter_2.setStyleSheet('color:green')
            phidget.setpos(1,[4])
            return True
        else:
            self.ui.Vis_Stage_Shutter_2.setStyleSheet('color:black')
            phidget.setpos(0,[4])
            return False
            
    def ShutterBlue_2(self):
        if self.ui.Blue_Stage_Shutter_2.isChecked():
            self.ui.Blue_Stage_Shutter_2.setStyleSheet('color:blue')
            phidget.setpos(1,[6])
            return True
        else:
            self.ui.Blue_Stage_Shutter_2.setStyleSheet('color:black')
            phidget.setpos(0,[6])
            return False
            
    def Spectrometer_live_dtt(self):
        if self.ui.Spectrometer_DTT_Live.isChecked():
            self.ui.Spectrometer_DTT_Live.setStyleSheet('color:green')
            self.spec_thread.emit_dTT = True
        else:
            if hasattr(self,'spec_thread'):
                self.spec_thread.emit_dTT = False
            self.ui.Spectrometer_DTT_Live.setStyleSheet('color:black')
        
    def Spectrometer_live_static(self):
        if self.ui.Spectrometer_Spectrum_Live.isChecked():
            self.ui.Spectrometer_Spectrum_Live.setStyleSheet('color:green')
            self.spec_thread.emit_spectrum = True
        else:
            self.spec_thread.emit_spectrum = False
            self.ui.Spectrometer_Spectrum_Live.setStyleSheet('color:black')   
        
    def ChangeNumberOfShots_Spec(self):
        if int(self.ui.Shots_to_avg_display_spec.text()) > 30:
            self.no_of_avgs_spec = int(self.ui.Shots_to_avg_display_spec.text())
            self.spec_thread.no_of_avgs_spec = self.no_of_avgs_spec
        else:
            pass

    def ToggleCameraAcq(self):
        if self.ui.Thunder_Acquisition.isChecked():
            "Initialise Camera to Thunder"
            print('Initialising Thunder')
            self.bridge = Bridge()
            self.core = self.bridge.get_core()
        
            "Set Initial Exposure and Gain"
            self.exposure=10
            self.core.set_exposure(self.exposure)
            self.gain =1
            self.core.set_property('Camera-1','MultiplierGain',self.gain)
            self.core.set_property('Camera-1','ShutterMode','Pre-Sequence')
            self.core.set_property('Camera-1','ClearMode','Pre- and Post-Sequence')
            self.core.set_property('Camera-1','TriggerMode','Strobed')
            if not hasattr(self,'roi_size_camera'):
                self.roi_size_camera = 512
                self.c_x =0
                self.c_y =0
                self.dx = 0
                self.dy = 0

            self.im_on = np.zeros(self.roi_size_camera*self.roi_size_camera)
            self.im_off = np.zeros(self.roi_size_camera*self.roi_size_camera)
            self.core.get_roi()
            self.core.set_roi(self.c_x,self.c_y,self.roi_size_camera,self.roi_size_camera)
            
            self.ui.Set_Gain_Thunder.clear()
            self.ui.Set_Exposure_Thunder.clear()
            self.ui.Set_Exposure_Thunder_2.clear()
            self.ui.Set_Gain_Thunder.insert(str(self.gain))
            self.ui.Set_Exposure_Thunder.insert(str(self.exposure))
            self.ui.Set_Exposure_Thunder_2.insert(str(self.exposure))
            
            self.ui.Thunder_Acquisition.setStyleSheet('color:green')
            self.ui.Spectrometer_Acquisition.setChecked(False)
            self.ui.Spectrometer_Acquisition.setCheckable(True)
            self.core.start_continuous_sequence_acquisition(1)
            self.pause = 1
            self.ui.Thunder_Live.setCheckable(True)
            self.ui.Thunder_static_Live.setCheckable(True)
            self.ui.Set_ROI_Thunder.setCheckable(True)
            self.ui.ReSet_ROI_Thunder.setCheckable(True)
            self.ui.DTT_Fit.setCheckable(True)
            self.ui.Set_Center_Thunder.setCheckable(True)
            self.ToggleSpectrometerAcq()
        else:
            self.ui.Thunder_Acquisition.setStyleSheet('color:black')
            if hasattr(self,'core'):
                self.core.stop_sequence_acquisition()
            self.pause = 1
            self.ui.Thunder_Live.setChecked(False)
            self.ui.Thunder_Live.setCheckable(False)
            self.ui.Thunder_static_Live.setChecked(False)
            self.ui.Thunder_static_Live.setCheckable(False)
            self.ui.Set_ROI_Thunder.setCheckable(False)
            self.ui.ReSet_ROI_Thunder.setCheckable(False)
            self.ui.DTT_Fit.setCheckable(False)
            self.ui.Set_Center_Thunder.setCheckable(False)
            self.ui.Spectrometer_Acquisition.setCheckable(True)
        self.Display_Live_Thunder()
        self.Display_Live_Thunder_static()
            
    def ToggleSpectrometerAcq(self):
        if self.ui.Spectrometer_Acquisition.isChecked():
            self.spec_thread = FastSpectrometerAcqThread(self.no_of_avgs_spec)
            self.spec_thread.dTT_avg.connect(self.dTTSpectrumRecieved)
            self.spec_thread.dTT_avg.connect(self.SpectrallyResolvedMeasurement)
            self.spec_thread.spectrum.connect(self.StaticSpectrumRecieved)
            self.spec_thread.spectrum_stats.connect(self.StaticSpectrumStatisticsRecieved)
            self.spec_thread.start()
            self.ui.Spectrometer_Acquisition.setStyleSheet('color:green')
            self.ui.Thunder_Acquisition.setChecked(False)
            self.ToggleCameraAcq()
            self.ui.Thunder_Acquisition.setCheckable(True)
            self.ui.Spectrometer_DTT_Live.setCheckable(True)
            self.ui.Spectrometer_Spectrum_Live.setCheckable(True)
            self.ui.DTT_Fit.setCheckable(True)
            self.ui.Set_Center_Thunder.setCheckable(True)
        else:
            if hasattr(self,'spec_thread'):
                self.spec_thread.cleanup_framegrabber = True
            self.ui.Spectrometer_Acquisition.setStyleSheet('color:black')
            self.ui.Spectrometer_DTT_Live.setChecked(False)
            self.ui.Spectrometer_DTT_Live.setCheckable(False)
            self.ui.Spectrometer_Spectrum_Live.setChecked(False)
            self.ui.Spectrometer_Spectrum_Live.setCheckable(False)
            self.ui.Thunder_Acquisition.setCheckable(True)
            
        if hasattr(self,'spec_thread'):
            self.Spectrometer_live_dtt()
        
    def dTTSpectrumRecieved(self,dTT_spec):
        if hasattr(self, 'spec_wavelengths'):
                dTT_spec = np.transpose(np.asarray( [self.spec_wavelengths,dTT_spec]))
        if self.ui.Spectrometer_Acquisition.isChecked() and self.ui.Spectrometer_DTT_Live.isChecked() and not self.Spec_Measurement_underway:
            self.DTT_spec_plot_spec.setData(dTT_spec)
            if self.ui.Spectrometer_Freeze.isChecked():
                self.avg_DTT_spec_plot_spec = self.DTT_spec_plot.plot(clear = False,pen= pg.mkPen(self.spec_thread.no_of_frozen_spectra))
                self.avg_DTT_spec_plot_spec.setData(dTT_spec,axis =0)
                self.spec_thread.no_of_frozen_spectra += 1
                self.ui.Spectrometer_Freeze.setChecked(False)
            if self.ui.Spectrometer_Freeze_ClearAll.isChecked():
                self.avg_DTT_spec_plot_spec = self.DTT_spec_plot.plot(clear = True,pen= pg.mkPen(self.spec_thread.no_of_frozen_spectra))
                self.DTT_spec_plot_spec = self.DTT_spec_plot.plot(clear=True)
                self.ui.Spectrometer_Freeze_ClearAll.setChecked(False)
            
    def StaticSpectrumRecieved(self,spectrum):
        if hasattr(self, 'spec_wavelengths'):
                spectrum =  np.transpose(np.asarray([self.spec_wavelengths,spectrum]))
        if self.ui.Spectrometer_Acquisition.isChecked() and self.ui.Spectrometer_Spectrum_Live.isChecked() and not self.Spec_Measurement_underway:
            self.static_spec_plot.plot(spectrum, clear=True)
        if self.ui.Spectrometer_Acquisition.isChecked() and self.ui.SpectrumSnapCalib.isChecked() and not self.Spec_Measurement_underway:
            self.calib_peak_line.setValue(400)
            self.calib_snapped_spectra = spectrum
            self.calib_snap_plot.setData(spectrum)
            self.ui.SpectrumSnapCalib.setChecked(False)
            self.ui.SpectrumSnapCalib.setStyleSheet('color:black')
            
    def StaticSpectrumStatisticsRecieved(self,spectrum_stats):
        if self.ui.Spectrometer_Acquisition.isChecked() and self.ui.Spectrometer_Spectrum_Live.isChecked() and not self.Spec_Measurement_underway:
             self.static_statistics_spec_plot.plot(spectrum_stats, clear=True)
             
    def ThunderSnapSpecTab(self):
        self.core.snap_image()
        time.sleep(100e-3)
        self.tagged_image = self.core.get_tagged_image()
        self.pixels = np.reshape(self.tagged_image.pix,(self.roi_size_camera,self.roi_size_camera))
        self.ThunderSnapped_SpecTab_image_view.setRange(QtCore.QRectF(0,0, self.roi_size_camera, self.roi_size_camera))
        self.ThunderSnappedImage_forSpecTab.setImage(self.pixels)
        
    def Setup_timefile(self):
        self.number_of_segments = int(self.ui.Set_Number_of_Epochs.text())
        self.current_seg_no=0
        self.delaytimes = []
        self.ui.Current_Epoch_Number.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
        self.ui.Current_Epoch_Number.display(self.current_seg_no+1)

    def Setup_timefile_2(self):
        self.number_of_segments = int(self.ui.Set_Number_of_Epochs_2.text())
        self.current_seg_no=0
        self.delaytimes = []
        self.ui.Current_Epoch_Number_2.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
        self.ui.Current_Epoch_Number_2.display(self.current_seg_no+1)
        
    def Add_Epoch(self):
         if self.current_seg_no <self.number_of_segments:
            if self.ui.Delay_type_linear.isChecked():
                self.delaytimes = np.append(self.delaytimes,np.linspace(float(self.ui.Delay_startpoint.text()),float(self.ui.Delay_endpoint.text()),int(self.ui.Number_of_delaypoints.text())))
            if self.ui.Delay_type_log.isChecked():
                print('called')
                self.delaytimes = np.append(self.delaytimes,np.logspace(np.log10(float(self.ui.Delay_startpoint.text())),np.log10(float(self.ui.Delay_endpoint.text())),int(self.ui.Number_of_delaypoints.text())))
            self.current_seg_no+=1
            self.ui.Current_Epoch_Number.display(self.current_seg_no)
            print(self.delaytimes)
            print('called 2')
            self.ui.Add_Epoch.setChecked(False)
         if self.current_seg_no ==self.number_of_segments:
             self.delaytimes = np.unique(np.asarray(self.delaytimes))
             self.ui.Start_Measurement.setCheckable(True)
             self.ui.Start_Measurement.setStyleSheet('color:orange')
             print(self.delaytimes)
             print('called 1')
             
    def Add_Epoch_2(self):
         if self.current_seg_no <self.number_of_segments:
            if self.ui.Delay_type_linear_2.isChecked():
                self.delaytimes = np.append(self.delaytimes,np.linspace(float(self.ui.Delay_startpoint_2.text()),float(self.ui.Delay_endpoint_2.text()),int(self.ui.Number_of_delaypoints_2.text())))
            if self.ui.Delay_type_log_2.isChecked():
                print('called')
                self.delaytimes = np.append(self.delaytimes,np.logspace(np.log10(float(self.ui.Delay_startpoint_2.text())),np.log10(float(self.ui.Delay_endpoint_2.text())),int(self.ui.Number_of_delaypoints_2.text())))
            self.current_seg_no+=1
            self.ui.Current_Epoch_Number_2.display(self.current_seg_no)
            print(self.delaytimes)
            print('called 2')
            self.ui.Add_Epoch_2.setChecked(False)
         if self.current_seg_no ==self.number_of_segments:
             self.delaytimes = np.unique(np.asarray(self.delaytimes))
             self.ui.Start_Measurement_2.setCheckable(True)
             self.ui.Start_Measurement_2.setStyleSheet('color:orange')
             print(self.delaytimes)
             print('called 1')
             
    def Measure_Spectra(self):
        self.temp_path_measurement =  self.ui.Measurement_path_2.text() + '/' + self.ui.MeasurementName_2.text()
        self.measurement_comments = self.ui.MeasurementComments_2.text()
        self.spec_measurement_no_of_sweeps = int(self.ui.Number_of_sweeps_2.text())
        self.spec_measurement_no_of_avgs = int(self.ui.Number_of_averages_2.text())
        self.spec_measurement_no_of_timepoints = self.delaytimes.shape[0]
        self.im_meas_avg = np.zeros((self.spec_measurement_no_of_avgs,self.roi_size_camera))
        self.im_meas_data = np.zeros((self.spec_measurement_no_of_sweeps,self.spec_measurement_no_of_timepoints,self.roi_size_camera))
        self.i_sweep = 0
        self.i_time = 0
        self.i_avgs = 0
        self.spec_meas_data =np.zeros((self.spec_measurement_no_of_sweeps,self.spec_measurement_no_of_timepoints,1024))
        self.stage_moved = False
        self.Spec_Measurement_underway =  True
        #SpectrallyResolvedMeasurement(self)
    
    def SpectrallyResolvedMeasurement(self,dTT_spec):
        if self.Spec_Measurement_underway is True:
            print('underway')
            
            self.spec_thread.no_of_avgs_spec = self.spec_measurement_no_of_avgs
            'Room Light Background block pump and probe'
            'Pre time zero PL background'
            if self.stage_moved is False:                    
                if  self.ui.HighNA_NewportStage_Box_2.isChecked() == True:
                    longdelay_highNA.MovetoTime(self.delaytimes[self.i_time ] +self.global_time_zero_highNAnewport)
                    while not longdelay_highNA.MotionDone():
                        pass
                    self.ui.CurrentDelay_2.display(np.round(longdelay_highNA.ReturnTime(),1)-self.global_time_zero_highNAnewport)
                if self.ui.Cryo_NewportStage_Box_2.isChecked() == True:
                    longdelay_cryo.MovetoTime(self.delaytimes[self.i_time ] + self.global_time_zero_cryo)
                    while not longdelay_cryo.MotionDone():
                        pass
                    self.ui.CurrentDelay_2.display(np.round(longdelay_cryo.ReturnTime(),1)-self.global_time_zero_cryo)
                if self.ui.PIStage_Box_2.isChecked() == True:
                    PI_shortstage.MovetoTime(self.delaytimes[self.i_time ] +self.global_time_zero_shortstage)
                    self.ui.CurrentDelay_2.display(np.round(PI_shortstage.ReturnTime(),1)  - self.global_time_zero_shortstage)
                    while not PI_shortstage.MotionDone():
                        pass
                    
                self.stage_moved = True
                self.spec_thread.disp_counter_spec = 0
                self.spec_meas_data[self.i_sweep,self.i_time,:] = dTT_spec
                
                if hasattr(self, 'spec_wavelengths'):
                    dTT_spec = np.transpose(np.asarray( [self.spec_wavelengths,dTT_spec]))
                    
                self.DTT_spec_plot_spec.setData(self.spec_meas_data[self.i_sweep,self.i_time,:])
                self.stage_moved = False
                print('Sweep number = ',self.i_sweep, 'Timepoint = ', self.delaytimes[self.i_time], ' fs')
                self.i_time +=1
                self.ui.MeasurementProgressBar_2.setValue((self.i_time + (self.i_sweep*self.spec_measurement_no_of_timepoints))/(self.spec_measurement_no_of_sweeps*self.spec_measurement_no_of_timepoints)*100)
    
            if self.i_time == self.spec_measurement_no_of_timepoints:
                self.i_time =0
                self.stage_moved = False
                if not os.path.exists(self.temp_path_measurement):
                    os.mkdir(self.temp_path_measurement)
                if hasattr(self, 'spec_wavelengths'):
                    self.temp_path_sweep = self.temp_path_measurement +'/'+ self.ui.MeasurementName_2.text() + '_sweep_' +  str(self.i_sweep + 1) +'.wtf'
                    self.sweep_wtf = np.vstack((self.delaytimes,self.spec_meas_data[self.i_sweep,:,:].T))
                    self.wavelengths_wtf = np.insert(self.spec_wavelengths,0,0) 
                    self.wavelengths_wtf = np.expand_dims(self.wavelengths_wtf, axis=0)
                    self.sweep_wtf = np.hstack((self.wavelengths_wtf.T,self.sweep_wtf))
                    np.savetxt(self.temp_path_sweep,self.sweep_wtf)
                self.i_sweep+=1
                
            if self.i_sweep == self.spec_measurement_no_of_sweeps:
                self.ui.MeasurementProgressBar_2.setValue(0)
                if hasattr(self, 'spec_wavelengths'):
                    self.temp_path_sweep = self.temp_path_measurement +'/'+ self.ui.MeasurementName_2.text() + 'Avg.wtf' 
                    self.sweep_wtf = np.vstack((self.delaytimes,np.mean(self.spec_meas_data,axis =0).T))
                    self.wavelengths_wtf = np.insert(self.spec_wavelengths,0,0) 
                    self.wavelengths_wtf = np.expand_dims(self.wavelengths_wtf, axis=0)
                    self.sweep_wtf = np.hstack((self.wavelengths_wtf.T,self.sweep_wtf))
                    np.savetxt(self.temp_path_sweep,self.sweep_wtf)
                
                np.save(self.temp_path_measurement +'/'+ self.ui.MeasurementName_2.text(),self.spec_meas_data)
                self.no_of_avgs_spec = int(self.ui.Shots_to_avg_display_spec.text())
                self.spec_thread.no_of_avgs_spec = self.no_of_avgs_spec
                self.Spec_Measurement_underway = False
                self.ui.Start_Measurement.setStyleSheet('color:black')
                self.ui.Start_Measurement.setCheckable(False)
        
    def Measure_TAM(self):
        if self.ui.Start_Measurement.isChecked():
            self.OpenPumpProbe()
            self.temp_path_measurement =  self.ui.Measurement_path.text() + '/' + self.ui.MeasurementName.text()
            self.measurement_comments = self.ui.MeasurementComments.text()
            self.TAM_measurement_no_of_sweeps = int(self.ui.Number_of_sweeps.text())
            self.TAM_measurement_no_of_avgs = int(self.ui.Number_of_averages.text())
            self.TAM_measurement_no_of_timepoints = self.delaytimes.shape[0]
            #check if the delaytime file has an averages column
            if self.delaytimes.ndim > 1:
                self.TAM_measurement_no_of_timepoints = self.delaytimes.shape[1]
                self.TAM_measurement_no_of_avgs_array = np.array(self.delaytimes[1,:],dtype = int)
                self.TAM_measurement_no_of_avgs_array_max = np.amax(self.TAM_measurement_no_of_avgs_array)
                self.im_meas_avg = np.zeros((self.TAM_measurement_no_of_avgs_array_max,self.roi_size_camera,self.roi_size_camera))
                self.im_meas_avg_on = np.zeros((self.TAM_measurement_no_of_avgs_array_max,self.roi_size_camera,self.roi_size_camera))
                self.im_meas_avg_off = np.zeros((self.TAM_measurement_no_of_avgs_array_max,self.roi_size_camera,self.roi_size_camera))
            else:
                self.im_meas_avg = np.zeros((self.TAM_measurement_no_of_avgs,self.roi_size_camera,self.roi_size_camera))
                self.im_meas_avg_on = np.zeros((self.TAM_measurement_no_of_avgs,self.roi_size_camera,self.roi_size_camera))
                self.im_meas_avg_off = np.zeros((self.TAM_measurement_no_of_avgs,self.roi_size_camera,self.roi_size_camera))
            self.im_meas_data = np.zeros((self.TAM_measurement_no_of_sweeps,self.TAM_measurement_no_of_timepoints,self.roi_size_camera,self.roi_size_camera))
            self.im_meas_data_on = np.zeros((self.TAM_measurement_no_of_sweeps,self.TAM_measurement_no_of_timepoints,self.roi_size_camera,self.roi_size_camera))
            self.im_meas_data_off  = np.zeros((self.TAM_measurement_no_of_sweeps,self.TAM_measurement_no_of_timepoints,self.roi_size_camera,self.roi_size_camera))
            
            if hasattr(self,'measurement_positions'):
                self.number_of_positions = self.measurement_positions.shape[0]
                self.im_meas_data_pos = np.zeros((self.number_of_positions,self.TAM_measurement_no_of_sweeps,self.TAM_measurement_no_of_timepoints,self.roi_size_camera,self.roi_size_camera))
                self.i_pos = 0
                self.measurement_positions_real = np.zeros((self.number_of_positions,2))
                self.measurement_positions_real[self.i_pos,0] = AC.return_x_position()
                self.measurement_positions_real[self.i_pos,1] = AC.return_y_position()
            self.i_sweep = 0
            self.i_time = 0
            self.i_avgs = 0
            self.stage_moved = False
            self.TAM_Measurement_underway =  True
        else:
            self.TAM_Measurement_underway =  False
            
    def Load_TimeFile(self):
        self.temp_path = self.ui.Timefile_path_load.text()
        print(self.temp_path)
        self.delaytimes = np.loadtxt(self.temp_path)
        self.ui.Load_Timefile.setStyleSheet('color:orange')
        self.ui.Start_Measurement.setCheckable(True)
        self.ui.Start_Measurement.setStyleSheet('color:orange')
        
    def Load_PositionFile(self):
        self.temp_path = self.ui.Timefile_path_load_3.text()
        print(self.temp_path)
        self.measurement_positions = np.loadtxt(self.temp_path)
        self.ui.Load_PositionFile.setStyleSheet('color:orange')

    def Save_TimeFile(self):
        self.temp_path = self.ui.Timefile_path_save.text() + '/' + self.ui.Timefile_path_save_name.text()
        print(self.temp_path)
        np.savetxt(self.temp_path,self.delaytimes)
        
    def Load_TimeFile_2(self):
        self.temp_path = self.ui.Timefile_path_load_2.text()
        print(self.temp_path)
        self.delaytimes = np.loadtxt(self.temp_path)
        self.ui.Load_Timefile_2.setStyleSheet('color:orange')
        self.ui.Start_Measurement_2.setCheckable(True)
        self.ui.Start_Measurement_2.setStyleSheet('color:orange')

    def Save_TimeFile_2(self):
        self.temp_path = self.ui.Timefile_path_save_2.text() + '/' + self.ui.Timefile_path_save_name_2.text()
        print(self.temp_path)
        np.savetxt(self.temp_path,self.delaytimes)
        
    def SpecCalibSnap(self):
        if  self.ui.SpectrumSnapCalib.isChecked():
            self.spec_thread.emit_spectrum = True
            self.ui.SpectrumSnapCalib.setStyleSheet('color:green')
        else:
            self.spec_thread.emit_spectrum = False
            self.ui.SpectrumSnapCalib.setStyleSheet('color:black')

    def SpecCalibFindPeak(self):
        self.peakpix_calib = np.argmax(self.calib_snapped_spectra[10:-10])
        self.ui.PeakPixel.clear()
        self.ui.PeakPixel.insert(str(self.peakpix_calib))
        self.calib_peak_line.setValue(self.peakpix_calib)
    
    def SpecCalibAddpoint(self):
        self.calib_wavelengths = np.append(self.calib_wavelengths, float(self.ui.Current_Wavelength.text()))
        self.calib_pixels = np.append(self.calib_pixels, self.calib_peak_line.value())
        self.spec_calib_points.setData(self.calib_pixels, self.calib_wavelengths, symbol = 'o')
        
    def SpecCalibFitCalib(self):
        self.spec_calib_fit = np.polyfit(self.calib_pixels,self.calib_wavelengths,2)
        self.spec_pixels = np.arange(0,1024,step =1)
        self.spec_wavelengths = self.spec_calib_fit[0]*self.spec_pixels**2 + self.spec_calib_fit[1]*self.spec_pixels +self.spec_calib_fit[2]
        self.spec_calib_plot_fit.setData(self.spec_pixels, self.spec_wavelengths ,clear = False,pen = ('r'))
        
    def SpecCalibLoadFile(self):
        self.temp_path = self.ui.Calib_loadPath.text()
        print(self.temp_path)
        self.spec_wavelengths = np.loadtxt(self.temp_path)
        
    def SpecCalibSaveFile(self):
        self.temp_path = self.ui.Calib_savepath.text() + '/' + self.ui.Calib_savename.text()
        print(self.temp_path)
        np.savetxt(self.temp_path,self.spec_wavelengths)

    def OpenZPositioner(self):
        if self.ui.OpenZ.isChecked():
            Z_controller.initialise()
            self.z_pos = Z_controller.return_z_position(0)
            self.ui.z_voltage_display.display(self.z_pos)
            #Z_controller.openport()
            self.ui.OpenZ.setStyleSheet('color:green')
        else:
            Z_controller.close()
            self.ui.OpenZ.setStyleSheet('color:red')
            
    def OpenPumpProbe(self):
        self.ui.PumpShutter.setChecked(True)
        self.ui.ProbeShutter.setChecked(True)
        self.ShutterPump()
        self.ShutterProbe()
        
    def CloseWLStages(self):
        self.ui.Vis_Stage_Shutter.setChecked(False)
        self.ui.NIR_Stage_Shutter.setChecked(False)
        self.ui.Blue_Stage_Shutter.setChecked(False)
        self.ShutterVis()
        self.ShutterNIR()
        self.ShutterBlue()
        
    "Methods for Cryo control"
    # initially find the gfsf, tes, tves and print them out
    # initially have the set point as 294
    # initially have manual controls
    # initially set the room temps/ hum to 0 if no input
    
    def CryoSetup(self)->None:
        p, u = MC.gas.gfsf
        self.ui.Current_GFSF.display(float(p))
        p1, u1 = MC.gas.gear
        self.ui.Current_GEAR.display(float(p1))
        p2, u2 = MC.gas.tes
        self.ui.Current_GEAR.display(float(p2))
        p3, u3 = MC.gas.tves
        self.ui.Current_GEAR.display(float(p3))
        # if :# if temp probe is connected
        #     self.tr = 
        #     self.ts =
        #     self.h =
        # else:# if not connected
        #     tr = 0
        #     ts = 0
        #     h = 0
        #     self.ui.Current_RoomTemp.display(tr)
        #     self.ui.Current_SurfaceTemp.display(0)
        #     self.ui.Current_Humidity.display(h)
        #     td = tr -22 + 0.2*h
        #     self.ui.Current_DewTemp.display(td)
        #     if td < ts:
        #         self.ui.Current_DewTemp.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
        tr = 0
        ts = 0
        h = 0
        self.ui.Current_RoomTemp.display(tr)
        self.ui.Current_SurfaceTemp.display(0)
        self.ui.Current_Humidity.display(h)
        td = tr -22 + 0.2*h
        self.ui.Current_DewTemp.display(td)
        if td < ts:
            self.ui.Current_DewTemp.setStyleSheet("""QLCDNumber { background-color: red; color: white; }""")
            
    def DisplayLiveCryoSpectrum(self)->None:
        if self.ui.Live_cryo.isChecked():
            self.ui.Live_cryo.setStyleSheet('color:green')
        else:
            self.ui.Live_cryo.setStyleSheet('color:black')

    def ChangeSetPoint(self)->None:
        self.SetPoint = float(self.ui.Set_SetPoint.text()) 
        if 3.5 < self.SetPoint < 400:
            MC.temp.loop_tset = self.SetPoint
            # how to clear this?
            
    def ChangeFlowPoint(self)->None:
        self.FlowPoint = float(self.ui.Set_FlowPoint.text()) 
        if 0 <= self.FlowPoint <= 100:
            MC.temp.loop_fset = self.FlowPoint
            
    def ChangeHeatPoint(self)->None:
        self.HeatPoint = float(self.ui.Set_HeatPoint.text()) 
        if 0 <= self.HeatPoint <= 100:
            MC.temp.loop_hset = self.HeatPoint
             
    def ChangeGFSF(self)->None:
        self.GFSF = float(self.ui.Set_GFSF.text())  
        MC.gas.gfsf = self.GFSF
        p, u = MC.gas.gfsf
        self.ui.Current_GFSF.display(float(p))
        self.ui.Set_GFSF.clear()
    
    def ChangeGear(self)->None:
        self.Gear = float(self.ui.Set_Gear.text())  
        MC.gas.gear = self.Gear
        p, u = MC.gas.gear
        self.ui.Current_Gear.display(float(p))
        self.ui.Set_Gear.clear()
    
    def ChangeTVES(self)->None:
        self.TVES = float(self.ui.Set_TVES.text())  
        MC.gas.tves = self.TVES
        p, u = MC.gas.tves
        self.ui.Current_TVES.display(float(p))
        self.ui.Set_TVES.clear()
   
    def ChangeTES(self)->None:
        self.TES = float(self.ui.Set_TES.text())  
        MC.gas.tes = self.TES
        p,u = MC.gas.tes
        self.ui.Current_TES.display(float(p))
        self.ui.Set_TES.clear()
        
    def ChangeP(self)->None:
        self.Prop = float(self.ui.Set_P)
        MC.temp.loop_p = self.Prop
        p, u = MC.temp_loop_p
        self.ui.Current_P.display(float(p))

    def ChangeI(self)->None:
        self.Int = float(self.ui.Set_I)
        MC.temp.loop_i = self.Int
        p, u = MC.temp_loop_i
        self.ui.Current_I.display(float(p))    
    
    def ChangeD(self)->None:
        self.Diff = float(self.ui.Set_D)
        MC.temp.loopdp = self.Diff
        p, u = MC.temp_loop_d
        self.ui.Current_D.display(float(p))
        
    def TempLCD(self)->None:
        p, u = MC.temp.temp
        self.ui.Current_Temp.display(float(p))
        
    def FlowLCD(self)->None:
        p, u = MC.gas.perc
        self.ui.Current_Flow.display(float(p))
         
    def HeatLCD(self)->None:
        p, u = MC.heater.volt
        self.ui.Current_Heat.display(float(p))
        
    def TempPoint(self)->None:
        p, u = MC.temp.loop_tset
        self.ui.Current_SetPoint.display(float(p))
        
    def FlowPoint(self)->None:
        p, u = MC.temp.loop_fset
        self.ui.Current_SetPoint.display(float(p))
        
    def HeatPoint(self)->None:
        p, u = MC.temp.loop_hset
        self.ui.Current_SetPoint.display(float(p))
        
    def GasControl(self)->None:
        if self.ui.AutoFlow.isChecked():
            MC.temp.loop_faut = 'ON'
        if self.ui.ManualFlow.isChecked():
            MC.temp.loop_faut = 'OFF'

    def HeatControl(self)->None:
        if self.ui.AutoHeat.isChecked():
            MC.temp.loop_enab = 'ON'
        if self.ui.ManualHeat.isChecked():
            MC.temp.loop_enab = 'OFF'
    
    
'Defining a thread for the asynch spectrometer acquisition'
    
class FastSpectrometerAcqThread(QtCore.QThread):
    dTT_avg = QtCore.pyqtSignal(np.ndarray)
    spectrum = QtCore.pyqtSignal(np.ndarray)
    spectrum_stats = QtCore.pyqtSignal(np.ndarray)
    def __init__(self,no_of_avgs_spec):
        super().__init__()
        print('Initialising Silicon Software FrameGrabber')
        self.emit_dTT = False
        self.emit_spectrum = False
        self.cleanup_framegrabber = False
        self.boardId = 0
        self.applet = 'DualLineGray16'
        self.camPort = s.PORT_A
        self.no_of_frozen_spectra = 0
        
        self.fg = s.Fg_InitEx(self.applet, self.boardId, 0);
        s.Fg_loadConfig(self.fg,"C:\PyRunTAM\SpecPy\pump-probe.mcf")
        "Initialise the global variables for the spectrometer"
        #Define the aquisition parameters
        self.width_spec =2048
        self.height_spec = 4
        self.samplePerPixel_spec = 1
        self.bytePerSample_spec = 1
        self.nbBuffers_spec = 20000
        self.display_averaging_index_= 0
        self.totalBufferSize_spec = self.width_spec * self.height_spec * self.samplePerPixel_spec * self.bytePerSample_spec * self.nbBuffers_spec
        self.nrOfPicturesToGrab_spec = s.GRAB_INFINITE
        self.rep_rate_spec = 5000
        self.disp_counter_spec =0
        self.no_of_avgs_spec = no_of_avgs_spec
        
        "Initialise the framegrabber runtime variables"
        
        self.cur_pic_nr_spec = 0
        self.last_pic_nr_spec=0
        self.i_spec = 0
        self.spec_on = np.zeros((self.no_of_avgs_spec,1024))
        self.spec_off = np.zeros((self.no_of_avgs_spec,1024))
        self.spec_dtt_spec = np.zeros(1024)
        self.spectrum_spec = np.zeros(1204)
        self.spectrum_stats_spec = np.zeros(1204)
        self.img_spec = "will point to last grabbed image"
        self.nImg_spec = "will point to Numpy image/matrix"
        self.memHandle_spec = s.Fg_AllocMemEx(self.fg, self.totalBufferSize_spec, self.nbBuffers_spec)
        self.err = s.Fg_AcquireEx(self.fg,self.camPort, self.nrOfPicturesToGrab_spec, s.ACQ_STANDARD, self.memHandle_spec)

    
    def run(self):
        while self.cleanup_framegrabber is False:
            self.disp_counter_spec = 0
            while self.disp_counter_spec < self.no_of_avgs_spec:
                #Catch a change in the nuber of averages
                if self.no_of_avgs_spec != np.shape(self.spec_on)[0]:
                    self.spec_on = np.zeros((self.no_of_avgs_spec,1024))
                    self.spec_off = np.zeros((self.no_of_avgs_spec,1024))
                    self.disp_counter_spec = 0
                self.cur_pic_nr_spec = s.Fg_getLastPicNumberBlockingEx(self.fg, self.last_pic_nr_spec + 1, self.camPort, 5, self.memHandle_spec)
                self.last_pic_nr_spec = self.cur_pic_nr_spec
                self.spectrum_stack = s.Fg_getImagePtrEx(self.fg, self.last_pic_nr_spec, self.camPort, self.memHandle_spec)
                self.nspectrum_stack = s.getArrayFrom(self.spectrum_stack, self.width_spec,self.height_spec)
                self.spec_on[self.disp_counter_spec,:] = np.mean(self.nspectrum_stack [:2,1::2]*2**8 + self.nspectrum_stack [:2,0::2],axis =0)
                self.spec_off[self.disp_counter_spec,:] = np.mean(self.nspectrum_stack [2:,1::2]*2**8 + self.nspectrum_stack [2:,0::2],axis =0)
                self.disp_counter_spec+=1
            self.spec_dtt = np.mean(self.spec_on,axis =0)/np.mean(self.spec_off,axis =0) -1
            self.spectrum_spec = np.mean((self.spec_on + self.spec_off),axis = 0)
            self.spectrum_stats_spec = np.std((self.spec_on + self.spec_off),axis = 0)
            if self.emit_dTT:
                self.dTT_avg.emit(self.spec_dtt)
            if self.emit_spectrum:
                self.spectrum.emit(self.spectrum_spec)
                self.spectrum_stats.emit(self.spectrum_stats_spec)
            self.disp_counter_spec = 0
        if (self.fg != None):
            s.Fg_stopAcquire(self.fg, self.camPort)
            s.Fg_FreeMemEx(self.fg, self.memHandle_spec)
            s.Fg_FreeGrabber(self.fg)
            
            
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
        