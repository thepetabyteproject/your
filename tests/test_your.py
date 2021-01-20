import os

import pytest

from your import Your

_install_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="session", autouse=True)
def fil_file():
    return os.path.join(_install_dir, "data/28.fil")


@pytest.fixture(scope="session", autouse=True)
def fits_file():
    return os.path.join(_install_dir, "data/28.fits")


@pytest.fixture(scope="function", autouse=True)
def y(fil_file):
    return Your(fil_file)


def test_your_from_fil(fil_file):
    fil_obj = Your(fil_file)
    assert fil_obj.nchans == 336

    fil_obj = Your([fil_file])
    assert fil_obj.nchans == 336


def test_your_from_fits(fits_file):
    fits_obj = Your(fits_file)
    assert fits_obj.nchans == 336

    fits_obj = Your([fits_file])
    assert fits_obj.nchans == 336


def test_your_no_file():
    with pytest.raises(ValueError):
        Your([])

    with pytest.raises(IOError):
        Your("nofile.blah")


def test_unsupported_file():
    with pytest.raises(TypeError):
        Your(os.path.join(_install_dir, "data/some.blah"))

    with pytest.raises(TypeError):
        Your([os.path.join(_install_dir, "data/some.blah")])


def test_paths():
    with pytest.raises(ValueError):
        Your(bytearray("data/28.fil", "utf-8"))


def test_your_header(fits_file):
    fits_obj = Your(fits_file)
    print(fits_obj.your_header)
    assert True


def test_bandpass(y):
    assert pytest.approx(y.bandpass().mean(), rel=3) == 128
    assert pytest.approx(y.bandpass(nspectra=2 ** 20).mean(), rel=3) == 128
    assert pytest.approx(y.bandpass(nspectra=512).mean(), rel=3) == 128


def test_decimation_factors(y):
    data = y.get_data(0, 1024, time_decimation_factor=2, frequency_decimation_factor=2)
    assert data.shape == (512, 168)

    with pytest.raises(ValueError):
        y.get_data(0, 256, pol=10)

    with pytest.raises(ValueError):
        y.get_data(0, 256, time_decimation_factor=255)

    with pytest.raises(ValueError):
        y.get_data(0, 256, frequency_decimation_factor=5)


def test_pol(y):
    data = y.get_data(0, 256, pol=1)
    assert data.shape == (256, 336)


def test_repr(fil_file):
    y = Your(fil_file)
    assert repr(y) == f"Using <class 'str'>:\n{fil_file}"


def test_dispersion_delay(y):
    assert pytest.approx(y.dispersion_delay(1), rel=1e-3) == 0.0013160529703817566
