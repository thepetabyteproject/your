from your import Your

import os
_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_your_from_fil():
    fil_file = os.path.join(_install_dir, 'data/28.fil')
    fil_obj = Your(fil_file)
    print(fil_obj)
    assert fil_obj.nchans == 336

    fil_file = os.path.join(_install_dir, 'data/28.fil')
    fil_obj = Your([fil_file])
    assert fil_obj.nchans == 336


def test_your_from_fits():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = Your(fits_file)
    assert fits_obj.nchans == 336

    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = Your([fits_file])
    assert fits_obj.nchans == 336


def test_your_no_file():
    try:
        f = Your([])
    except ValueError:
        assert True


def test_your_header():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = Your(fits_file)
    print(fits_obj.your_header)
    assert True
