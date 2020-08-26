#!/usr/bin/env python3
"""
Combines the two frequency bands for data 
from the Mock Spectrometer

Original C code: https://github.com/demorest/psrfits_utils/blob/master/combine_mocks.c
"""

import argparse
import glob
import logging
import os
from datetime import datetime

import astropy.io.fits as pyfits
import numpy as np
import tqdm

from your import Your
from your.formats.pysigproc import SigprocFile

logger = logging.getLogger(__name__)


def calc_skipchan(lowband_obj, upband_obj):
    '''
    Calculate the number of frequency channels to 
    skip from top of lower and bottom of upper 
    frequency bands
    :param lowband_obj: Your object for the lower frequency band
    :param upband_obj: Your object for the upper frequency band
    '''
    assert lowband_obj.bw / lowband_obj.nchans == upband_obj.bw / upband_obj.nchans
    logger.debug(f'Calculating number of frequency channels to skip in upper and lower band.')
    df = lowband_obj.bw / lowband_obj.nchans
    upperfreqoflower = lowband_obj.chan_freqs.max()
    lowerfreqofupper = upband_obj.chan_freqs.min()
    nextfromlower = upperfreqoflower + np.abs(df)
    numchandiff = int(np.round((nextfromlower - lowerfreqofupper) / np.abs(df)))
    chanskip = numchandiff if numchandiff > 0 else 0
    (upchanskip, lowchanskip) = (chanskip // 2, chanskip // 2 + 1) if chanskip % 2 else (chanskip // 2, chanskip // 2)

    if upchanskip % 2 == 1:  # Not needed now, but added for historic reasons.
        upchanskip += 1
        lowchanskip -= 1

    logger.debug(f'Number of frequency channels to skip in upper band are {upchanskip}')
    logger.debug(f'Number of frequency channels to skip in lower band are {lowchanskip}')
    return upchanskip, lowchanskip


def read_and_combine_subint(lowband_obj, upband_obj, fsub, upchanskip, lowchanskip):
    '''
    Reads data for a subint for both bands, applies
    scales and offsets, rescale the scales and offsets
    according to mean ratio of the overlapping channels
    from the two bands, and returns combined data
    :param lowband_obj: Your object for the lower frequency band
    :param upband_obj: Your object for the upper frequency band
    :fsub: subint to read
    :upchanskip: Lower channels to skip from the upperband
    :lowchanskip: Upper channels to skip from the lower band
    :return data: Combined data for the input subint 
    '''
    lowsub_data = lowband_obj.read_subint(fsub, apply_weights=False, apply_scales=False, apply_offsets=False)
    lowsub_scales = lowband_obj.get_scales(fsub)[:lowband_obj.nchan]
    lowsub_offsets = lowband_obj.get_offsets(fsub)[:lowband_obj.nchan]

    upsub_data = upband_obj.read_subint(fsub, apply_weights=False, apply_scales=False, apply_offsets=False)
    upsub_scales = upband_obj.get_scales(fsub)[:upband_obj.nchan]
    upsub_offsets = upband_obj.get_offsets(fsub)[:upband_obj.nchan]

    logger.debug(f'Read data, scales and offset of subint {fsub} from upper and lower band.')

    if any(lowsub_offsets[lowchanskip:]) and any(upsub_offsets[:upchanskip]):
        offsetfactor = np.mean(lowsub_offsets[lowchanskip:]) / np.mean(upsub_offsets[:upchanskip])
    else:
        offsetfactor = 1
    scalefactor = np.mean(lowsub_scales[lowchanskip:]) / np.mean(upsub_scales[:upchanskip])

    logger.debug(f'Applying scales, offset and weights to lower band data.')
    lowsub_data *= lowsub_scales
    lowsub_data += lowsub_offsets
    lowsub_data *= lowband_obj.get_weights(fsub)[:lowband_obj.nchan]

    logger.debug(f'Applying scales, offset and weights to upper band data, and rescaling scales and offsets.')
    upsub_data *= upsub_scales * scalefactor
    upsub_data += upsub_offsets * offsetfactor
    upsub_data *= upband_obj.get_weights(fsub)[:upband_obj.nchan]

    logger.debug(f'Combining data from relevant channels from upper and lower bands')
    # Note freq are not exactly same in the two subbands. Assuming fch1 and channel_bandwidth from lower band.
    # The exact freq in upperband will vary
    data = np.flip(np.concatenate((lowsub_data[:, :-lowchanskip], upsub_data[:, upchanskip:]), axis=1), axis=1)

    if lowband_obj.nbits == 16:
        data -= np.mean(data)
        data /= np.std(data)
        data *= np.sqrt(2 ** 16)
        data += 2 ** 15
        data = np.round(data)
        data = np.clip(data, 0, 2 ** 16 - 1)
        return data.astype('uint16')
    elif lowband_obj.nbits == 8:
        data -= np.mean(data)
        data /= np.std(data)
        data *= np.sqrt(2 ** 8)
        data += 2 ** 7
        data = np.round(data)
        data = np.clip(data, 0, 2 ** 8 - 1)
        return data.astype('uint8')
    else:
        return data


def make_sigproc_obj(filfile, lowband_obj, nchan, fch1, foff):
    '''
    Use Your class object of the lower band to make Sigproc
    class object with the relevant parameters
    :param filfile: Name of the Filterbank file
    :param lowband_obj: Your object for the lower frequency band
    :param nchan: Number of channels in the combined data
    :param fch1: Frequency of the first channel
    :return fil_obj: Sigproc class object
    '''
    logger.debug(f'Generating Sigproc object')
    fil_obj = SigprocFile()

    logger.debug(f'Setting attributes of Sigproc object from Your object.')
    fil_obj.rawdatafile = filfile
    fil_obj.source_name = lowband_obj.your_header.source_name

    # Verify the following parameters
    fil_obj.machine_id = 0  # since mock isn't a machine in the standard list, we use fake
    fil_obj.barycentric = 0  # by default the data isn't barycentered
    fil_obj.pulsarcentric = 0
    fil_obj.telescope_id = 1  # its always Arecibo
    fil_obj.data_type = 0

    fil_obj.nchans = nchan  # lowband_obj.your_header.nchans * 2 - lowchanskip - upchanskip
    fil_obj.foff = foff
    fil_obj.fch1 = fch1
    fil_obj.nbeams = 1
    fil_obj.ibeam = 0
    fil_obj.nbits = lowband_obj.your_header.nbits
    fil_obj.tsamp = lowband_obj.your_header.tsamp
    fil_obj.tstart = lowband_obj.your_header.tstart
    fil_obj.nifs = 1  # always write single pol should use "lowband_obj.your_header.npol" if needed otherwise

    from astropy.coordinates import SkyCoord
    loc = SkyCoord(lowband_obj.your_header.ra_deg, lowband_obj.your_header.dec_deg, unit='deg')
    ra_hms = loc.ra.hms
    dec_dms = loc.dec.dms

    fil_obj.src_raj = float(f'{int(ra_hms[0]):02d}{int(np.abs(ra_hms[1])):02d}{np.abs(ra_hms[2]):07.4f}')
    fil_obj.src_dej = float(f'{int(dec_dms[0]):02d}{int(np.abs(dec_dms[1])):02d}{np.abs(dec_dms[2]):07.4f}')

    fil_obj.az_start = -1
    fil_obj.za_start = -1
    return fil_obj


def write_fil(data, lowband_obj, upband_obj, filename=None, outdir=None):
    '''
    Write Filterbank file given the upper and lower band Your 
    objects and combined data
    :param lowband_obj: Your object for the lower frequency band
    :param upband_obj: Your object for the upper frequency band
    :param upband_obj: Your object for the upper frequency band
    :param data: Combined data from two bands 
    :param filename: Output name of the Filterbank file
    :param outdir: Output directory for the Filterbank file
    '''

    original_dir, orig_lowband_basename = os.path.split(lowband_obj.your_header.filename)
    if not filename:
        filename = '.'.join(orig_lowband_basename.split('.')[:-3]) + '.fil'

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
            nchan = data.shape[1]
            fch1 = upband_obj.chan_freqs.max()
            foff = lowband_obj.foff if lowband_obj.foff < 0 else -1 * lowband_obj.foff
            fil_obj = make_sigproc_obj(filfile, lowband_obj, nchan, fch1, foff)
            fil_obj.write_header(filfile)
            logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
            fil_obj.append_spectra(data, filfile)

    except FileNotFoundError:
        nchan = data.shape[1]
        fch1 = upband_obj.chan_freqs.max()
        foff = lowband_obj.foff if lowband_obj.foff < 0 else -1 * lowband_obj.foff
        fil_obj = make_sigproc_obj(filfile, lowband_obj, nchan, fch1, foff)
        fil_obj.write_header(filfile)
        logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
        fil_obj.append_spectra(data, filfile)
    logger.info(f'Successfully written data to Filterbank file: {filfile}')


def combine(f1, f2, nstart=0, nsamp=100, outdir=None, filfile=None):
    '''
    combines data from two subbands from Mock spectrometer 
    and writes out a Filterbank file.
    :param f1: List of files from one subband
    :param f2: List of files from other subband
    :param nstart: Starting sample
    :param nsamp: number of samples to read
    :param outdir: Output directory for Filterbank file
    :param filfile: Name of the Filterbank file to write to
    '''
    y1 = Your(f1)
    y2 = Your(f2)
    (lowband_obj, upband_obj) = (y1, y2) if y1.chan_freqs.max() < y2.chan_freqs.max() else (y2, y1)
    del y1
    del y2

    if lowband_obj.foff < 0 or upband_obj.foff < 0:
        raise AttributeError('Negative channel_bandwidth in Mock fits not supported.')

    low_header = vars(lowband_obj.your_header)
    up_header = vars(upband_obj.your_header)
    for key in low_header.keys():
        if key == 'filelist' or key == 'filename' or key == 'center_freq' or key == 'fch1':
            continue
        elif key == 'ra_deg' or key == 'dec_deg' or key == 'gl' or key == 'gb':
            hpbw = 57.3 * 3 * 10 ** 8 / (low_header['center_freq'] * 10 ** 6 * 200)  # deg
            if np.abs(low_header[key] - up_header[key]) > 0.1 * hpbw:
                raise ValueError(f'Value of {key} in the two bands differ by more than 10% FWHM')
            else:
                continue

        if low_header[key] != up_header[key]:
            raise ValueError(f'Values of {key} are different in the two bands')

    if len(low_header['filelist']) != len(up_header['filelist']):
        raise ValueError(f'Number of files are different in the two bands.')

    upchanskip, lowchanskip = calc_skipchan(lowband_obj, upband_obj)

    if nsamp == -1:
        nsamp = lowband_obj.nspectra

    # Calculate starting subint and ending subint
    startsub = int(nstart / lowband_obj.nsamp_per_subint)
    skip = int(nstart - (startsub * lowband_obj.nsamp_per_subint))
    endsub = int((nstart + nsamp) / lowband_obj.nsamp_per_subint)
    trunc = int(((endsub + 1) * lowband_obj.nsamp_per_subint) - (nstart + nsamp))

    cumsum_num_subint = np.cumsum(lowband_obj.specinfo.num_subint)
    startfileid = np.where(startsub < cumsum_num_subint)[0][0]
    assert startfileid < len(lowband_obj.filelist)

    if startfileid != lowband_obj.fileid:
        lowband_obj.fileid = startfileid
        upband_obj.fileid = startfileid

        logger.debug(f'Updating fileid of lower and upper band to {lowband_obj.fileid} and {upband_obj.fileid}')

        lowband_obj.fits.close()
        upband_obj.fits.close()

        del lowband_obj.fits['SUBINT']
        del upband_obj.fits['SUBINT']

        logger.debug("Deleted mmap'ed object")

        lowband_obj.filename = lowband_obj.filelist[lowband_obj.fileid]
        logger.debug(f"Loweband file id is {lowband_obj.fileid}, Reading file: {lowband_obj.filename}")

        upband_obj.filename = upband_obj.filelist[upband_obj.fileid]
        logger.debug(f"Upperband file id is {upband_obj.fileid}, Reading file: {upband_obj.filename}")

        lowband_obj.fits = pyfits.open(lowband_obj.filename, mode='readonly', memmap=True)
        upband_obj.fits = pyfits.open(upband_obj.filename, mode='readonly', memmap=True)

    # Read data
    logger.debug(f"Startsub {startsub}, endsub {endsub}")
    for isub in tqdm.tqdm(range(startsub, endsub + 1), desc=f'Subint'):
        logger.debug(f"isub is {isub}")
        logger.debug(f"lowband file id is {lowband_obj.fileid}")
        logger.debug(f"upperband file id is {upband_obj.fileid}")

        if isub > cumsum_num_subint[lowband_obj.fileid] - 1:
            logger.debug(f'isub lies in a later file')
            lowband_obj.fits.close()
            upband_obj.fits.close()

            del lowband_obj.fits['SUBINT']
            del upband_obj.fits['SUBINT']

            logger.debug("Delted mmap'ed object")
            lowband_obj.fileid += 1
            upband_obj.fileid += 1

            if lowband_obj.fileid == len(lowband_obj.filelist):
                logger.warn(f"Not enough subints, returning data till last subint")
                logger.debug(f'Setting file ID to that of last file')
                lowband_obj.fileid -= 1
                upband_obj.fileid -= 1
                break
            logger.debug(f"Updating lowerband file ID to: {lowband_obj.fileid}")
            logger.debug(f"Updating upperband file ID to: {upband_obj.fileid}")

            lowband_obj.filename = lowband_obj.filelist[lowband_obj.fileid]
            logger.debug(f"Reading lowband file: {lowband_obj.filename}")

            upband_obj.filename = upband_obj.filelist[upband_obj.fileid]
            logger.debug(f"Reading upperband file: {upband_obj.filename}")

            lowband_obj.fits = pyfits.open(lowband_obj.filename, mode='readonly', memmap=True)
            upband_obj.fits = pyfits.open(upband_obj.filename, mode='readonly', memmap=True)

        logger.debug(f"Using: {lowband_obj.fits} and {upband_obj.fits}")
        fsub = int((isub - np.concatenate([np.array([0]), cumsum_num_subint]))[lowband_obj.fileid])
        logger.debug(f'Reading subint {fsub} in file {lowband_obj.filename} and {upband_obj.filename}')

        try:
            data = read_and_combine_subint(lowband_obj, upband_obj, fsub, upchanskip, lowchanskip)
        except KeyError:
            logger.warn(f"Encountered KeyError, maybe mmap'd object was delected")
            logger.debug(f"Trying to open files {lowband_obj.filename} and {upband_obj.filename}")

            lowband_obj.fits = pyfits.open(lowband_obj.filename, mode='readonly', memmap=True)
            upband_obj.fits = pyfits.open(upband_obj.filename, mode='readonly', memmap=True)

            logger.debug(f'Reading subint {fsub} in files {lowband_obj.filename} and {upband_obj.filename}')

            data = read_and_combine_subint(lowband_obj, upband_obj, fsub, upchanskip, lowchanskip)

        if skip != 0 and isub == startsub:
            data = data[skip:, :]

        if isub == endsub:
            if trunc > 0:
                data = data[:-trunc, :]
            else:
                raise ValueError("Number of bins to truncate is negative: %d" % trunc)

        if data.shape[1] == 958:
            logger.debug(
                f'Final number of frequency channels is {data.shape[1]}, padding the data to make 960 channels.')
            data = np.pad(data, [(0, 0), (0, 960 - data.shape[1])], 'constant', constant_values=np.mean(data[:, -1]))

        logger.info(f'Writing data from subint {fsub} to filterbank')
        write_fil(data, lowband_obj, upband_obj, outdir=outdir, filename=filfile)
        logger.debug(f'Successfully written data from subint {fsub} to filterbank')

    logging.debug(f'Read all the necessary subints')


def all_files(direct, nstart, nsamp, outdir):
    names = {}
    direct = os.path.join(direct, '')
    outdir = os.path.join(outdir, '')
    logger.debug('Looking for file pairs.')
    for af in glob.glob(direct + "*.fits"):
        base_name = os.path.basename(af)
        split = base_name.split('.')
        file_one = direct + split[0] + '.' + split[1] + '.' + split[2] + '.' + split[3][0:2] + 's0' + split[3][
                                                                                                      4:6] + '.*.fits'
        file_two = direct + split[0] + '.' + split[1] + '.' + split[2] + '.' + split[3][0:2] + 's1' + split[3][
                                                                                                      4:6] + '.*.fits'
        out_file = split[0] + '.' + split[1] + '.' + split[2] + '.' + split[1] + '.' + split[3][0:2] + split[3][
                                                                                                       4:6] + '.fil'
        names[out_file] = [file_one, file_two]
    logger.info(f'Found {len(names.keys())} file pairs, combing.')
    for out in names:
        combine(glob.glob(names[out][0]), glob.glob(names[out][1]), nstart=values.nstart, nsamp=values.nsamp,
                outdir=outdir, filfile=out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='your_combine_mocks.py',
                                     description="Combine two bands from mock spectrometer to a filterbank file.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    parser.add_argument('-f1', '--first_band', help='Path of files containing one band', required=False, type=str)
    parser.add_argument('-f2', '--second_band', help='Path of files containing second band', required=False, type=str)
    parser.add_argument('-s', '--nstart', type=int, help='Start sample number', default=0)
    parser.add_argument('-n', '--nsamp', type=int, help='Number of samples to read (-1: whole file)',
                        default=-1, required=False)
    parser.add_argument('-o', '--outdir', type=str, help='Output directory for Filterbank file', default='.',
                        required=False)
    parser.add_argument('-fil', '--fil_name', type=str, help='Output name of the Filterbank file', default=None,
                        required=False)
    parser.add_argument('-a', '--all_files', type=str, help='Process all files in the given directory', default=None,
                        required=False)
    values = parser.parse_args()

    logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
    log_filename = values.outdir + '/' + datetime.utcnow().strftime('combine_mocks_%Y_%m_%d_%H_%M_%S_%f.log')

    if values.verbose:
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(filename=log_filename, level=logging.INFO, format=logging_format)

    if values.all_files:
        all_files(values.all_files, nstart=values.nstart, nsamp=values.nsamp, outdir=values.outdir)
    elif not (values.first_band and values.second_band):
        print('The following arguments are required: -f1/--first_band, -f2/--second_band OR -a/--all_files')
    else:
        combine(glob.glob(values.first_band), glob.glob(values.second_band), nstart=values.nstart, nsamp=values.nsamp,
                outdir=values.outdir, filfile=values.fil_name)
