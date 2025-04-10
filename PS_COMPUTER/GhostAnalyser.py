# GHOST Analyser
# import spectrometer spectrogram and FFT and plot them
import numpy as np
import mathplotlib as plt

spectra = np.loadtxt('C:\\Data\\GHOSTs\\GhostBuster_Spectrum.dat')
spectro = np.loadtxt('C:\\Data\\GHOSTs\\GhostBuster_spectrogram.dat', skiprows=1)
FFT = np.loadtxt('C:\\Data\\GHOSTs\\GhostBuster_spectrum_ghost.dat', skiprows =1)
spectro_info = np.genfromtxt('C:\\Data\\GHOSTs\\GhostBuster_spectrogram.dat', max_rows=1) # lowest wl, highest wl, wl step size, time step size
FFT_info = np.genfromtxt('C:\\Data\\GHOSTs\\GhostBuster_spectrum_ghost.dat', max_rows =1) # lowest wl, highest wl, wl step size, freq step size

























