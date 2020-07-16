#!/usr/bin/env python3
"""
Converts files in PSRFITS format
to Filterbank format and combines
them into a single file.

"""

import argparse
import logging
import os
from datetime import datetime

import numpy as np
import tqdm

from your import Your
from your.pysigproc import SigprocFile
from your.utils.rfi import sk_filter, savgol_filter

logger = logging.getLogger(__name__)


def make_sigproc_obj(filfile, y, nchans, chan_freq):
    '''
    Use Your class object of the lower band to make Sigproc
    class object with the relevant parameters
    :param filfile: Name of the Filterbank file
    :param y: Your object for the PSRFITS files
    :param nchans: No:of channels in the frequency range
    :param chan_freq: Required frequency channel range
    '''
    logger.debug(f'Generating Sigproc object')
    fil_obj = SigprocFile()

    logger.debug(f'Setting attributes of Sigproc object from Your object.')
    fil_obj.rawdatafile = filfile
    fil_obj.source_name = y.your_header.source_name

    # Verify the following parameters
    fil_obj.machine_id = 0  # use "Fake" for now
    fil_obj.barycentric = 0  # by default the data isn't barycentered
    fil_obj.pulsarcentric = 0
    fil_obj.telescope_id = 6  # use only GBT for now
    fil_obj.data_type = 0

    fil_obj.nchans = nchans
    fil_obj.foff = y.your_header.foff
    fil_obj.fch1 = chan_freq[0]
    fil_obj.nbeams = 1
    fil_obj.ibeam = 0
    fil_obj.nbits = y.your_header.nbits
    fil_obj.tsamp = y.your_header.tsamp
    fil_obj.tstart = y.your_header.tstart
    fil_obj.nifs = 1  # Only use Intensity values

    from astropy.coordinates import SkyCoord
    loc = SkyCoord(y.your_header.ra_deg, y.your_header.dec_deg, unit='deg')
    ra_hms = loc.ra.hms
    dec_dms = loc.dec.dms

    fil_obj.src_raj = float(f'{int(ra_hms[0]):02d}{np.abs(int(ra_hms[1])):02d}{np.abs(ra_hms[2]):07.4f}')
    fil_obj.src_dej = float(f'{int(dec_dms[0]):02d}{np.abs(int(dec_dms[1])):02d}{np.abs(dec_dms[2]):07.4f}')

    fil_obj.az_start = -1
    fil_obj.za_start = -1
    return fil_obj


def write_fil(data, y, nchans=None, chan_freq=None, filename=None, outdir=None):
    '''
    Write Filterbank file given the Your object
    :param data: data to write to the filterbank file
    :param y: Your object for the PSRFITS files
    :param nchans: No:of channels in the frequency range
    :param chan_freq: Required frequency channel range
    :param filename: Output name of the Filterbank file
    :param outdir: Output directory for the Filterbank file
    '''

    original_dir, orig_basename = os.path.split(y.your_header.filename)
    if not filename:
        filename = '_'.join(orig_basename.split('.')[0].split('_')[:-1]) + '.fil'

    if not outdir:
        outdir = original_dir

    filfile = outdir + '/' + filename

    # Add checks for an existing fil file
    logger.info(f'Trying to write data to filterbank file: {filfile}')
    try:
        if os.stat(filfile).st_size > 8192:  # check and replace with the size of header
            logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
            SigprocFile.append_spectra(data, filfile)

        else:
            fil_obj = make_sigproc_obj(filfile, y, nchans, chan_freq)
            fil_obj.write_header(filfile)
            logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
            fil_obj.append_spectra(data, filfile)

    except FileNotFoundError:
        fil_obj = make_sigproc_obj(filfile, y, nchans, chan_freq)
        fil_obj.write_header(filfile)
        logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
        fil_obj.append_spectra(data, filfile)
    logger.info(f'Successfully written data to Filterbank file: {filfile}')


def convert(f, c=None, outdir=None, filfile=None, progress=None, flag_rfi=False, sk_sig=4, sg_fw=15, 
        sg_sig=4, zero_dm_subt=False):
    '''
    reads data from one or more PSRFITS files
    and writes out a Filterbank File.
    :param f: List of PSRFITS files
    :param c: Required frequency channel range
    :param outdir: Output directory for Filterbank file
    :param filfile: Name of the Filterbank file to write to
    :param progress: turn on/off progress bar
    :param flag_rfi: To turn on RFI flagging 
    :param sk_sig: sigma for spectral kurtosis filter
    :param sg_fw: filter window for savgol filter
    :param sg_sig: sigma for savgol filter
    :param zero_dm_subt: enable zero DM rfi excision
    '''
    y = Your(f)
    fits_header = vars(y.your_header)
    if c:
        min_c = int(np.min(c))
        max_c = int(np.max(c))
    else:
        min_c = 0
        max_c = len(y.chan_freqs)

    chan_freq = y.chan_freqs[min_c:max_c]
    nchans = len(chan_freq)

    # Calculate loop of spectra
    interval = 4096 * 24
    if y.your_header.native_nspectra > interval:
        nloops = 1 + y.your_header.native_nspectra // interval
    else:
        nloops = 1
    nstarts = np.arange(0, interval * nloops, interval, dtype=int)
    nsamps = np.full(nloops, interval)
    if y.your_header.native_nspectra % interval != 0:
        nsamps[-1] = y.your_header.native_nspectra % interval

    # Read data
    for nstart, nsamp in tqdm.tqdm(zip(nstarts, nsamps), total=len(nstarts), disable=progress):
        logger.debug(f'Reading spectra {nstart}-{nstart + nsamp} in file {y.filename}')
        data = y.get_data(nstart, nsamp).astype(y.your_header.dtype)
        data = data[:, min_c:max_c]
        if flag_rfi:
            logger.info(f'Applying spectral kurtosis filter with sigma={sk_sig}')
            sk_mask = sk_filter(data, foff=y.your_header.foff, nchans=nchans, tsamp=y.your_header.tsamp, sig=sk_sig)
            bp = data.sum(0)[~sk_mask]
            logger.info(f'Applying savgol filter with fw={sg_fw} and sig={sg_sig}')
            sg_mask = savgol_filter(bp, y.your_header.foff, fw=sg_fw, sig=sg_sig)
            mask = np.zeros(data.shape[1], dtype=np.bool)
            mask[sk_mask] = True
            mask[np.where(mask == False)[0][sg_mask]] = True
            data[:, mask] = 0
        if zero_dm_subt:
            logger.debug('Subtracting 0-DM time series from the data')
            data = data - data.mean(1)[:,None]
        logger.info(
            f'Writing data from spectra {nstart}-{nstart + nsamp} in the frequency channel range {min_c}-{max_c} to filterbank')
        write_fil(data, y, nchans=nchans, chan_freq=chan_freq, outdir=outdir, filename=filfile)
        logger.debug(f'Successfully written data from spectra {nstart}-{nstart + nsamp} to filterbank')

    logging.debug(f'Read all the necessary spectra')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert files from PSRFITS format to a single file in Filterbank"
                                                 "format.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f', '--files',
                        help='Paths of PSRFITS files to be converted to a single file in Filterbank format. Surround '
                             'with quotes, and either use wildcards or separate with spaces',
                        required=True, nargs='+')
    parser.add_argument('-c', '--chans', help='Required channels (eg -c 0 4096)', required=False, type=int, nargs=2,
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
    parser.add_argument('-zero_dm_subt', '--zero_dm_subt', help='Enable 0 DM subtraction', action='store_true', default=False)
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

    convert(f=values.files, c=values.chans, outdir=values.outdir, filfile=values.fil_name, progress=values.no_progress,
            flag_rfi=values.flag_rfi, sk_sig=values.sk_sig, sg_fw=values.sg_fw, sg_sig=values.sg_sig, 
            zero_dm_subt=values.zero_dm_subt)
