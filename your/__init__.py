#!/usr/bin/env python3
import json
import logging
import os

import numpy as np

from your.psrfits import PsrfitsFile
from your.pysigproc import SigprocFile

logger = logging.getLogger(__name__)


class Your(PsrfitsFile, SigprocFile):
    """
    Your class!
    """

    def __init__(self, file):
        self.your_file = file
        self.time_decimation_factor = 1
        self.frequency_decimation_factor = 1
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

    @property
    def chan_freqs(self):
        return self.fch1 + np.arange(self.nchans) * self.foff

    def bandpass(self, nspectra=None):
        """
        Create the bandpass of the file
        Args:
            nspectra: Number of spectra to create bandpass of.

        Returns: numpy bandpass array

        """
        if nspectra:
            if nspectra < self.nspectra:
                ns = nspectra
            else:
                logger.info(f'nspectra > number of spectra in file, generating bandpass using all available spectra.')
                ns = self.nspectra
        else:
            logger.warning(f'This will read all the data in the RAM. Might be slow as well.')
            ns = self.nspectra

        logger.debug(f'Generating bandpass using {ns} spectra.')
        return self.get_data(nstart=0, nsamp=int(ns))[:, 0, :].mean(0)

    def get_data(self, nstart: int, nsamp: int, time_decimation_factor=None,
                 frequency_decimation_factor=None, pol: int = 0):
        """
        Read data from files
        Args:
            nstart: start sample
            nsamp: number of samples to read
            time_decimation_factor: decimate in time with this factor
            frequency_decimation_factor: decimate in frequency with this factor
            pol: which polarization to chose

        Returns: 2D numpy array of data

        """
        logger.debug(f"Reading from {nsamp} samples from sample {nstart}")

        if time_decimation_factor is not None:
            self.time_decimation_factor = time_decimation_factor
        if frequency_decimation_factor is not None:
            self.frequency_decimation_factor = frequency_decimation_factor

        if self.time_decimation_factor != 1:
            logger.warning(f"Setting Time decimation factor to {self.time_decimation_factor},"
                           f"this will change the properties of the class")

        if self.frequency_decimation_factor != 1:
            logger.warning(f"Setting frequency decimation factor to {self.frequency_decimation_factor},"
                           f"this will change the properties of the class")

        logger.debug(f"time_decimation_factor: {self.time_decimation_factor}")
        logger.debug(f"frequency_decimation_factor: {self.frequency_decimation_factor}")

        if nsamp % self.time_decimation_factor != 0:
            raise ValueError(
                f"time_decimation_factor: {self.time_decimation_factor} should be a divisor of nsamp: {nsamp}")

        if self.nchans % self.frequency_decimation_factor != 0:
            raise ValueError(
                f"frequency_decimation_factor: {self.frequency_decimation_factor} should be a divisor or nchans:{self.nchans}")

        if pol not in [0, 1, 2, 3, 4]:
            raise ValueError(f"pol: {pol} can only be one of 0 (Intensity), 1 (Right Circular), 2 (Left Circular), "
                             "3 (Horizontal Linear), 4 (Vertical Linear)")

        if self.isfil:
            if pol > 0:
                logging.warning(f"pol > 0 not tested for Filterbank files.")
                if self.your_header.npol == 0:
                    logging.warning(f"Data contains only one polarisation. Setting pol to 0")
                    pol = 0
                else:
                    logging.warning(f'pol: {pol}, Assuming IQUV polarisation data in Filterbank file')
            data = SigprocFile.get_data(self, nstart, nsamp, pol=pol)
        else:
            data = PsrfitsFile.get_data(self, nstart, nsamp, pol=pol)

        if (self.time_decimation_factor > 1) or (self.frequency_decimation_factor > 1):
            nt, nf = data.shape
            if nf != self.your_header.nchans:
                raise ValueError(f"We screwed up!")
            data = data.reshape(self.time_decimation_factor, nt // self.time_decimation_factor,
                                nf // self.frequency_decimation_factor, self.frequency_decimation_factor)
            data = data.astype(np.float32)
            data = data.mean(axis=0)
            data = data.mean(axis=-1)
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

    @property
    def tsamp(self):
        return self.time_decimation_factor * self.native_tsamp

    @property
    def nchans(self):
        return self.native_nchans // self.frequency_decimation_factor

    @property
    def foff(self):
        return self.native_foff * self.frequency_decimation_factor

    def dispersion_delay(your_object, dms=5_000):
        return 4148808.0 * dms * (
                1 / np.min(self.chan_freqs) ** 2 - 1 / np.max(self.chan_freqs) ** 2) / 1000


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

            self.basename = os.path.basename(os.path.splitext(self.filename)[0])
            logger.debug(f'Generating unified header for file {self.basename}')
            if isinstance(your.source_name, str):
                self.source_name = your.source_name
            else:
                self.source_name = your.source_name.decode("utf-8")

            from your.utils.astro import ra2deg
            from your.utils.astro import dec2deg
            ra = ra2deg(your.src_raj)
            dec = dec2deg(your.src_dej)
            self.ra_deg = ra
            self.dec_deg = dec
            self.bw = your.nchans * your.foff
            self.center_freq = your.fch1 + self.bw / 2
        else:
            self.filelist = your.filelist
            self.filename = your.filename
            self.basename = os.path.basename(os.path.splitext(self.filename)[0])[:-5]
            logger.debug(f'Generating unified header for file {self.basename}')
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
        self.native_tsamp = your.tsamp
        self.native_nchans = your.nchans
        self.time_decimation_factor = your.time_decimation_factor
        self.frequency_decimation_factor = your.frequency_decimation_factor
        self.fch1 = your.fch1
        self.foff = your.foff
        self.npol = your.nifs
        self.tstart = your.tstart
        self.isfits = your.isfits
        self.isfil = your.isfil
        self.nspectra = your.nspectra



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
