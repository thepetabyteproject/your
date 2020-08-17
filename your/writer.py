#!/usr/bin/env python3

import logging
import os

import numpy as np
import tqdm
from astropy.io import fits

from your.formats.filwriter import write_fil
from your.formats.fitswriter import initialize_psrfits
from your.utils.rfi import sk_sg_filter

logger = logging.getLogger(__name__)


class Writer:
    """
    Writer class

    Args:

        y: your object

    """

    def __init__(self, y):
        self.your_obj = y

    def to_fil(self, nstart=None, nsamp=None, c=None, outdir=None, outname=None, flag_rfi=False,
               progress=None, sk_sig=4, sg_fw=15, sg_sig=4, zero_dm_subt=False):
        """
        Writes out a Filterbank File.

        Args:

            nstart: Start sample to read from

            nsamp: Number of samples to write

            c: Required frequency channel range [min_chan, max_chan] (excludes the higher channel number)

            outdir: Output directory for Filterbank file

            outname: Name of the Filterbank file to write to

            progress: turn on/off progress bar

            flag_rfi: To turn on RFI flagging

            sk_sig: sigma for spectral kurtosis filter

            sg_fw: filter window for savgol filter

            sg_sig: sigma for savgol filter

            zero_dm_subt: enable zero DM rfi excision

        """

        if c:
            min_c = int(np.min(c))
            max_c = int(np.max(c))
        else:
            min_c = 0
            max_c = len(self.your_obj.chan_freqs)

        chan_freq = self.your_obj.chan_freqs[min_c:max_c]
        nchans = len(chan_freq)

        # Calculate loop of spectra
        if not nstart:
            nstart = 0

        if not nsamp:
            nsamp = self.your_obj.your_header.native_nspectra

        interval = 4096 * 24
        if nsamp < interval:
            interval = nsamp

        if nsamp > interval:
            nloops = 1 + nsamp // interval
        else:
            nloops = 1
        nstarts = np.arange(nstart, interval * nloops, interval, dtype=int)
        nsamps = np.full(nloops, interval)
        if nsamp % interval != 0:
            nsamps = np.append(nsamps, [nsamp % interval])

        original_dir, orig_basename = os.path.split(self.your_obj.your_header.filename)
        if not outname:
            name, ext = os.path.splitext(orig_basename)
            if ext == '.fits':
                temp = name.split('_')
                if len(temp) > 1:
                    outname = '_'.join(temp[:-1]) + '_converted.fil'
                else:
                    outname = name + '_converted.fil'
            else:
                outname = name + '_converted.fil'

        if not outdir:
            outdir = original_dir

        # Read data
        for st, samp in tqdm.tqdm(zip(nstarts, nsamps), total=len(nstarts), disable=progress):
            logger.debug(f'Reading spectra {st}-{st + samp} in file {self.your_obj.your_header.filename}')
            data = self.your_obj.get_data(st, samp)
            data = data[:, min_c:max_c]
            if flag_rfi:
                mask = sk_sg_filter(data, self.your_obj, sk_sig, nchans, sg_fw, sg_sig)

                if self.your_obj.your_header.dtype == np.uint8:
                    data[:, mask] = np.around(np.mean(data[:, ~mask]))
                else:
                    data[:, mask] = np.mean(data[:, ~mask])

            if zero_dm_subt:
                logger.debug('Subtracting 0-DM time series from the data')
                data = data - data.mean(1)[:, None]

            data = data.astype(self.your_obj.your_header.dtype)
            logger.info(
                f'Writing data from spectra {st}-{st + samp} in the frequency channel range {min_c}-{max_c} '
                f'to filterbank')
            write_fil(data, self.your_obj, nchans=nchans, chan_freq=chan_freq, outdir=outdir, filename=outname,
                      nstart=nstart)
            logger.debug(f'Successfully written data from spectra {st}-{st + samp} to filterbank')

        logging.debug(f'Read all the necessary spectra')

    def to_fits(self, nstart=None, c=None, nsamp=None, npsub=-1, outdir=None, outname=None, progress=None,
                flag_rfi=False, sk_sig=4, sg_fw=15, sg_sig=4, zero_dm_subt=False):
        """
        Writes out a fits file

        Args:

            nstart: start sample number to read from

            nsamp: number of samples to read/write

            c: Required frequency channel range [min_chan, max_chan] (excludes the higher channel number)

            npsub: Number of spectra per subint

            outdir: Output directory for Filterbank file

            outname: Name of the PSRFITS file to write to

            progress: turn on/off progress bar

            flag_rfi: To turn on RFI flagging

            sk_sig: sigma for spectral kurtosis filter

            sg_fw: filter window for savgol filter

            sg_sig: sigma for savgol filter

            zero_dm_subt: enable zero DM rfi excision

        """

        tsamp = self.your_obj.your_header.tsamp

        if npsub == -1:
            npsub = int(1.0 / tsamp)
        else:
            pass

        if nsamp:
            if nsamp < npsub:
                npsub = nsamp

        if not outname:
            original_dir, orig_basename = os.path.split(self.your_obj.your_header.filename)
            name, ext = os.path.splitext(orig_basename)
            if ext == '.fits':
                temp = name.split('_')
                if len(temp) > 1:
                    outname = '_'.join(temp[:-1]) + '_converted.fits'
                else:
                    outname = name + '_converted.fits'
            else:
                outname = name + '_converted.fits'

        if not outdir:
            outdir = os.getcwd()

        outfile = outdir + '/' + outname

        if c:
            min_c = int(np.min(c))
            max_c = int(np.max(c))
        else:
            min_c = 0
            max_c = len(self.your_obj.chan_freqs)

        chan_freqs = self.your_obj.chan_freqs[min_c:max_c]
        nchans = len(chan_freqs)

        initialize_psrfits(outfile=outfile, y=self.your_obj, npsub=npsub, nstart=nstart, nsamp=nsamp,
                           chan_freqs=chan_freqs)

        nifs = self.your_obj.your_header.npol

        logger.info("Filling PSRFITS file with data")

        # Open PSRFITS file
        hdulist = fits.open(outfile, mode='update')
        hdu = hdulist[1]
        nsubints = len(hdu.data[:]['data'])

        # Loop through chunks of data to write to PSRFITS
        n_read_subints = 10
        if not nstart:
            nstart = 0
        logger.info(f'Number of subints to write {nsubints}')

        for istart in tqdm.tqdm(np.arange(0, nsubints, n_read_subints), disable=progress):
            istop = istart + n_read_subints
            if istop > nsubints:
                istop = nsubints
            else:
                pass
            isub = istop - istart

            logger.info(f"Writing data to {outfile} from subint = {istart} to {istop}.")

            # Read in nread samples from filfile
            nread = isub * npsub
            data = self.your_obj.get_data(nstart=nstart, nsamp=nread)
            data = data[:, min_c:max_c]
            if flag_rfi:
                mask = sk_sg_filter(data, self.your_obj, sk_sig, nchans, sg_fw, sg_sig)

                if self.your_obj.your_header.dtype == np.uint8:
                    data[:, mask] = np.around(np.mean(data[:, ~mask]))
                else:
                    data[:, mask] = np.mean(data[:, ~mask])

            if zero_dm_subt:
                logger.debug('Subtracting 0-DM time series from the data')
                data = data - data.mean(1)[:, None]

            logger.debug(f'Shape of data array after get_data is {data.shape}')
            nstart += nread

            nvals = isub * npsub * nifs
            if data.shape[0] < nvals:
                logger.debug(f'nspectra in this chunk ({data.shape[0]}) < nsubints * npsub * nifs ({nvals})')
                logger.debug(f'Appending zeros at the end to fill the subint')
                pad_back = np.zeros((nvals - data.shape[0], data.shape[1]))
                data = np.vstack((data, pad_back))
            else:
                pass

            data = np.reshape(data, (isub, npsub, nifs, nchans))

            # If foff is negative, we need to flip the freq axis
#            if foff < 0:
#                logger.debug(f"Flipping band as {foff} < 0")
#                data = data[:, :, :, ::-1]
#            else:
#                pass

            # Put data in hdu data array
            logger.debug(f'Writing data of shape {data.shape} to {outfile}.')
            hdu.data[istart:istop]['data'][:, :, :, :] = data[:].astype(self.your_obj.your_header.dtype)

            # Write to file
            hdulist.flush()

        logger.info(f'All spectra written to {outfile}')
        # Close open FITS file
        hdulist.close()
