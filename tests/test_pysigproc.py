import os

import numpy as np

from your.formats.pysigproc import SigprocFile

_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_pysigproc_obj():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    fil_obj = SigprocFile(fil_file)
    assert fil_obj.nchans == 336


def test_get_data_fil():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    fil_obj = SigprocFile(fil_file)
    data = fil_obj.get_data(0, 10)
    assert np.isclose(np.mean(data), 128, atol=1)
