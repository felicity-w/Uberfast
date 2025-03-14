# Try the PyPret for Pulse Retrieval
# Input data must be dark subtracted and interpolated first
import numpy as np
#import numba as nb
import scipy as sp
import pyfftw 
#import python-magic as pm
from pypret.benchmarking import benchmark_retrieval, RetrievalResultPlot
import pypret as pp
import h5py 


# ft instance that specifies the temporal and spectral grid, N is size of mesh, dt is temporal step size,dw = 2pi/(N dt)
# pp.fourier.FourierTransform(N, dt=None, dw=None, t0=None, w0=None)

# ultrashot pulse using envelope, ft is ft instance, wl0 is central wavelength
# pp.pulse.Pulse(ft, wl0, unit='wl')

# creates a pnps instance, pulse is pulse object
# pp.pnps.FROG(pulse, process='shg')

# calculates a pnps from a pnps, using different algos
# pp.retrieval.step_retriever.COPRARetriever(pnps, alpha=0.25, **kwargs)
# pp.retrieval.step_retriever.PCGPARetriever(pnps, decomposition='power', **kwargs)
# pp.retrieval.step_retriever.GPARetriever(pnps, step_size='exact', **kwargs)
# pp.retrieval.step_retriever.PIERetriever(pnps, logging=False, verbose=False, **kwargs)

# generate mesh, gives tiem grid and frequency grid the same length
mesh = 300
time_step = 1.06e-15
central_wl = 550e-9
the_ft = pp.FourierTransform(mesh, dt=time_step)
# make pulse, creates an empty array for pulse.spectrum
pulse_1 = pp.Pulse(the_ft, central_wl)
pulse_2 = pp.Pulse(the_ft, central_wl)
# fill spectrum envelope with standard dev
pulse_2.spectrum = pp.lib.gaussian(pulse_2.wl, x0=central_wl+100e-9, sigma=20e-9)
pulse_1.spectrum = pp.lib.gaussian(pulse_1.wl, x0=central_wl, sigma=50e-9)
# create pnps of the FROG pulse
the_pnps = pp.pnps.FROG(pulse_1, "shg")
# then calculate trace using the spectrum
the_pnps.calculate(pulse_1.spectrum, pulse_1.t )
# print the spectrogram
pp.MeshDataPlot(the_pnps.trace)


# set retrieval settings using pcgpa
the_ret = pp.Retriever(the_pnps, "pcgpa", verbose=True, maxiter=300)
# using trace and spectrum retrieve the pulse
the_ret.retrieve(the_pnps.trace, pulse_1.spectrum)
# data from retrieval
the_ret.result(pulse_2.spectrum)
# from benchmarking to compare ret and og
res = benchmark_retrieval(pulse_1, "shg-frog", "pcgpa", repeat=1, verbose=True, maxiter=300, additive_noise=0.01)
rrp = RetrievalResultPlot(res.retrievals[0])

def compare_retrieval(pulse_r :pp.Pulse, pulse_m:pp.Pulse, scheme : str, algo : str, its: int, verb:bool )->None:
    # create pnps, then calc trace, then Retriever, then result with other pulse
    spec_1 = pp.pnps.FROG(pulse_r, "shg")
    spec_1.calculate(pulse_r.spectrum, pulse_r.t)
    ret = pp.Retriever(spec_1, "pcgpa", verbose=True, maxiter=300)
    ret.retrieve(spec_1.trace, pulse_r.spectrum)
    ressie = ret.result(pulse_m.spectrum)
    rtp = RetrievalResultPlot(ressie)

compare_retrieval(pulse_1, pulse_2, "shg-frog", "pcgpa", 1, True)
ppt = pp.PulsePlot(pulse_1) # way to print out the time and wavelength plots
pp.random_gaussian(pulse_2, time_step*30, phase_max=3.141592653589793) #  updates pulse_2 by creating a gaussian with random phases

# this takes in a pulse and makes it noisy
res = benchmark_retrieval(pulse_2, "shg-frog", "pcgpa", initial_guess="random", repeat=1, verbose=True, maxiter=300, additive_noise=0.01)
# This  gives the results of the retrievals together
rrp = RetrievalResultPlot(res.retrievals[0])

tr = np.loadtxt('FROG_trace.dat')
wav = np.loadtxt('wavelength.dat')
wl_range =wav[ len(wav) - 1] -  wav[0]


