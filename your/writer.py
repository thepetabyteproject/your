#!/usr/bin/env python3

import logging
import os

import numpy as np
from astropy.io import fits
from astropy.time import Time
from rich.progress import Progress

from your.formats.filwriter import sigproc_object_from_writer
from your.formats.fitswriter import initialize_psrfits
from your.utils.math import primes
from your.utils.rfi import sk_sg_filter

logger = logging.getLogger(__name__)


class Writer:
    """
    The unified writer class.

    Args:

        your_object: Your object
        nstart (int): Start sample to read from
        nsamp (int): Number of samples to write
        c_min (int): Starting channel index (default: 0)
        c_max (int): End channel index (default: total number of frequencies)
        outdir (str): Output directory for file
        outname (str): Name of the file to write to (without the file extension)
        progress (bool): Set to it to false to disable progress bars
        flag_rfi (bool): To turn on RFI flagging
        spectral_kurtosis_sigma (float): Sigma for spectral kurtosis filter
        savgol_frequency_window (float): Filter window for savgol filter
        savgol_sigma (float):  Sigma for savgol filter
        gulp (int): Gulp size for the data
        zero_dm_subt (bool): Enable zero DM rfi excision

    """

    def __init__(
        self,
        your_object,
        nstart=0,
        nsamp=None,
        c_min=None,
        c_max=None,
        outdir=None,
        outname=None,
        flag_rfi=False,
        progress=True,
        spectral_kurtosis_sigma=4,
        savgol_frequency_window=15,
        savgol_sigma=4,
        gulp=None,
        zero_dm_subt=False,
        time_decimation_factor=1,
        frequency_decimation_factor=1,
    ):

        self.your_object = your_object
        self.nstart = nstart
        if nsamp is None:
            self.nsamp = self.your_object.your_header.nspectra
        else:
            self.nsamp = nsamp

        self.c_min = c_min
        self.c_max = c_max

        self.time_decimation_factor = time_decimation_factor
        self.frequency_decimation_factor = frequency_decimation_factor

        if self.time_decimation_factor > 1:
            raise NotImplementedError("We have not implemented this feature yet.")

        if self.frequency_decimation_factor > 1:
            raise NotImplementedError("We have not implemented this feature yet.")

        self.outdir = outdir
        self.outname = outname
        self.flag_rfi = flag_rfi
        self.progress = progress
        self.sk_sig = spectral_kurtosis_sigma
        self.sg_fw = savgol_frequency_window
        self.sg_sig = savgol_sigma
        self.zero_dm_subt = zero_dm_subt
        self.data = None
        self.dada_is_set = False

        if gulp is not None:
            self.gulp = gulp
        else:
            # this logic fails if the number of samples is a prime number.
            p = np.sort(primes(self.nsamp))[::-1]
            if len(p) > 1:
                cumprods = np.cumprod(p)
                self.gulp = int(cumprods[len(cumprods) // 2])
            else:
                self.gulp = self.nsamp

        if self.gulp > self.nsamp:
            self.gulp = self.nsamp

        original_dir, orig_basename = os.path.split(
            self.your_object.your_header.filename
        )
        if not self.outname:
            name, ext = os.path.splitext(orig_basename)
            if ext == ".fits":
                temp = name.split("_")
                if len(temp) > 1:
                    self.outname = "_".join(temp[:-1]) + "_converted"
                else:
                    self.outname = name + "_converted"
            else:
                self.outname = name + "_converted"

        if not self.outdir:
            self.outdir = original_dir

        logging.debug("Writer Attributes:-")
        for arg, value in sorted(vars(self).items()):
            logging.debug("Attribute %s: %r", arg, value)

    @property
    def chan_min(self):
        if self.c_min:
            return self.c_min
        else:
            return 0

    @property
    def chan_max(self):
        if self.c_max:
            return self.c_max
        else:
            return len(self.your_object.chan_freqs)

    @property
    def chan_freqs(self):
        return self.your_object.chan_freqs[self.chan_min : self.chan_max]

    @property
    def nchans(self):
        return len(self.chan_freqs)

    @property
    def tstart(self):
        return (
            self.your_object.your_header.tstart
            + self.nstart * self.your_object.your_header.tsamp / (60 * 60 * 24)
        )

    def get_data_to_write(self, start_sample, nsamp):
        """

        Read data to self.data, selects channels
        Optionally perform RFI filtering and zero-DM subtraction

        Args:

            start_sample (int): Start sample number to read from
            nsamp (int): Number of samples to read

        """
        data = self.your_object.get_data(start_sample, nsamp)
        data = data[:, self.chan_min : self.chan_max]
        if self.flag_rfi:
            mask = sk_sg_filter(
                data,
                self.your_object,
                self.nchans,
                self.sk_sig,
                self.sg_fw,
                self.sg_sig,
            )

            if self.your_object.your_header.dtype == np.uint8:
                data[:, mask] = np.around(np.mean(data[:, ~mask]))
            else:
                data[:, mask] = np.mean(data[:, ~mask])

        if self.zero_dm_subt:
            logger.debug("Subtracting 0-DM time series from the data")
            data = data - data.mean(1)[:, None]

        data = data.astype(self.your_object.your_header.dtype)
        self.data = data

    def to_fil(self):
        """

        Writes out a Filterbank File.

        """

        self.outname += ".fil"
        with Progress() as progress:
            if not self.progress:
                task = progress.add_task(
                    "[green]Writing...", total=self.nsamp, visible=False
                )
            else:
                task = progress.add_task("[green]Writing...", total=self.nsamp)
            # create the header
            sigproc_object = sigproc_object_from_writer(self)

            # write the header
            sigproc_object.write_header(filename=self.outname)

            # make sure header got written
            if not os.path.isfile(self.outname):
                raise IOError("Failed to write the filterbank file")

            # get the nstart and number of samples to write
            start_sample = self.nstart
            samples_left = self.nsamp

            # open the file
            with open(self.outname, "ab") as f:
                # read till there are spectra to read
                while samples_left > 0:
                    self.get_data_to_write(start_sample, self.gulp)
                    start_sample += self.gulp
                    samples_left -= self.gulp
                    # goto the end of the file and dump
                    f.seek(0, os.SEEK_END)
                    f.write(self.data.ravel())
                    progress.update(task, advance=self.gulp)
                    logger.debug(
                        f"Wrote from spectra {start_sample}-{start_sample + self.gulp} to filterbank"
                    )

        logging.debug(f"Wrote all the necessary spectra")

    def to_fits(self, npsub=-1):
        """
        Writes out a PSRFITS file

        Args:
            npsub (int): number of spectra per subint

        """

        tsamp = self.your_object.your_header.tsamp

        if npsub == -1:
            npsub = int(1.0 / tsamp)
        else:
            pass

        if self.nsamp:
            if self.nsamp < npsub:
                npsub = self.nsamp

        outfile = self.outdir + "/" + self.outname + ".fits"

        initialize_psrfits(
            outfile=outfile,
            your_object=self.your_object,
            npsub=npsub,
            nstart=self.nstart,
            nsamp=self.nsamp,
            chan_freqs=self.chan_freqs,
        )

        nifs = self.your_object.your_header.npol

        logger.info("Filling PSRFITS file with data")

        # Open PSRFITS file
        hdulist = fits.open(outfile, mode="update")
        hdu = hdulist[1]
        nsubints = len(hdu.data[:]["data"])

        # Loop through chunks of data to write to PSRFITS
        n_read_subints = 10
        logger.info(f"Number of subints to write {nsubints}")

        st = self.nstart
        with Progress() as progress:
            if not self.progress:
                task = progress.add_task(
                    "[green]Writing...", total=nsubints, visible=False
                )
            else:
                task = progress.add_task("[green]Writing...", total=nsubints)

            for istart in np.arange(0, nsubints, n_read_subints):
                istop = istart + n_read_subints
                if istop > nsubints:
                    istop = nsubints
                else:
                    pass
                isub = istop - istart

                logger.info(
                    f"Writing data to {outfile} from subint = {istart} to {istop}."
                )

                # Read in nread samples from filfile
                nread = isub * npsub
                self.get_data_to_write(st, nread)
                progress.update(task, advance=n_read_subints)
                data = self.data
                st += nread

                nvals = isub * npsub * nifs
                if data.shape[0] < nvals:
                    logger.debug(
                        f"nspectra in this chunk ({data.shape[0]}) < nsubints * npsub * nifs ({nvals})"
                    )
                    logger.debug(f"Appending zeros at the end to fill the subint")
                    pad_back = np.zeros((nvals - data.shape[0], data.shape[1]))
                    data = np.vstack((data, pad_back))
                else:
                    pass

                data = np.reshape(data, (isub, npsub, nifs, self.nchans))

                # If channel_bandwidth is negative, we need to flip the freq axis
                #            if channel_bandwidth < 0:
                #                logger.debug(f"Flipping band as {channel_bandwidth} < 0")
                #                data = data[:, :, :, ::-1]
                #            else:
                #                pass

                # Put data in hdu data array
                logger.debug(f"Writing data of shape {data.shape} to {outfile}.")
                hdu.data[istart:istop]["data"][:, :, :, :] = data[:].astype(
                    self.your_object.your_header.dtype
                )

            # Write to file
            hdulist.flush()

        logger.info(f"All spectra written to {outfile}")
        # Close open FITS file
        hdulist.close()

    def dada_header(self):
        """
        Create the psrdada header dictionary

        Returns:
            dict: psrdada header dictionary

        """
        header = dict()
        header["BW"] = str(self.nchans * self.your_object.your_header.foff)
        header["FREQ"] = str((self.chan_freqs[0] + self.chan_freqs[-1]) / 2)
        tstart = Time(self.tstart, format="mjd")
        header["MJD_START"] = str(self.tstart)
        header["NBIT"] = str(self.your_object.your_header.nbits)
        header["TSAMP"] = str(self.your_object.your_header.tsamp * 1e6)
        header["HDR_SIZE"] = "4096"
        header["NCHAN"] = str(self.nchans)
        header["OBS_OFFSET"] = str(0)
        header["NPOL"] = str(1)  # self.your_object.your_header.npol)
        header["UTC_START"] = str(tstart.utc.iso.replace(" ", "-"))
        return header

    def setup_dada(self, dada_key=None, data_step=None):
        """
        Set up the psrdada buffers.

        Args:
            dada_key (hex): hex key, if left None, key would be chosen randomly
            data_step (int): size of each page in the ring buffer in bytes

        """
        from your.formats.dada import DadaManager

        if dada_key is None:
            self.dada_key = hex(np.random.randint(0, 16 ** 4))

        if data_step is not None:
            self.data_step = data_step
        else:
            self.data_step = self.gulp

        self.dada_size = int(
            self.data_step * self.nchans * self.your_object.your_header.nbits / 8
        )
        logger.debug(
            f"Setting up DadaManager with key: {self.dada_key} and page size {self.dada_size} bytes"
        )
        self.DM = DadaManager(size=self.dada_size, key=self.dada_key)
        self.DM.setup()

        self.dada_is_set = True

    def to_dada(self):
        """
        Start the process of dumping data to the dada buffers till the EOF.
        """
        if not self.dada_is_set:
            self.setup_dada()

        header = self.dada_header()
        with Progress() as progress:
            if not self.progress:
                task = progress.add_task(
                    "[green]Reading...", total=self.nsamp, visible=False
                )
            else:
                task = progress.add_task("[green]Reading...", total=self.nsamp)

            for data_read in range(
                self.nstart, self.nstart + self.nsamp, self.data_step
            ):
                logger.debug(f"Data read is {data_read}, Data step is {self.data_step}")
                self.get_data_to_write(data_read, self.data_step)
                self.DM.dump_header(header)
                self.DM.dump_data(self.data.flatten())
                progress.update(task, advance=self.data_step)
                if data_read == self.nsamp - self.data_step:
                    logger.info("Marked the end of data")
                    self.DM.eod()
                else:
                    self.DM.mark_filled()
        return None
