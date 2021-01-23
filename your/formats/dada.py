import logging
import os

import numpy as np
from psrdada import Writer

logger = logging.getLogger(__name__)

"""
To use `psrdada` you would first need to install [psrdada-python](https://github.com/TRASAL/psrdada-python).
"""


class DadaManager:
    """
    A manager class for `psrdada` writer.

    Args:

        size (int): size of each buffer (in bytes)
        key (hex): hexadecimal dada key
        n_readers (int): Number of dada readers.
    """

    def __init__(self, size, key=0xDADA, n_readers=1):
        self.size = size
        self.key = key
        self.n_readers = n_readers

    def setup(self):
        """
        Kill any previous buffers with the same key.
        Set up the dada buffers and connect to a writer.
        """
        logger.debug(
            f"Destroying previous buffers using: dada_db -d -k {self.key} 2>/dev/null"
        )
        os.system(f"dada_db -d -k {self.key} 2>/dev/null")
        logger.info(
            f"Creating new buffers using dada_db -b {self.size} -k {self.key} -r {self.n_readers}"
        )
        os.system(
            f"dada_db -b {self.size} -k {self.key} -r {self.n_readers} -n 8 -l -p"
        )
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
        data[: len(data_input)] = data_input

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
