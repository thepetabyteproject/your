#!/usr/bin/env python3
"""
Converts files in PSRFITS format
to Filterbank format and combines
them into a single file.

"""

import argparse
import logging
from datetime import datetime

from your import Your
from your.writer import Writer

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='your_fits2fil.py',
                                     description="Convert files from PSRFITS format to a single file in Filterbank"
                                                 "format.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f', '--files',
                        help='Paths of PSRFITS files to be converted to a single file in Filterbank format. Surround '
                             'with quotes, and either use wildcards or separate with spaces',
                        required=True, nargs='+')
    parser.add_argument('-c', '--chans', help='Required channels (eg -c 0 4096)', required=False, type=int, nargs=2,
                        default=None)
    parser.add_argument('-nstart', '--nstart', help='Start spectra number', required=False, type=int, default=None)
    parser.add_argument('-nsamp', '--nsamp', help='Number of spectra to convert', required=False, type=int,
                        default=None)
    parser.add_argument('-o', '--outdir', type=str, help='Output directory for Filterbank file', default='.',
                        required=False)
    parser.add_argument('-fil', '--fil_name', type=str, help='Output name of the Filterbank file', default=None,
                        required=False)
    parser.add_argument('--no_progress', help='Do not show the tqdm bar', action='store_true', default=None)
    parser.add_argument('-r', '--flag_rfi', help='Turn on RFI flagging', action='store_true', default=False)
    parser.add_argument('-sksig', '--sk_sig', help='Sigma for spectral kurtosis filter', type=float, default=4,
                        required=False)
    parser.add_argument('-sgsig', '--sg_sig', help='Sigma for savgol filter', type=float, default=4, required=False)
    parser.add_argument('-sgfw', '--sg_fw', help='Filter window for savgol filter (MHz)', type=float, default=15,
                        required=False)
    parser.add_argument('-zero_dm_subt', '--zero_dm_subt', help='Enable 0 DM subtraction', action='store_true',
                        default=False)
    values = parser.parse_args()

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
    log_filename = values.outdir + '/' + datetime.utcnow().strftime('fits2fil_%Y_%m_%d_%H_%M_%S_%f.log')

    if values.verbose:
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(filename=log_filename, level=logging.INFO, format=logging_format)

    logging.info("Input Arguments:-")
    for arg, value in sorted(vars(values).items()):
        logging.info("Argument %s: %r", arg, value)

    y = Your(values.files)
    w = Writer(y)
    w.to_fil(c=values.chans, nstart=values.nstart, nsamp=values.nsamp, outdir=values.outdir, filfile=values.fil_name,
             progress=values.no_progress, flag_rfi=values.flag_rfi, sk_sig=values.sk_sig, sg_fw=values.sg_fw,
             sg_sig=values.sg_sig, zero_dm_subt=values.zero_dm_subt)
