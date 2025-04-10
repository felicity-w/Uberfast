# GHOST Spectrometer
# Connect to OceanHDX
import numpy as np
from typing import List 
from oceandirect.od_logger import od_logger
from oceandirect.OceanDirectAPI_2 import OceanDirectAPI, OceanDirectError,  FeatureID, Spectrometer

od = OceanDirectAPI()
usb_device_count = 0
usb_device_ids = []

def connect_devices()-> (int,List[int]):
    usb_device_count = od.find_usb_devices()
    usb_device_ids = od.get_device_ids()
    if usb_device_count == 0:
        print("No device found.")
    else:
        for id in usb_device_ids:
            device       = od.open_device(id)
            serialNumber = device.get_serial_number()
            device.details()
    return usb_device_count, usb_device_ids

def assign_device()->Spectrometer:
    if usb_device_count == 0:
        print("No devices to assign.")
    else:
        for id in usb_device_ids:
            return od.open_device(id)

def disconnect_devices()-> (int,List[int]):
    if usb_device_count == 0:
        print("No devices to close.")
    else:
        for id in usb_device_ids:
            ser_no = od.get_serial_number(id)
            print("Closing device: %s \n" % ser_no)
            od.close_device(id)
    return 0, []

def set_trigger_mode(device:Spectrometer, mode:int)->None:
    device.set_trigger_mode(mode)

def get_int_time(device:Spectrometer )-> int:
    return device.get_integration_time()

def get_dev_spectrum(device:Spectrometer)->np.ndarray:
    try:
        print('For an integration time of %i ms on %s.' % (device.get_integration_time(), device.get_serial_number()))
        intensity = np.array(device.get_formatted_spectrum())
        wavelengths = np.array(device.get_wavelengths())
        # print(intensity.shape)
        # length = device.get_formatted_spectrum_length()
        # spectra = np.zeros((length, 2), dtype=float)
        # spectra[:,0] = wavelengths
        # spectra[:,1] = intensity
        spectra = np.column_stack((wavelengths, intensity))
        return spectra
    except OceanDirectError as e:
        [errorCode, errorMsg] = e.get_error_details()
        print("get_spec_formatted(device): exception / %d = %s" % (errorCode, errorMsg))
        
def save_spec_as_csv(spectra: np.ndarray)->None:
    np.savetxt('spectra.csv', spectra, delimiter=',')

def get_spec_raw_with_meta(device, sn):
    try:
        print("[START] Reading spectra for dev s/n = %s" % sn, flush=True)
        for i in range(10):
            spectra = []
            timestamp = []
            total_spectra = device.Advanced.get_raw_spectrum_with_metadata(spectra, timestamp, 3)

            print("len(spectra) =  %d" % (total_spectra) )

            #print sample count on each spectra 
            for x in range(total_spectra):
                print("spectraWithMetadata: %d ==>  %d, %d, %d, %d" % (timestamp[x], spectra[x][100], spectra[x][101], spectra[x][102], spectra[x][103]))
    except OceanDirectError as e:
        [errorCode, errorMsg] = e.get_error_details()
        print("get_spec_raw_with_meta(device): exception / %d = %s" % (errorCode, errorMsg))

usb_device_count, usb_device_ids = connect_devices()
if len(usb_device_ids)>0:
    HDX_spec = assign_device()

def get_spectrum()->np.ndarray:
    try:
        device = HDX_spec
        # print('For an integration time of %i ms on %s.' % (device.get_integration_time(), device.get_serial_number()))
        intensity = np.array(device.get_formatted_spectrum())
        wavelengths = np.array(device.get_wavelengths())
        # print(intensity.shape)
        # length = device.get_formatted_spectrum_length()
        # spectra = np.zeros((length, 2), dtype=float)
        # spectra[:,0] = wavelengths
        # spectra[:,1] = intensity
        spectra = np.column_stack((wavelengths, intensity))
        return spectra
    except OceanDirectError as e:
        [errorCode, errorMsg] = e.get_error_details()
        print("get_spec_formatted(device): exception / %d = %s" % (errorCode, errorMsg))
    
def get_intensity()->np.ndarray:
    try:
        device = HDX_spec
        intensity = np.array(device.get_formatted_spectrum())
        return intensity
    except OceanDirectError as e:
        [errorCode, errorMsg] = e.get_error_details()
        print("get_spec_formatted(device): exception / %d = %s" % (errorCode, errorMsg))

def set_int_time(time:int)->None:
    """!
     t must be in milli seconds
    """
    device = HDX_spec
    device.set_integration_time(time*1000)
    
def get_int_time()->int:
    """!
     convert t to be in milli seconds
    """
    device = HDX_spec
    itime = int(device.get_integration_time()/1000)
    return itime
    
def get_all_wl()->np.ndarray:
    device = HDX_spec
    wavelengths = np.array(device.get_wavelengths())
    return wavelengths
    
    

# if __name__ == '__main__':
#     usb_device_count, usb_device_ids = connect_devices()
#     if len(usb_device_ids)>0:
#         HDX_spec = assign_device()
#         print(HDX_spec.get_integration_time())
#         HDX_spec.set_integration_time(100*1000)
#         print('here')
#         # save_spec_as_csv(get_dev_spectrum(HDX_spec))
#         #set_trigger_mode(HDX_spec,0)
#     print('noids@)')
#     # usb_device_count, usb_device_ids = disconnect_devices()
#     # print("**** exiting program ****")
