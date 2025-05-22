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


def test_zero_subints():
    with pytest.raises(ValueError):
        Your(os.path.join(_install_dir, "data/empty.fits"))


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
    assert pytest.approx(y.bandpass(nspectra=2**20).mean(), rel=3) == 128
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

    with pytest.raises(AssertionError):
        y.get_data(0, 100, npoln=4)

    assert y.your_header.poln_order == "I"


def test_4pol():
    file = os.path.join(_install_dir, "data/test_4pol.fits")
    y = Your(file)
    data = y.get_data(0, 100, npoln=1)
    assert data.shape == (100, 512)

    data = y.get_data(0, 100, npoln=4)
    assert data.shape == (100, 4, 512)

    data = y.get_data(
        0, 100, npoln=4, time_decimation_factor=2, frequency_decimation_factor=2
    )
    assert data.shape == (50, 4, 256)

    with pytest.raises(ValueError):
        y.get_data(0, 100, npoln=3)

    with pytest.raises(ValueError):
        y.get_data(0, 100, pol=5)


def test_repr(fil_file):
    y = Your(fil_file)
    assert repr(y) == f"Using <class 'str'>:\n{fil_file}"


# Ensure 'datadir' fixture is available or adapt path to test files.
# The existing conftest.py should provide 'datadir'.

def test_your_context_manager_psrfits(datadir):
    fits_file = os.path.join(datadir, "28.fits") # Using 28.fits as per earlier successful test addition
    assert os.path.exists(fits_file), f"Test file not found: {fits_file}"
    with your.Your(fits_file) as y:
        _ = y.your_header.source_name # Perform some action
    # Check if the astropy FITS file object is closed
    assert hasattr(y, 'formatclass') and hasattr(y.formatclass, 'fits'), "formatclass or fits attribute missing"
    assert y.formatclass.fits is not None, "fits object is None"
    # astropy's HDUList has a _file attribute which is the actual file object
    assert hasattr(y.formatclass.fits, '_file') and y.formatclass.fits._file is not None, "_file attribute missing or None"
    assert y.formatclass.fits._file.closed, "PSRFITS file was not closed by context manager"

def test_your_context_manager_filterbank(datadir):
    fil_file = os.path.join(datadir, "28.fil") # Using 28.fil as per earlier successful test addition
    assert os.path.exists(fil_file), f"Test file not found: {fil_file}"
    with your.Your(fil_file) as y:
        _ = y.your_header.source_name # Perform some action
    # Check if the sigproc file object is closed
    assert hasattr(y, 'formatclass') and hasattr(y.formatclass, 'fp'), "formatclass or fp attribute missing"
    assert y.formatclass.fp is not None, "fp object is None"
    assert y.formatclass.fp.closed, "Filterbank file object (fp) was not closed by context manager"

    # Check if the mmap object is closed
    assert hasattr(y.formatclass, '_mmdata') and y.formatclass._mmdata is not None, "_mmdata attribute missing or None"
    if hasattr(y.formatclass._mmdata, 'closed'): # Python 3.2+
        assert y.formatclass._mmdata.closed, "Filterbank mmap object (_mmdata) was not closed by context manager (using .closed)"
    else:
        # Fallback for older Python: try to access a property that would fail on a closed mmap
        with pytest.raises(ValueError, match="mmap closed|cannot access closed mmap"):
            y.formatclass._mmdata.size()


def test_dispersion_delay(y):
    assert pytest.approx(y.dispersion_delay(1), rel=1e-3) == 0.0013160529703817566
