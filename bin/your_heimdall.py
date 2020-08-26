#!/usr/bin/env python3

import argparse
import json
import logging
import os
from datetime import datetime
from multiprocessing import Process

import numpy as np

from your import Your
from your.formats import dada
from your.utils.heimdall import HeimdallManager
from your.utils.misc import MyEncoder
from your.utils.plotter import save_bandpass
from your.utils.rfi import savgol_filter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='your_heimdall.py', description="Your Heimdall Fetch FRB",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-p', '--probability', help='Detection threshold', default=0.5, type=float)
    parser.add_argument('-f', '--files', help='filterbank or psrfits', nargs='+')
    parser.add_argument('-dm', '--dm', help='DM (eg -dm 10 1000)', type=float, nargs=2, default=[10, 1000])
    parser.add_argument('-g', '--gpu_id', help='GPU ID to run heimdall on', type=int, required=False, default=0)
    parser.add_argument('-sg', '--apply_savgol', help='Apply savgol filter to zap bad channels', action='store_true')
    parser.add_argument('-frequency_window', '--filter_window', help='Window size (MHz) for savgol filter',
                        required=False,
                        default=15, type=float)
    parser.add_argument('-sigma', '--sigma', help='Sigma for the savgol filter', required=False, default=6, type=float)
    parser.add_argument('-m', '--mask', help='Input RFI mask (could be 1-D bad channel mask or 2-D FT mask)',
                        required=False, type=str,
                        default=None)
    parser.add_argument('-dm_tol', '--dm_tol', help='SNR loss tolerance between DM trials', required=False,
                        type=float, default=1.25)
    parser.add_argument('-rfi_no_narrow', '--rfi_no_narrow', help='disable narrow band RFI excision', required=False,
                        action='store_true', default=False)
    parser.add_argument('-rfi_no_broad', '--rfi_no_broad', help='disable 0-DM RFI excision', required=False,
                        action='store_true', default=False)
    parser.add_argument('-o', '--output_dir', help='Output dir for heimdall candidates', type=str, required=False,
                        default=None)
    parser.add_argument('--no_progress', help='Do not show the tqdm bar', action='store_true', default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = "{0}/{1}".format(os.getcwd(), ('.').join(
            os.path.basename(args.files[0]).split('.')[:-1]))
        os.makedirs(args.output_dir, exist_ok=True)

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
    log_filename = args.output_dir + '/' + datetime.utcnow().strftime('your_heimdall_%Y_%m_%d_%H_%M_%S_%f.log')

    if args.verbose:
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=logging_format)
        logging.debug("Using debug mode")
    else:
        logging.basicConfig(filename=log_filename, level=logging.INFO, format=logging_format)

    logging.info("Input Arguments:-")
    for arg, value in sorted(vars(args).items()):
        logging.info("%s: %r", arg, value)

    your_object = Your(file=args.files)
    max_delay = your_object.dispersion_delay(dms=np.max(args.dm))
    dispersion_delay_samples = np.ceil(max_delay / your_object.your_header.tsamp)
    logging.info(f"Max Dispersion delay = {max_delay} s")
    logging.info(f"Max Dispersion delay = {dispersion_delay_samples} samples")

    nsamps_gulp = int(np.max([(2 ** np.ceil(np.log2(dispersion_delay_samples))), 2 ** 18]))

    your_dada = dada.YourDada(your_object)
    your_dada.setup()

    if args.apply_savgol:
        bandpass = your_object.bandpass(nspectra=8192)
        mask = savgol_filter(bandpass, your_object.your_header.foff, frequency_window=args.filter_window,
                             sigma=args.sigma)
        chan_nos = np.arange(0, bandpass.shape[0], dtype=np.int)
        bad_chans = list(chan_nos[mask])

        save_bandpass(your_object, bandpass, chan_nos=chan_nos, mask=mask, outdir=args.output_dir + '/')

        kill_mask_file = args.output_dir + '/' + your_object.your_header.basename + '.bad_chans'
        with open(kill_mask_file, 'w') as f:
            np.savetxt(f, chan_nos[mask], fmt='%d', delimiter=' ', newline=' ')
    elif args.mask:
        logging.info(f'Reading RFI mask from {args.mask}')
        mask = np.loadtxt(args.mask)
        if len(mask.shape) == 1:
            bad_chans = list(mask)
        elif len(mask.shape) == 2:
            sk_mask = mask
            bad_chans = None
        else:
            logging.warning('RFI mask not understood, can only be 1D or 2D. Not using RFI flagging.')
            bad_chans = None
    else:
        logging.info('No RFI flagging done.')
        bad_chans = None

    HM = HeimdallManager(dm=args.dm, dada_key=your_dada.dada_key, boxcar_max=int(32e-3 / your_object.your_header.tsamp),
                         verbosity='v', nsamps_gulp=nsamps_gulp, gpu_id=args.gpu_id, output_dir=args.output_dir,
                         zap_chans=bad_chans, rfi_no_broad=args.rfi_no_broad, rfi_no_narrow=args.rfi_no_narrow,
                         dm_tol=args.dm_tol)

    with open(args.output_dir + '/' + your_object.your_header.basename + '_heimdall_inputs.json', 'w') as fp:
        json.dump(HM.__dict__, fp, cls=MyEncoder, indent=4)

    dada_process = Process(name='To dada', target=your_dada.to_dada, args=(args.no_progress,))
    heimdall_process = Process(name='Heimdall', target=HM.run)

    dada_process.start()
    heimdall_process.start()

    try:
        heimdall_process.join()
        dada_process.join()
    except KeyboardInterrupt:
        heimdall_process.terminate()
        dada_process.terminate()

    your_dada.teardown()
    logging.info("Destroyed dada buffers")
