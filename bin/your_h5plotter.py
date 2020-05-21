#!/usr/bin/env python3

import argparse
import logging
import os
from multiprocessing import Pool

import matplotlib
import pandas as pd
import pylab as plt
from tqdm import tqdm
from functools import partial

from your.utils.plotter import get_params, plot_h5

os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
matplotlib.use('Agg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot candidate h5 files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f', '--files', help='h5 files to be plotted', nargs='+', required=False)
    parser.add_argument('-c', '--results_csv', help='Plot positives in results.csv', required=False)
    parser.add_argument('--publish', help='Make publication quality plots', action='store_true')
    parser.add_argument('-mad','--mad_filter', help='Median Absolute Deviation spectal clipper, default 3 sigma', nargs='?', const=3.0, default=False)
    parser.add_argument('-n', '--nproc', help='Number of processors to use in parallel (default: 4)',
                        type=int, default=4, required=False)

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
            for i, _ in tqdm(enumerate(p.imap_unordered(func, h5_files, chunksize=2))):
                pbar.update()
