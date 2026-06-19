import math
import numpy as np
import pandas as pd
from df_functions import *
import argparse
import matplotlib.pyplot as plt
import glob, os
from scipy.integrate import quad
from scipy.optimize import curve_fit

parser = argparse.ArgumentParser(description="dealing with combined timestream")
parser.add_argument('--prefix','-p',type=str,default=None,help="Will go into figure titles and names")
parser.add_argument('--outdir','-o',type=str,default=None,help="Output directory and path to data files")
parser.add_argument('--file', '-f', type=str, default=None, help="Save statistic results from voltage vs time data to a text file.")
args=parser.parse_args()

df_list = []   # list of indiv dataframes
df = {}        # all files dataframe
fs_arr = []
namelist = []  # used in plotting
df_comb = {}   # big timestream dataframe
ffto = {}

files = glob.glob(f"{args.outdir}*.mat")
print(f"There are {len(files)} files to load")

for f in files:
    name = os.path.basename(f).replace(f".mat", "") 
    namelist.append(name)
    df[name],t_int = mat_to_df(f)
    #print(f"Loaded {f}") 
    
    # Get individual sample rates #   
    fs_arr.append(1/t_int)  # in Hz

    # Build combined dataframe (for big timestream) #
    df_list.append(df[name])
    
# check all sample freqs are the same #
fs_arr = np.asarray(fs_arr).ravel()
if not np.allclose(fs_arr, fs_arr[0]):
    bad_ind = np.where(fs_arr != fs_arr[0])[0]
    bad_file = namelist[bad_ind]
    raise ValueError(f"Error: not all sample frequencies are the same. Review {bad_file}")

df_comb = comb_df(df_list,t_int)

# get data statistics #
voltage = df_comb['Channel B'].values
time = df_comb['Time'].values
nan_vol_ind = df[name][df[name]['Channel B'].isna()].index.tolist()

print(f"NaN indices: {nan_vol_ind}")

voltage = np.delete(voltage, nan_vol_ind)
time = np.delete(time, nan_vol_ind)

rms = np.sqrt(np.mean(voltage**2))
var = np.std(voltage)

if args.file:
    with open(args.file, 'a') as f:
         f.write("Filename,RMS[mV],1sig[mV]\n")
         f.write(f"{name},{rms},{var}\n")

# Histogram and gaussian fit of voltage #

low_bound = 0.05 #mV
up_bound  = 0.8
SPE_volt = [v for v in voltage if low_bound <= v <= up_bound]

nbins = 1000
bkgcounts = 1500

## [amp,mean,var]
#initial = [3000,0.2,0.1]
initial = [12000,0.18,0.15,2000,0.18,0.15]

for k in range(1,6):
    counts,bin_edges=np.histogram(SPE_volt,bins=k*50)
   
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    
    p1,pcov,infodict,mesg,ier = curve_fit(signal2,bin_centers,counts,p0=initial,full_output=True,maxfev=1000000)
    

    if ier not in (1,2,3,4):
        print("Solutiuon was not found")
        print(mesg)
    else:
        print(f"Soultion found for {k*50} bins")
        print(p1)
    
    xarr = np.linspace(bin_edges[0],bin_edges[-1],100000)
    yarr = signal2(xarr,*p1) 

    yarr_gaus1 = gaussian(xarr,p1[0],p1[1],p1[2])
    yarr_gaus2 = gaussian(xarr,p1[3],p1[4],p1[5])
    ymat = np.column_stack([yarr_gaus1,yarr_gaus2])

    plt.figure(layout='constrained')
    plt.stairs(counts,bin_edges)
    plt.plot(xarr,yarr,'r-')
    plt.xlabel('Voltage [mV]')
    plt.ylabel('Counts')
    #plt.text(0.2,10000,f'amp = {amp_fit:.5f} counts')
    plt.title(f'{args.prefix} Voltage Histogram')
    plt.xlim(0,1.0)
    plt.savefig(f'{args.outdir}/plots/fithistogram_{args.prefix}_{k*50}bins.png')

    plt.figure(layout='constrained')
    plt.stairs(counts,bin_edges)
    plt.plot(xarr,ymat)
    plt.xlabel('Voltage [mV]')
    plt.ylabel('Counts')
    plt.title(f'{args.prefix} Voltage Histogram with decomposed fit')
    plt.xlim(0,1.0)
    plt.savefig(f'{args.outdir}/plots/fithistogram_decomposed_{args.prefix}_{k*50}bins.png')

print("Done!")
