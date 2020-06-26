import logging
import os

import numpy as np
from astropy.time import Time
from psrdada import Writer
from tqdm import tqdm

from your.utils.math import primes, closest_divisor, find_gcd

logger = logging.getLogger(__name__)

"""
To use `psrdada` you would first need to install [psrdada-python](https://github.com/AA-ALERT/psrdada-python).
"""


class DadaManager:
    """
    A manager class for `psrdada` writer.

    Args:

        size (int): size of each buffer (in bytes)

        key (hex): hexadecimal dada key

        n_readers (int): Number of dada readers.
    """

    def __init__(self, size, key=0xdada, n_readers=1):
        self.size = size
        self.key = key
        self.n_readers = n_readers

    def setup(self):
        """
        Kill any previous buffers with the same key.
        Set up the dada buffers and connect to a writer.
        """
        logger.debug(f"Destroying previous buffers using: dada_db -d -k {self.key} 2>/dev/null")
        os.system(f"dada_db -d -k {self.key} 2>/dev/null")
        logger.info(f"Creating new buffers using dada_db -b {self.size} -k {self.key} -r {self.n_readers}")
        os.system(f"dada_db -b {self.size} -k {self.key} -r {self.n_readers}")
        self.writer = Writer()
        self.writer.connect(int(self.key, 16))

    def dump_header(self, header):
        """
        Set the psrdada header
        """
        return self.writer.setHeader(header)

    def dump_data(self, data_input):
        """
        Dump the data to the buffer

        Args:

            data_input (numpy.ndarray): Numpy array of the data.

        """
        page = self.writer.getNextPage()
        data = np.asarray(page)
        data.fill(0)
        data[:len(data_input)] = data_input

    def mark_filled(self):
        """
        Mark that data is filled in the buffer page.
        """
        return self.writer.markFilled()

    def eod(self):
        """
        Mark the end of data.
        """
        return self.writer.markEndOfData()

    def teardown(self):
        """
        Disconnect the writer and tear down the buffers.

        """
        self.writer.disconnect()
        os.system(f"dada_db -d -k {self.key} 2> /dev/null")


class YourDada:
    """

    Linker class between `psrdada` and `your`.

    Args:

        your_object: your object

    """

    def __init__(self, your_object):

        self.your_object = your_object
        if self.your_object.isfits:
            logger.debug(f'Calculating dada size and data step for the fits files')
            self.list_of_subints = self.your_object.specinfo.num_subint.astype('int')
            if len(self.list_of_subints) > 1:
                # if there is more than one files see how many subints we need to read so that the data is equally split
                self.subint_steps = int(find_gcd(self.list_of_subints))
            else:
                # if there is just one large file, read it in chunks
                self.subint_steps = int(np.max(np.prod(np.unique((primes(self.list_of_subints))))))
            self.dada_size = self.subint_steps * self.your_object.your_header.nchans * self.your_object.specinfo.spectra_per_subint  # * self.your_object.nbits / 8  # bytes
            self.data_step = int(self.subint_steps * self.your_object.specinfo.spectra_per_subint)
        else:
            nsamp_gulp = 2 ** 18
            logger.debug(f'Calculating dada size and data step for the filterbank file')
            if self.your_object.your_header.nspectra < nsamp_gulp:
                self.dada_size = self.your_object.your_header.nspectra * self.your_object.your_header.nchans * self.your_object.your_header.nbits / 8  # bytes
                self.data_step = int(self.your_object.your_header.nspectra)
            else:
                self.data_step = int(closest_divisor(self.your_object.your_header.nspectra, nsamp_gulp))
                self.dada_size = self.data_step * self.your_object.your_header.nchans * self.your_object.your_header.nbits / 8  # bytes
        self.dada_key = hex(np.random.randint(0, 16 ** 4))

    def setup(self):
        """
        Start the dada manager and make the header.

        """
        logger.info(f"dada buffer key {self.dada_key}")
        self.DM = DadaManager(size=self.dada_size, key=self.dada_key)
        self.dada_header = self.your_dada_header()
        return self.DM.setup()

    def teardown(self):
        """
        Tear down the dada header.
        """
        logger.info("Tearing down the dada buffer")
        return self.DM.teardown()

    def your_dada_header(self):
        """
        Make dada header from `your_header`.

        Returns:

            dict: dada header as a python dictionary.

        """
        header = {}
        header["BW"] = str(self.your_object.your_header.nchans * self.your_object.your_header.foff)
        header["FREQ"] = str(self.your_object.your_header.fch1 + (
                self.your_object.your_header.nchans * self.your_object.your_header.foff / 2))
        header["MJD_START"] = str(self.your_object.your_header.tstart)
        header["NBIT"] = str(self.your_object.your_header.nbits)
        header["TSAMP"] = str(self.your_object.your_header.tsamp * 1e6)
        header["HDR_SIZE"] = "4096"
        header["NCHAN"] = str(self.your_object.your_header.nchans)
        header["OBS_OFFSET"] = str(0)
        header["NPOL"] = str(self.your_object.your_header.npol)
        tstart = Time(self.your_object.your_header.tstart, format='mjd')
        header["UTC_START"] = str(tstart.utc.iso.replace(' ', '-'))
        return header

    def to_dada(self, progress=None):
        """
        Dump the data to the dada buffer

        Args:

            progress: if `False` will not show the progress bar.

        """
        for data_read in tqdm(range(0, int(self.your_object.your_header.native_nspectra), self.data_step),
                              disable=progress):
            logger.debug(f"Data read is {data_read}, Data step is {self.data_step}")
            data_input = self.your_object.get_data(data_read, self.data_step)
            logger.debug(f"Data specs: Shape: {data_input.shape}, dtype: {data_input.dtype}")
            self.DM.dump_header(self.dada_header)
            self.DM.dump_data(data_input.flatten().astype(self.your_object.your_header.dtype))
            if data_read == self.your_object.your_header.nspectra - self.data_step:
                logger.info("Marked the End of Data")
                self.DM.eod()
            else:
                self.DM.mark_filled()
        return
