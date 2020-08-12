#!/usr/bin/env python3

import logging
from your.your import Your
from your.utils.rfi import sk_sg_filter
from your.utils.filwriter import write_fil
import numpy as np
import tqdm
logger = logging.getLogger(__name__)

class Writer:
    def __init__(self, y):
        self.your_obj = y

    def to_fil(self, nstart=None, nsamp=None, c=None, outdir=None, filfile=None, progress=None,
            flag_rfi=False, sk_sig=4, sg_fw=15, sg_sig=4, zero_dm_subt=False):

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

        # Read data
        for st, samp in tqdm.tqdm(zip(nstarts, nsamps), total=len(nstarts), disable=progress):
            logger.debug(f'Reading spectra {st}-{st + samp} in file {self.your_obj.your_header.filename}')
            data = self.your_obj.get_data(st, samp).astype(self.your_obj.your_header.dtype)
            data = data[:, min_c:max_c]
            if flag_rfi:
                mask = sk_sg_filter(data, self, sk_sig, nchans, sg_fw, sg_sig)

                if self.your_obj.your_header.dtype == np.uint8:
                    data[:, mask] = np.around(np.mean(data[:, ~mask]))
                else:
                    data[:, mask] = np.mean(data[:, ~mask])

            if zero_dm_subt:
                logger.debug('Subtracting 0-DM time series from the data')
                data = data - data.mean(1)[:, None]

            logger.info(
                f'Writing data from spectra {st}-{st + samp} in the frequency channel range {min_c}-{max_c} to filterbank')
            write_fil(data, self.your_obj, nchans=nchans, chan_freq=chan_freq, outdir=outdir, filename=filfile, nstart=nstart)
            logger.debug(f'Successfully written data from spectra {st}-{st + samp} to filterbank')

        logging.debug(f'Read all the necessary spectra')

