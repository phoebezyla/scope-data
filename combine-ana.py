import numpy as np
import pandas as pd
from df_functions import *
import argparse
import matplotlib.pyplot as plt
import glob, os


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

#files = glob.glob(f"{args.prefix}*.mat")
files = glob.glob(f"{args.outdir}*.mat")
#print(files)
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

# Start plotting #
print("Plotting timestream...")
plt.figure(figsize=(50,3),layout='constrained')
plt.plot(1e3*df_comb['Time'],df_comb['Channel B'],'-',linewidth=0.2)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [mV]')
plt.title(f'{args.prefix} Timestream')
plt.savefig(f"{args.outdir}/plots/voltime_{args.prefix}.png")
plt.close

print("Plotting spectrogram...")
vmin= -150
vmax= -80
Fs = 1/2e-9 # Hz
plt.figure(figsize=(12,4),layout='constrained')
pxx,freqs,bins,im = plt.specgram(df_comb['Channel B'],
    Fs=Fs,cmap='plasma',vmin=vmin,vmax=vmax,scale='dB')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [ks]')
plt.title(f'Combined {args.prefix} spectrogram')
plt.colorbar(im, label='Power/Frequency [dB/Hz]')
plt.savefig(f'{args.outdir}/plots/spec_{args.prefix}.png')
plt.close

print("Plotting logy spectrogram...")
plt.figure(figsize=(12,4),layout='constrained')
pxx,freqs,bins,im = plt.specgram(df_comb['Channel B'],
    Fs=Fs,cmap='plasma',vmin=vmin,vmax=vmax,scale='dB')
plt.ylabel('Frequency [Hz]')
plt.yscale('log')
plt.ylim(bottom=freqs[1])
plt.xlabel('Time [ks]')
plt.title(f'Combined {args.prefix} spectrogram')
plt.colorbar(im, label='Power/Frequency [dB/Hz]')
plt.savefig(f'{args.outdir}/plots/speclog_{args.prefix}.png')
plt.close


print('Plotting loglog FFT...')
df_comb['Channel B'] = df_comb['Channel B'].interpolate().ffill().bfill()
                # interpolates over any NaN entries in the data
voltage = df_comb['Channel B'].values
arr_len = len(voltage)
freq_fft = np.fft.rfftfreq(arr_len, d=1/Fs)
vals_fft = np.fft.rfft(voltage)
mag_fft = 20 * np.log10(np.abs(vals_fft).clip(min=1e-10))
                # converts to dB to be consistent w spectogram (& picoscope)
                # clip changes any values = 0 to 1e-10, so the log10 later doesn't break
ffto = {
    'freq': freq_fft,
    'mag': mag_fft
}
 
n_pts = len(ffto['freq'])
stride = max(1, n_pts // 10000)
plt.figure(layout='constrained')
plt.loglog(ffto['freq'][::stride]/1e6, ffto['mag'][::stride])
plt.xlabel('Frequency [MHz]')
plt.ylabel('Magnitude [dB]')
plt.title(f"{args.prefix} FFT")
plt.grid(True)
plt.savefig(f'{args.outdir}/plots/fftlog_{args.prefix}.png')


# get data statistics #
voltage = df_comb['Channel B'].values
time = df_comb['Time'].values
nan_vol_ind = df[name][df[name]['Channel B'].isna()].index.tolist()

print(f"NaN indices: {nan_vol_ind}")

voltage = np.delete(voltage, nan_vol_ind)
time = np.delete(time, nan_vol_ind)

rms = np.sqrt(np.mean(voltage**2))
var = np.std(voltage)

print(f"  Votlage RMS: {rms:.4f} mV")
print(f"  Voltage 1sigma: {var:.4f} mV")

if args.file:
    with open(args.file, 'a') as f:
         f.write("Filename,RMS[mV],1sig[mV]\n")
         f.write(f"{name},{rms},{var}\n")

# check how often we cross thresholds #
thresholds = (rms+var, rms+2*var, rms+3*var, rms+4*var, rms+5*var)

for thresh in thresholds:
    ups, downs = count_cross(voltage,thresh)
    print(f" Voltage goes above  {thresh:.4f} mV {ups} times.")
    print(f"              below -{thresh:.4f} mV {downs} times.")
    if args.file:
        with open(args.file, 'a') as f:
            f.write("Threshold, upward crosses, negative threshold, downward crosses")
            f.write(f"\n{thresh:.4f} {ups} -{thresh:.4f} {downs}\n")

# Histogram of voltage #
for k in range(1,4):
    plt.figure(layout='constrained')
    plt.hist(voltage,bins=100*k,rwidth=1)
    plt.xlim(0.1,1.0)
    plt.xlabel('Voltage [mV]')
    plt.ylabel('Counts')
    plt.title(f'{args.prefix} Voltage Histogram')
    plt.savefig(f'{args.outdir}/plots/histogram_{args.prefix}_{k}00bins.png')

print("Done!")
