#!/usr/bin/env python3

import argparse
import glob
import logging
import os

from your.utils.math import normalise

os.environ['OPENBLAS_NUM_THREADS'] = '1'  # stop numpy multithreading regardless of the backend
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

from multiprocessing import Pool
from datetime import datetime

import numpy as np
import pandas as pd

from your.candidate import Candidate, crop
from your.utils.gpu import gpu_dedisp_and_dmt_crop

logger = logging.getLogger()


def cpu_dedisp_dmt(cand, args):
    pulse_width = cand.width
    if pulse_width == 1:
        time_decimate_factor = 1
    else:
        time_decimate_factor = pulse_width // 2
    logger.debug(f"Time decimation factor {time_decimate_factor}")

    cand.dmtime()
    logger.info('Made DMT')
    if args.opt_dm:
        logger.info('Optimising DM')
        logger.warning('This feature is experimental!')
        cand.optimize_dm()
    else:
        cand.dm_opt = -1
        cand.snr_opt = -1
    cand.dedisperse()
    logger.info('Made Dedispersed profile')

    # Frequency - Time reshaping
    cand.decimate(key='ft', axis=0, pad=True, decimate_factor=time_decimate_factor, mode='median')
    crop_start_sample_ft = cand.dedispersed.shape[0] // 2 - args.time_size // 2
    cand.dedispersed = crop(cand.dedispersed, crop_start_sample_ft, args.time_size, 0)
    logger.info(f'Decimated Time axis of FT to tsize: {cand.dedispersed.shape[0]}')
    # DM-time reshaping
    cand.decimate(key='dmt', axis=1, pad=True, decimate_factor=time_decimate_factor, mode='median')
    crop_start_sample_dmt = cand.dmt.shape[1] // 2 - args.time_size // 2
    cand.dmt = crop(cand.dmt, crop_start_sample_dmt, args.time_size, 1)
    logger.info(f'Decimated DM-Time to dmsize: {cand.dmt.shape[0]} and tsize: {cand.dmt.shape[1]}')
    return cand


def cand2h5(cand_val):
    """
    TODO: Add option to use cand.resize for reshaping FT and DMT
    Generates h5 file of candidate with resized frequency-time and DM-time arrays
    :param cand_val: List of candidate parameters (filename, snr, width, dm, label, tcand(s))
    :type cand_val: Candidate
    :return: None
    """
    filename, snr, width, dm, label, tcand, kill_mask_path, num_files, args, gpu_id = cand_val
    if os.path.exists(str(kill_mask_path)):
        logger.info(f'Using mask {kill_mask_path}')
        kill_chans = np.loadtxt(kill_mask_path, dtype=np.int)
    else:
        logger.debug('No Kill Mask')

    fname, ext = os.path.splitext(filename)
    if ext == ".fits" or ext == ".sf":
        if num_files == 1:
            files = [filename]
        else:
            files = glob.glob(fname[:-5] + '*fits')
            if len(files) != num_files:
                raise ValueError("Number of fits files found was not equal to num_files in cand csv.")
    elif ext == '.fil':
        files = [filename]
    else:
        raise TypeError("Can only work with list of fits file or filterbanks")

    logger.debug(f'Source file list: {files}')
    cand = Candidate(files, snr=snr, width=width, dm=dm, label=label, tcand=tcand, device=gpu_id)
    if os.path.exists(str(kill_mask_path)):
        kill_mask = np.zeros(cand.nchans, dtype=np.bool)
        kill_mask[kill_chans] = True
        cand.kill_mask = kill_mask
    cand.get_chunk()
    if cand.isfil:
        cand.fp.close()

    logger.info('Got Chunk')

    if gpu_id >= 0:
        logger.debug(f"Using the GPU {gpu_id}")
        try:
            cand = gpu_dedisp_and_dmt_crop(cand, device=gpu_id)
        except CudaAPIError:
            logger.info("Ran into a CudaAPIError, using the CPU version for this candidate")
            cand = cpu_dedisp_dmt(cand, args)
    else:
        cand = cpu_dedisp_dmt(cand, args)

    cand.resize(key='ft', size=args.frequency_size, axis=1, anti_aliasing=True, mode='constant')
    logger.info(f'Resized Frequency axis of FT to fsize: {cand.dedispersed.shape[1]}')
    cand.dmt = normalise(cand.dmt)
    cand.dedispersed = normalise(cand.dedispersed)
    fout = cand.save_h5(out_dir=args.fout)
    logger.debug(f"Filesize of {fout} is {os.path.getsize(fout)}")
    if not os.path.isfile(fout):
        raise IOError(f"File with {cand.id} not written")
    if os.path.getsize(fout) < 100 * 1024:
        raise ValueError(f"File with id: {cand.id} has issues! Its size is too less.")
    logger.info(fout)
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='your_candmaker.py',
                                     description="Your candmaker! Make h5 candidates from the candidate csv files",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-fs', '--frequency_size', type=int, help='Frequency size after rebinning', default=256)
    parser.add_argument('-g', '--gpu_id',
                        help='GPU ID (use -1 for CPU). To use multiple GPUs (say with id 2 and 3 use -g 2 3', nargs='+',
                        required=False, default=[-1],
                        type=int)
    parser.add_argument('-ts', '--time_size', type=int, help='Time length after rebinning', default=256)
    parser.add_argument('-c', '--cand_param_file', help='csv file with candidate parameters', type=str, required=True)
    parser.add_argument('-n', '--nproc', type=int, help='number of processors to use in parallel (default: 2)',
                        default=2)
    parser.add_argument('-o', '--fout', help='Output file directory for candidate h5', type=str, default='.')
    parser.add_argument('-opt', '--opt_dm', dest='opt_dm', help='Optimise DM', action='store_true', default=False)
    values = parser.parse_args()

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
    log_filename = values.fout + '/' + datetime.utcnow().strftime('your_candmaker_%Y_%m_%d_%H_%M_%S_%f.log')

    if values.verbose:
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(filename=log_filename, level=logging.INFO, format=logging_format)

    if -1 not in values.gpu_id:
        from numba.cuda.cudadrv.driver import CudaAPIError

        for gpu_ids in values.gpu_id:
            logger.info(f"Using the GPU {gpu_ids}")
        if len(values.gpu_id) > 1:
            from itertools import cycle

            gpu_id_cycler = cycle(range(len(values.gpu_id)))
    else:
        logger.info(f"Using CPUs only")

    cand_pars = pd.read_csv(values.cand_param_file)
    # Randomly shuffle the candidates, this is so that the high DM candidates are spread through out
    # Else they will clog the GPU memory at once
    cand_pars.sample(frac=1).reset_index(drop=True)
    process_list = []
    for index, row in cand_pars.iterrows():
        if len(values.gpu_id) > 1:
            # If there are more than one GPUs cycle the candidates between them.
            gpu_id = gpu_id_cycler.__next__()
        else:
            gpu_id = values.gpu_id[0]
        process_list.append(
            [row['file'], row['snr'], 2 ** row['width'], row['dm'], row['label'], row['stime'],
             row['chan_mask_path'], row['num_files'], values, gpu_id])

    with Pool(processes=values.nproc) as pool:
        pool.map(cand2h5, process_list, chunksize=1)
