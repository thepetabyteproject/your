#!/usr/bin/env python3

import argparse
import logging
import os
from multiprocessing import Pool

import matplotlib
import pandas as pd
import pylab as plt
from tqdm import tqdm
<<<<<<< HEAD
from multiprocessing import Pool
from functools import partial
from scipy import stats
=======

from your.utils.plotter import get_params, plot_h5
>>>>>>> 07ec8071abbeb8b59dd7eb3b0693aabe09e2f115

os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
matplotlib.use('Agg')

<<<<<<< HEAD
def figsize(scale):
    fig_width_pt = 513.17 #469.755                  # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0/72.27                       # Convert pt to inch
    golden_mean = (np.sqrt(5.0)-1.0)/2.0            # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt*inches_per_pt*scale    # width in inches
    fig_height = fig_width*golden_mean              # height in inches
    fig_size = [fig_width,fig_height]
    return fig_size

def smad(freq_time, sigma, clip=True):
    mads = stats.median_absolute_deviation(freq_time, axis=0)
    threshold=1.4826*sigma

    for j,k in enumerate(mads):
        cut = threshold*k
        if clip:
            freq_time[freq_time[:, j]>=cut, j]=cut
            freq_time[freq_time[:, j]<=-cut, j]=-cut
    return freq_time

#plt.rcParams.update(plt.rcParamsDefault)
params = {'backend': 'pdf',
        'axes.labelsize': 10,
        'lines.markersize': 4,
        'font.size': 10,
        'xtick.major.size':6,
        'xtick.minor.size':3,  
        'ytick.major.size':6,
        'ytick.minor.size':3,
        'xtick.major.width':0.5,
        'ytick.major.width':0.5,
        'xtick.minor.width':0.5,
        'ytick.minor.width':0.5,
        'lines.markeredgewidth':1,
        'axes.linewidth':1.2,
        'legend.fontsize': 7,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'savefig.dpi':200,
        'path.simplify':True,
        'font.family': 'serif',
        'font.serif':'Times',
        'text.latex.preamble': [r'\usepackage{amsmath}',r'\usepackage{amsbsy}',
                                r'\DeclareMathAlphabet{\mathcal}{OMS}{cmsy}{m}{n}'],
        'figure.figsize': figsize(0.5)}

plt.rcParams.update(params)


def plot_h5(mad_filter, h5_file, save=True, detrend_ft=True, publication=False):
    """
    Plot the h5 candidate file
    :param h5_file: Address of the candidate h5 file
    :param save: Argument to save the plot
    :param detrend_ft: Optional argument to detrend the frequency-time array
    :param publication: Make publication quality plots
    :return:
    """
    with h5py.File(h5_file, 'r') as f:
        dm_time = np.array(f['data_dm_time'])
        if detrend_ft:
            freq_time = detrend(np.array(f['data_freq_time'])[:, ::-1].T)
        else:
            freq_time = np.array(f['data_freq_time'])[:, ::-1].T
        dm_time[dm_time != dm_time] = 0
        freq_time[freq_time != freq_time] = 0
        freq_time -= np.median(freq_time)
        freq_time /= np.std(freq_time)
        fch1, foff, nchan, dm, cand_id, tsamp, dm_opt, snr, snr_opt, width = f.attrs['fch1'], \
                                                                             f.attrs['foff'], f.attrs['nchans'], \
                                                                             f.attrs['dm'], f.attrs['cand_id'], \
                                                                             f.attrs['tsamp'], f.attrs['dm_opt'], \
                                                                             f.attrs['snr'], f.attrs['snr_opt'], \
                                                                             f.attrs['width']
        if width > 1:
            ts = np.linspace(-128, 128, 256) * tsamp * width * 1000 / 2
        else:
            ts = np.linspace(-128, 128, 256) * tsamp * 1000

        if mad_filter:
            freq_time = smad(freq_time, float(mad_filter))

        plt.clf()

        if publication:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(5, 7), sharex='col')

        else:
            fig = plt.figure(figsize=(15, 8))
            gs = gridspec.GridSpec(3, 2, width_ratios=[4, 1], height_ratios=[1, 1, 1])
            ax1 = plt.subplot(gs[0, 0])
            ax2 = plt.subplot(gs[1, 0])
            ax3 = plt.subplot(gs[2, 0])
            ax4 = plt.subplot(gs[:, 1])
            to_print = []
            for key in f.attrs.keys():
                if 'filelist' in key:
                    pass
                elif 'filename' in key:
                    to_print.append(f'filename : {os.path.basename(f.attrs[key])}\n')
                    to_print.append(f'filepath : {os.path.dirname(f.attrs[key])}\n')
                else:
                    to_print.append(f'{key} : {f.attrs[key]}\n')
            str_print = ''.join(to_print)
            ax4.text(0.2, 0, str_print, fontsize=14, ha='left', va='bottom', wrap=True)
            ax4.axis('off')

        ax1.plot(ts, freq_time.sum(0), 'k-')
        ax1.set_ylabel('Flux (Arb. Units)')
        ax2.imshow(freq_time, aspect='auto', extent=[ts[0], ts[-1], fch1, fch1 + (nchan * foff)], interpolation='none')
        ax2.set_ylabel('Frequency (MHz)')
        ax3.imshow(dm_time, aspect='auto', extent=[ts[0], ts[-1], 2 * dm, 0], interpolation='none')
        ax3.set_ylabel(r'DM (pc cm$^{-3}$)')
        ax3.set_xlabel('Time (ms)')

        plt.tight_layout()
        if save:
            plt.savefig(h5_file[:-3] + '.png', bbox_inches='tight')
        else:
            plt.close()


=======
>>>>>>> 07ec8071abbeb8b59dd7eb3b0693aabe09e2f115
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot candidate h5 files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f', '--files', help='h5 files to be plotted', nargs='+', required=False)
    parser.add_argument('-c', '--results_csv', help='Plot positives in results.csv', required=False)
    parser.add_argument('--publish', help='Make publication quality plots', action='store_true')
<<<<<<< HEAD
    parser.add_argument('-mad','--mad_filter', help='Median Absolute Deviation spectal clipper, default 3 sigma', nargs='?', const=3.0, default=False)
    parser.add_argument('-n', '--nproc', help='Number of processors to use in parallel (default: 4)', 
                type=int, default=4, required=False)
=======
    parser.add_argument('-n', '--nproc', help='Number of processors to use in parallel (default: 4)',
                        type=int, default=4, required=False)
>>>>>>> 07ec8071abbeb8b59dd7eb3b0693aabe09e2f115

    values = parser.parse_args()
    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

    if values.files:
        h5_files = values.files
    elif values.results_csv:
        df = pd.read_csv(values.results_csv)
        h5_files = list(df['candidate'][df['label'] == 1])
    else:
        raise ValueError(f"Need either --files or --results_csv argument.")

    params = get_params()

    plt.rcParams.update(params)

    with Pool(processes=values.nproc) as p:
        max_ = len(h5_files)
        func = partial(plot_h5, values.mad_filter)
        with tqdm(total=max_) as pbar:
<<<<<<< HEAD
            for i, _ in tqdm(enumerate(p.imap_unordered(func, h5_files, chunksize=2))):
=======
            for i, _ in tqdm(enumerate(p.imap_unordered(plot_h5, h5_files, chunksize=2))):
>>>>>>> 07ec8071abbeb8b59dd7eb3b0693aabe09e2f115
                pbar.update()
