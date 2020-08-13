import logging
import os

import numpy as np

from your.pysigproc import SigprocFile

logger = logging.getLogger(__name__)


def make_sigproc_obj(filfile, y, nchans, chan_freq, nstart):
    """
    Use Your class to make Sigproc class object with relevant parameters

    Args:

        filfile: Name of the Filterbank file

        y: Your object for the PSRFITS files

        nchans: No:of channels in the frequency range

        chan_freq: Required frequency channel range


    Returns:

        obj : Object of class SigprocFile

    """
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
    if not nstart:
        nstart = 0
    fil_obj.tstart = y.your_header.tstart + nstart * y.your_header.tsamp / (60 * 60 * 24)
    fil_obj.nifs = 1  # Only use Intensity values

    if y.your_header.ra_deg and y.your_header.dec_deg:
        ra = y.your_header.ra_deg
        dec = y.your_header.dec_deg
    else:
        ra = 0
        dec = 0

    from astropy.coordinates import SkyCoord
    loc = SkyCoord(ra, dec, unit='deg')
    ra_hms = loc.ra.hms
    dec_dms = loc.dec.dms

    fil_obj.src_raj = float(f'{int(ra_hms[0]):02d}{np.abs(int(ra_hms[1])):02d}{np.abs(ra_hms[2]):07.4f}')
    fil_obj.src_dej = float(f'{int(dec_dms[0]):02d}{np.abs(int(dec_dms[1])):02d}{np.abs(dec_dms[2]):07.4f}')

    fil_obj.az_start = -1
    fil_obj.za_start = -1
    return fil_obj


def write_fil(data, y, nchans=None, chan_freq=None, filename=None, outdir=None, nstart=None):
    """
    Write Filterbank file given the Your object

    Args:

        data: data to write to the filterbank file

        y: Your object for the PSRFITS files

        nchans: No of channels in the frequency range

        chan_freq: Required frequency channel range

        filename: Output name of the Filterbank file

        outdir: Output directory for the Filterbank file

        nstart: Start sample number

    """

    original_dir, orig_basename = os.path.split(y.your_header.filename)
    if not filename:
        name, ext = os.path.splitext(orig_basename)
        if ext == '.fits':
            temp = name.split('_')
            if len(temp) > 1:
                filename = '_'.join(temp[:-1]) + '_converted.fil'
            else:
                filename = name + '_converted.fil'
        else:
            filename = name + '_converted.fil'

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
            fil_obj = make_sigproc_obj(filfile, y, nchans, chan_freq, nstart)
            fil_obj.write_header(filfile)
            logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
            fil_obj.append_spectra(data, filfile)

    except FileNotFoundError:
        fil_obj = make_sigproc_obj(filfile, y, nchans, chan_freq, nstart)
        fil_obj.write_header(filfile)
        logger.info(f'Writing {data.shape[0]} spectra to file: {filfile}')
        fil_obj.append_spectra(data, filfile)
    logger.info(f'Successfully written data to Filterbank file: {filfile}')
