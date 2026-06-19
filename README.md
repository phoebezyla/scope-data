# scope-data
The data, scripts, and plots to go with the SWGO lab's picoscope

# `df_functions.py`
Functions for other .py scripts to use
`mat_to_df(f)`: Takes .mat file f and builds a dataframe with time and voltage information. Time interval is set to 2 ns. Voltage in is mV, time is in s. 
Returns pd.datafram({'Time':time, 'Channel B': voltage}), tinterval

`comb_df(dflist,tint)`
Builds one dataframe from list of dataframes. 

`count_cross(arr, threshold)`
Counts the number of times array arr has a rising edge that crosses threshold, and the number of times arr has a falling edge that crosses -threshold. 
Returns upward_cross, downward_cross

`gaussian(x,amp,mean,var`
A gaussian distribution function

`poisson(k,mean)`
A poisson distribution function

`tail(x,decay)`
An exponential decay function. For x-> 0 at infinity, decay should be positive. 

`signal(x,amp0,amp1,amp2,mean0,mean1,mean2,var0,var1,var2,decay)`
The sum of three gaussian functions and one exponential decay function. 

`signal2(x,amp0,mean0,var0,amp1,mean1,var1)`
The sum of two gaussian functions. 


# `charge-ana.py`
Input --outdir = directory with .mat files. 

Input --prefix = name you want files saved under and in title of plots

Input --file   = name (including .txt) of file you want statistic results saved to

Combines information from each file in --outdir inbto one dataframe, and builds a histogram of the voltage information. Fits signal2 to the histogram, and makes two plots: the histograsm with the full fit overlaid, and the histogram with the decomposed fir overlaid. 

# `combine_ana.py`
Input = directory with .mat files. 

Combines information from each file into one timestream of data, and plots voltage vs time, spectrogram (normal and log-y),a loglog FFT, and a histogram of the voltage. 

Also determines RMS and variance of the voltage, and the number of times n sigma (for n = 1,2,3,4,5) is crossed. Can optionally save RMS, variance, thresholds, and threshold crosses to a specified .txt files. 
