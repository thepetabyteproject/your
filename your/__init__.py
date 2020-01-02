#!/usr/bin/env python3
import json
import logging
import os

import numpy as np

from your.psrfits import PsrfitsFile
from your.pysigproc import SigprocFile

logger = logging.getLogger(__name__)


class Your(PsrfitsFile, SigprocFile):
    def __init__(self, file):
        self.your_file = file
        if isinstance(self.your_file, str):
            ext = os.path.splitext(self.your_file)[1]
            if ext == ".fits" or ext == ".sf":
                logger.debug(f'Reading the fits file: {self.your_file}')
                PsrfitsFile.__init__(self, psrfitslist=[self.your_file])
                self.isfits = True
                self.isfil = False
            elif ext == ".fil":
                logger.debug(f'Reading filterbank file {self.your_file}')
                SigprocFile.__init__(self, fp=self.your_file)
                self.isfits = False
                self.isfil = True
            else:
                raise TypeError('Filetype not supported')
        elif isinstance(self.your_file, list):
            if len(self.your_file) == 1 and os.path.splitext(*self.your_file)[1] == ".fil":
                for filterbank_file in self.your_file:
                    logger.debug(f'Reading filterbank file {filterbank_file}')
                    SigprocFile.__init__(self, fp=filterbank_file)
                    self.isfits = False
                    self.isfil = True
            else:
                for f in self.your_file:
                    ext = os.path.splitext(f)[1]
                    if ext == ".fits" or ext == ".sf" or ext == ".fil":
                        pass
                    else:
                        raise TypeError("Can only work with list of fits file or filterbanks")
                self.your_file.sort()
                logger.debug(f'Reading the following fits files: {self.your_file}')
                PsrfitsFile.__init__(self, psrfitslist=self.your_file)
                self.isfits = True
                self.isfil = False

        if not self.source_name:
            logger.info(f'Source name not present in the file. Setting source name to TEMP')
            self.source_name = 'TEMP'
        self.your_header = Header(self)

    @property
    def nspectra(self):
        if self.isfil:
            return SigprocFile.nspectra(self)
        else:
            return PsrfitsFile.nspectra(self)

    def get_data(self, nstart: int, nsamp: int, time_decimation_factor: int = 1):
        """

        :param nstart: start sample
        :param nsamp: number of samples to read
        :param time_decimation_factor: decimate time series by this factor
        .. note:: nsamp % time decimation factor should be 0.
        :return:
        """
        logger.debug(f"Reading from {nsamp} samples from sample {nstart}")

        if nsamp % time_decimation_factor != 0:
            raise ValueError(f"time_decimation_factor: {time_decimation_factor} should be a divisor of nsamp: {nsamp}")

        if self.isfil:
            data = SigprocFile.get_data(self, nstart, nsamp)
        else:
            data = PsrfitsFile.get_data(self, nstart, nsamp)

        if time_decimation_factor > 1:
            nt, nf = data.shape
            if nf != self.your_header.nchans:
                raise ValueError(f"We screwed up!")
            data = data.reshape(time_decimation_factor, nt // time_decimation_factor, nf)
            data = data.astype(np.float32)
            data = data.mean(axis=0)
            if self.nbits != 32:
                data = np.round(data)
                data = data.astype(self.your_header.dtype)
        return data

    def __repr__(self):
        if isinstance(self.your_file, list):
            s = "\n".join(map(str, self.your_file))
        else:
            s = self.your_file
        return f"Using {type(s)}:\n{s}"


class Header:
    # TODO: add nbeams, ibeam, data_type, az_start, za_start, telescope, backend
    def __init__(self, your):
        if your.isfil:
            if isinstance(your.your_file, str):
                assert os.path.isfile(your.your_file)
                self.filelist = [your.your_file]
                self.filename = your.your_file
            elif isinstance(your.your_file, list):
                self.filelist = your.your_file
                self.filename = your.your_file[0]
            else:
                raise IOError("Unknown type")

            logger.debug(f'Generating unified header for file {self.filename}')
            if isinstance(your.source_name, str):
                self.source_name = your.source_name
            else:
                self.source_name = your.source_name.decode("utf-8")

            from your.utils import dec2deg, ra2deg
            ra = ra2deg(your.src_raj)
            dec = dec2deg(your.src_dej)
            self.ra_deg = ra
            self.dec_deg = dec
            self.bw = your.nchans * your.foff
            self.center_freq = your.fch1 + self.bw / 2
        else:
            logger.debug(f'Generating unified header for file {your.filename}')
            self.filelist = your.filelist
            self.filename = your.filename
            self.ra_deg = your.ra_deg
            self.dec_deg = your.dec_deg
            self.bw = your.bw
            self.source_name = your.source_name
            self.center_freq = your.cfreq

        self.nbits = your.nbits

        if self.nbits <= 8:
            self.dtype = np.uint8
        elif self.nbits == 16:
            self.dtype = np.uint16
        elif self.nbits == 32:
            self.dtype = np.float32
        else:
            raise ValueError(f"Unsupported number of bits {self.nbits}")

        self.nchans = your.nchans
        self.tsamp = your.tsamp
        self.fch1 = your.fch1
        self.foff = your.foff
        self.npol = your.nifs
        self.tstart = your.tstart
        self.isfits = your.isfits
        self.isfil = your.isfil

        from astropy.coordinates import SkyCoord
        loc = SkyCoord(self.ra_deg, self.dec_deg, unit='deg')
        self.gl = loc.galactic.l.value - 180
        self.gb = loc.galactic.b.value

        from astropy.time import Time
        ts = Time(your.tstart, format='mjd')
        self.tstart_utc = ts.utc.isot

        logger.debug(f'Successfully generated unified header for file {self.filename}')

    def __str__(self):
        hdr = vars(self)
        return json.dumps(hdr, indent=2)
