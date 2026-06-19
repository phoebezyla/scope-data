# scope-data
The data, scripts, and plots to go with the SWGO lab's picoscope

## Scripts

### `df_functions.py`
Functions for other .py scripts to use
&emsp;#### `mat_to_df(f)`
&emsp;Takes .mat file f and builds a dataframe with time and voltage information. Time interval is set to 2 ns. Voltage in is mV, time is in s. 
&emsp;Returns pd.datafram({'Time':time, 'Channel B': voltage}), tinterval

#### &emsp;&emsp;`comb_df(dflist,tint)`
&emsp;&emsp;Builds one dataframe from list of dataframes. 

#### &emsp;&emsp;`count_cross(arr, threshold)`
&emsp;&emsp;Counts the number of times array arr has a rising edge that crosses threshold,
&emsp;&emsp;and the number of times arr has a falling edge that crosses -threshold. 
&emsp;&emsp;Returns upward_cross, downward_cross

#### &emsp;&emsp;`gaussian(x,amp,mean,var`
&emsp;&emsp;A gaussian distribution function

#### &emsp;`poisson(k,mean)`
&emsp;&emsp;A poisson distribution function

#### &emsp;&emsp;`tail(x,decay)`
&emsp;&emsp;An exponential decay function. For x-> 0 at infinity, decay should be positive. 

#### &emsp;&emsp;`signal(x,amp0,amp1,amp2,mean0,mean1,mean2,var0,var1,var2,decay)`
&emsp;&emsp;The sum of three gaussian functions and one exponential decay function. 

#### &emsp;&emsp;`signal2(x,amp0,mean0,var0,amp1,mean1,var1)`
&emsp;&emsp;The sum of two gaussian functions. 


### `charge-ana.py`
Input --outdir = directory with .mat files. 

Input --prefix = name you want files saved under and in title of plots

Input --file   = name (including .txt) of file you want statistic results saved to

Combines information from each file in --outdir inbto one dataframe, and builds a histogram of the voltage information. Fits signal2 to the histogram, and makes two plots: the histograsm with the full fit overlaid, and the histogram with the decomposed fir overlaid. 

### `combine_ana.py`
Input = directory with .mat files. 

Combines information from each file into one timestream of data, and plots voltage vs time, spectrogram (normal and log-y),a loglog FFT, and a histogram of the voltage. 

Also determines RMS and variance of the voltage, and the number of times n sigma (for n = 1,2,3,4,5) is crossed. Can optionally save RMS, variance, thresholds, and threshold crosses to a specified .txt files. 

## Data

### `dark-061726-02/`
~1.2 seconds of data recorded on June 17, 2026. Dark signal (HV on, LED off) at 1400 V.

Has subdirectory `plots/`. As of Fri 6/19, all plots are made.

### `dark-061926/`
Data recorded on June 19, 2026. Dark signal at 1400 V.

Has subdirectroy `plots/`. Plots still need to be made.


P. Zyla 6-19-26
