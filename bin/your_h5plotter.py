#!/usr/bin/env python3

import argparse
import logging
import os

import h5py
import matplotlib
import numpy as np
import pandas as pd
import pylab as plt
from matplotlib import gridspec
from scipy.signal import detrend
from tqdm import tqdm

os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
matplotlib.use('Agg')


def plot_h5(h5_file, save=True, detrend_ft=True, publication=False):
    """
    Plot the h5 candidate file
    :param h5_file: Address of the candidate h5 file
    :param save: Argument to save the plot
    :param detrend_ft: Optional argument to detrend the frequency-time array
    :param publication: Make publication quality plots
    :return:
    """
    with h5py.File(h5_file, 'r') as f:
        to_print = []
        for key in f.attrs.keys():
            to_print.append(f'{key} : {f.attrs[key]}\n')
        str_print = ''.join(to_print)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot candidate h5 files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f', '--files', help='h5 files to be plotted', nargs='+', required=False)
    parser.add_argument('-c', '--results_csv', help='Plot positives in results.csv', required=False)
    parser.add_argument('--publish', help='Make publication quality plots', action='store_true')
    values = parser.parse_args()

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'

    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

    if values.files:
        for files in tqdm(values.files):
            plot_h5(files, save=True, detrend_ft=True, publication=values.publish)
    elif values.results_csv:
        df = pd.read_csv(values.results_csv)
        h5_files = list(df['candidate'][df['label'] == 1])
        for files in tqdm(h5_files):
            plot_h5(files, save=True, detrend_ft=True, publication=values.publish)
    else:
        raise ValueError(f"Need either --files or --results_csv argument.")
