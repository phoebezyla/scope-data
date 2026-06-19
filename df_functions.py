import numpy as np
import pandas as pd
from scipy import signal
from scipy.io import loadmat 
import os
import math

def mat_to_df(f):
#    print(f)
    d = loadmat(f)
#    print(d)
    length = int(d['Length'][0,0]) #trim 4 extra samples in "B" array
    tstart = float(d['Tstart'][0, 0])
    tinterval = 2e-9 #2 nanoseconds
    #tinterval = float(d['Tinterval'][0, 0])
    voltage = d['B'][:length, 0].astype(float)*1e3  # V -> mV
    vollength = len(voltage)
    time = (tstart + np.arange(vollength) * tinterval) # [s]
    return pd.DataFrame({'Time': time, 'Channel B': voltage}),tinterval


def comb_df(dflist,tint):
    df_big = []
    time_offset = 0.0

    for frame in dflist:
        adjusted = frame.copy()
        adjusted['Time'] = frame['Time'] + time_offset

        time_offset = adjusted['Time'].iloc[-1] + tint
        df_big.append(adjusted)

    return pd.concat(df_big, ignore_index=True)

def count_cross(arr, threshold):
    above = (arr > threshold)
    below = (arr < -threshold)
    upward_cross = np.count_nonzero(np.diff(above.astype(int)) == 1)
    downward_cross = np.count_nonzero(np.diff(below.astype(int)) == 1)

    return upward_cross, downward_cross

def gaussian(x,amp,mean,var):
    #evaluates a normal distribution function
    return amp*np.exp(-((x-mean)**2) / (2*var**2))

def poisson(k,mean):
    #k = number of occurrences
    #mean = mean of the distribution
    k = round(k)
    return ((mean**k)*np.exp(-mean)/math.factorial(k))

def tail(x,decay):
    #exponential tail function
    #x = points at which fxn is evaluated
    #x0 = shape param
    return np.exp(-x*decay)

def signal(x,amp0,amp1,amp2,mean0,mean1,mean2,var0,var1,var2,decay):
    # sum of three gaussian functions & an exponential decay
    # amp, mean, and var are arrays where amp[n] refers to the nth gaussian
    gaussian_combo = gaussian(x,amp0,mean0,var0) + gaussian(x,amp1,mean1,var1) + gaussian(x,amp2,mean2,var2)

    return gaussian_combo + tail(x,decay)

def signal2(x,amp0,mean0,var0,amp1,mean1,var1):
    return gaussian(x,amp0,mean0,var0) + gaussian(x,amp1,mean1,var1)
