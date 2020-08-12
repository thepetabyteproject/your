import numpy as np

from your.psrfits import PsrfitsFile

import os
_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_psrfits_obj():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = PsrfitsFile([fits_file])
    print(fits_obj.specinfo)
    assert fits_obj.nchans == 336


def test_get_data_fits():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = PsrfitsFile([fits_file])
    data = fits_obj.get_data(0, 10)
    assert np.isclose(np.mean(data), 128, atol=1)
