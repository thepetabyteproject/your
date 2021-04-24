#!/usr/bin/env python3
import json
import logging
import os

import numpy as np

from your.formats.psrfits import PsrfitsFile
from your.formats.pysigproc import SigprocFile
from your.utils.misc import check_file_exist, MyEncoder

logger = logging.getLogger(__name__)

FORMATS = {"fil": SigprocFile, "fits": PsrfitsFile}


class Your(PsrfitsFile, SigprocFile):
    """
    Your class.

    Args:
        file: String or a list of files. It can either filterbank or psrfits files.

    Examples:
        your_object = your.Your("/path/to/filterbank.fil")
        your_object = your.Your(["puppi_58763_B1919+21_0292_0001.fits","puppi_58763_B1919+21_0292_0002.fits"]

    Attributes:
        your_header: instance of the Header class

    """

    def __init__(self, file):
        self.your_file = file
        if isinstance(self.your_file, str):
            ext = os.path.splitext(self.your_file)[1]
            check_file_exist(self.your_file)
            if ext == ".fits" or ext == ".sf":
                self.format = "fits"
                self.your_file = [self.your_file]
            elif ext == ".fil":
                self.format = "fil"
            else:
                raise TypeError(f"Filetype {ext} not supported")
        elif isinstance(self.your_file, list):
            if len(self.your_file) == 0:
                raise ValueError("Filelist is empty. Please check the input")
            if (
                len(self.your_file) == 1
                and os.path.splitext(*self.your_file)[1] == ".fil"
            ):
                self.format = "fil"
                self.your_file = self.your_file[0]
                check_file_exist(self.your_file)
            else:
                for f in self.your_file:
                    check_file_exist(f)
                    ext = os.path.splitext(f)[1]
                    if ext not in [".fits", ".sf"]:
                        raise TypeError(
                            "Can only work with a list of fits file or an individual filterbank file"
                        )
                self.your_file.sort()
                self.format = "fits"
        else:
            raise ValueError(
                "file should be a string of input file path or a list of strings with relevant file paths."
            )

        logger.debug(f"Reading the file(s): {self.your_file}")
        self.formatclass = FORMATS[self.format]
        self.formatclass.__init__(self, self.your_file)
        if not self.source_name:
            logger.info(
                f"Source name not present in the file. Setting source name to TEMP"
            )
            self.source_name = "TEMP"
        self.your_header = Header(self)

    @property
    def chan_freqs(self):
        """
        Returns: numpy array of channel frequencies
        """
        return self.fch1 + np.arange(self.nchans) * self.foff

    @property
    def native_tsamp(self):
        """
        Returns:
            Native sampling time of the data in seconds
        """
        return self.formatclass.native_tsamp(self)

    @property
    def native_foff(self):
        """
        Returns:
            Native channel bandwidth of the data in MHz
        """
        return self.formatclass.native_foff(self)

    @property
    def native_nchans(self):
        """
        Returns:
            Native number of channels in the data
        """
        return self.formatclass.native_nchans(self)

    @property
    def native_nspectra(self):
        """
        Returns:
            Native number of spectra in the data.
        """
        return self.formatclass.native_nspectra(self)

    @property
    def tend(self):
        """
        Returns:
            End MJD of the data
        """
        return (
            self.your_header.tstart
            + self.your_header.nspectra * self.your_header.tsamp / 86400.0
        )

    def bandpass(self, nspectra=None):
        """
        Create the bandpass of the file

        Args:
            nspectra (int): Number of spectra to create bandpass from.

        Returns:
            numpy.ndarray: bandpass array

        """
        if nspectra:
            if nspectra < self.your_header.native_nspectra:
                ns = nspectra
            else:
                logger.info(
                    f"nspectra > number of spectra in file, generating bandpass using all available spectra."
                )
                ns = self.your_header.native_nspectra
        else:
            logger.warning(
                f"This will read all the data in the RAM. Might be slow as well."
            )
            ns = self.your_header.native_nspectra

        logger.debug(f"Generating bandpass using {ns} spectra.")
        return self.get_data(nstart=0, nsamp=int(ns)).mean(0)

    def get_data(
        self,
        nstart: int,
        nsamp: int,
        time_decimation_factor=None,
        frequency_decimation_factor=None,
        pol: int = 0,
        npoln: int = 1,
    ):
        """
        Read data from files

        Args:
            nstart (int): start sample
            nsamp (int): number of samples to read
            time_decimation_factor (int): number of time samples to average
            frequency_decimation_factor (int): number of frequency channels to average
            pol (int): which polarization to chose
            npoln (int): number of polarization to return

        Note:
            The decimation (both in time and frequency) is done on the data read i.e containing `nsamp` number of samples
            and `nchans` number of channels. Therefore, both decimation factors should exactly divide the
            nsamps or nchans respectively.

        Returns:
            numpy.ndarray: 2D numpy array of data


        """
        logger.debug(f"Reading {nsamp} samples from sample {nstart}")

        if self.your_header.time_decimation_factor != 1:
            logger.warning(
                f"Setting Time decimation factor to {self.your_header.time_decimation_factor},"
                f"this will change the properties of the class"
            )

        if self.your_header.frequency_decimation_factor != 1:
            logger.warning(
                f"Setting frequency decimation factor to {self.your_header.frequency_decimation_factor},"
                f"this will change the properties of the class"
            )

        if time_decimation_factor is not None:
            self.your_header.time_decimation_factor = time_decimation_factor
        if frequency_decimation_factor is not None:
            self.your_header.frequency_decimation_factor = frequency_decimation_factor

        logger.debug(
            f"time_decimation_factor: {self.your_header.time_decimation_factor}"
        )
        logger.debug(
            f"frequency_decimation_factor: {self.your_header.frequency_decimation_factor}"
        )

        if nsamp % self.your_header.time_decimation_factor != 0:
            raise ValueError(
                f"time_decimation_factor: {self.your_header.time_decimation_factor} should be a divisor of nsamp: {nsamp}"
            )

        if self.nchans % self.your_header.frequency_decimation_factor != 0:
            raise ValueError(
                f"frequency_decimation_factor: {self.your_header.frequency_decimation_factor} should be a divisor or nchans:{self.nchans}"
            )

        assert npoln <= self.your_header.npol, (
            f"npoln={npoln} cannot be greater than number of polarisations in "
            f"the data {self.your_header.npol}"
        )

        if npoln == 1:
            if pol not in [0, 1, 2, 3, 4]:
                raise ValueError(
                    f"pol: {pol} can only be one of 0 (Intensity), 1 (Right Circular), 2 (Left Circular), "
                    "3 (Horizontal Linear), 4 (Vertical Linear)"
                )

            if self.format == "fil":
                if pol > 0:
                    logging.warning(f"pol > 0 not tested for Filterbank files.")
                    if self.your_header.npol == 0:
                        logging.warning(
                            f"Data contains only one polarisation. Setting pol to 0"
                        )
                        pol = 0
                    else:
                        logging.warning(
                            f"pol: {pol}, Assuming IQUV polarisation data in Filterbank file"
                        )
        elif npoln == 4:
            logger.warning(f"npoln is equal to 4. Returning all polarisations.")
        else:
            raise ValueError(
                f"npoln ({npoln}) can only be 1 (one polarisation) or 4 (all)."
            )

        data = self.formatclass.get_data(self, nstart, nsamp, pol=pol, npoln=npoln)

        if data.shape[1] == 1:
            data = data[:, 0, :]

        if (self.your_header.time_decimation_factor > 1) or (
            self.your_header.frequency_decimation_factor > 1
        ):
            sh = data.shape
            if len(sh) == 2:
                nt, nf = sh
                data = data.reshape(
                    self.your_header.time_decimation_factor,
                    nt // self.your_header.time_decimation_factor,
                    nf // self.your_header.frequency_decimation_factor,
                    self.your_header.frequency_decimation_factor,
                )
            elif len(sh) == 3:
                nt, nifs, nf = sh
                data = data.reshape(
                    self.your_header.time_decimation_factor,
                    nt // self.your_header.time_decimation_factor,
                    nifs,
                    nf // self.your_header.frequency_decimation_factor,
                    self.your_header.frequency_decimation_factor,
                )
            else:
                raise ValueError(
                    f"data shape is {sh}. But data can only have either 2 (nt, nf) or 3 (nt, nifs, nf) "
                    f"dimensions."
                )
            data = data.astype(np.float32)
            data = data.mean(axis=0)
            data = data.mean(axis=-1)
        if self.your_header.nbits != 32:
            data = np.round(data)
            data = data.astype(self.your_header.dtype)
        return data

    def __repr__(self):
        if isinstance(self.your_file, list):
            s = "\n".join(map(str, self.your_file))
        else:
            s = self.your_file
        return f"Using {type(s)}:\n{s}"

    def dispersion_delay(self, dms=5_000):
        """
        Calculate the dispersion delay in seconds for the given configuration

        Args:
            dms: DM or a list of DM values

        Returns:
            Dispersion delay in seconds.
        """
        return (
            4148808.0
            * dms
            * (1 / np.min(self.chan_freqs) ** 2 - 1 / np.max(self.chan_freqs) ** 2)
            / 1000
        )


class Header:
    # TODO: add nbeams, ibeam, data_type, az_start, za_start, telescope, backend
    """
    Your Header class, it contains all the relevant metadata.

    Args:
        your: Your object

    Attributes:
        filelist (list): List of files used to make the your object
        filename (str): Name of the first file used to make the object
        basename (str): Base name of file
        source_name (str): Source Name
        ra_deg (float): RA of the source in degrees
        dec_deg (float): Dec of the source in degrees
        bw (float): bandwidth of the data
        center_freq (float): Center frequency of the data.
        time_decimation_factor (int): Number of time samples to average
        frequency_decimation_factor (int): Number of frequency channels to average
        native_tsamp (float): Sampling time of the data pre-decimation (seconds)
        native_foff (float): Channel bandwidth of the data pre-decimation (MHz)
        native_nchans : Number of channels in the data pre-decimation
        native_nspectra: Number of spectra in the data pre-decimation
        dtype: dtype of the (read) data
        nbits (int): Number of bits in the data
        tstart (float): Start MJD of the data
        fch1 (float): Frequency of the first channel (MHz)
        npol (int): Number of polarisations in the data
    """

    def __init__(self, your):
        if isinstance(your.your_file, str):
            self.filelist = [your.your_file]
            self.filename = your.your_file
        elif isinstance(your.your_file, list):
            self.filelist = your.your_file
            self.filename = your.your_file[0]
        else:
            raise IOError("Unknown type")

        self.basename = os.path.basename(os.path.splitext(self.filename)[0])
        logger.debug(f"Generating unified header for file {self.basename}")
        if isinstance(your.source_name, str):
            self.source_name = your.source_name
        else:
            self.source_name = your.source_name.decode("utf-8")
        self.ra_deg = your.ra_deg
        self.dec_deg = your.dec_deg
        self.bw = your.bw
        self.center_freq = your.cfreq
        self.nbits = your.nbits
        self.format = your.format

        if self.nbits <= 8:
            self.dtype = np.uint8
        elif self.nbits == 16:
            if (
                self.format == "fits"
                and int(your.fits["SUBINT"].header["TDIM17"][1]) == 1
            ):
                self.dtype = np.int16
            else:
                self.dtype = np.uint16
        elif self.nbits == 32:
            if self.format == "fits":
                self.dtype = np.int32
            else:
                self.dtype = np.float32
        else:
            raise ValueError(f"Unsupported number of bits {self.nbits}")

        self.time_decimation_factor = 1
        self.frequency_decimation_factor = 1
        self.native_tsamp = your.native_tsamp
        self.native_foff = your.native_foff
        self.native_nchans = your.native_nchans
        self.native_nspectra = your.native_nspectra
        self.fch1 = your.fch1
        self.npol = your.nifs
        self.poln_order = your.poln_order
        self.tstart = your.tstart
        from astropy.coordinates import SkyCoord

        if self.ra_deg and self.dec_deg:
            loc = SkyCoord(self.ra_deg, self.dec_deg, unit="deg")
            self.gl = loc.galactic.l.value - 180
            self.gb = loc.galactic.b.value
        else:
            # for 174 bit header Filterbank
            self.gl = None
            self.gb = None

        from astropy.time import Time

        ts = Time(your.tstart, format="mjd")
        self.tstart_utc = ts.utc.isot

        logger.debug(f"Successfully generated unified header for file {self.filename}")

    @property
    def tsamp(self):
        return self.time_decimation_factor * self.native_tsamp

    @property
    def nchans(self):
        return self.native_nchans // self.frequency_decimation_factor

    @property
    def foff(self):
        return self.native_foff * self.frequency_decimation_factor

    @property
    def nspectra(self):
        return int(self.native_nspectra // self.time_decimation_factor)

    def __repr__(self):
        property_names = [p for p in dir(self) if not p.startswith("__")]
        d = {}
        for prop in property_names:
            d[prop] = getattr(self, prop)
        d["dtype"] = d["dtype"].__name__
        return "Unified Header:" + json.dumps(d, cls=MyEncoder, indent=2)[1:-1].replace(
            ",", ""
        )
