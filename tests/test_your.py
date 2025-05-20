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


def test_your_context_manager_psrfits(fits_file):
    with Your(fits_file) as y:
        # Perform some action to ensure file is opened and processed
        _ = y.your_header.source_name
    # Check if the file is closed
    # For astropy.io.fits, the actual file object is often in _file attribute of HDUList
    assert y.formatclass.fits._file.closed, "PSRFITS file was not closed by context manager"


def test_your_context_manager_filterbank(fil_file):
    with Your(fil_file) as y:
        # Perform some action to ensure file is opened and processed
        _ = y.your_header.source_name
    # Check if the sigproc file object is closed
    assert y.formatclass.fp.closed, "Filterbank file object (fp) was not closed by context manager"
    # Check if the mmap object is closed
    # For mmap objects, attempting to use them after closing raises a ValueError.
    # Or, if there's a .closed attribute (Python 3.2+ for mmap)
    if hasattr(y.formatclass._mmdata, 'closed'):
        assert y.formatclass._mmdata.closed, "Filterbank mmap object (_mmdata) was not closed by context manager"
    else:
        # Fallback for older Python versions or if .closed is not reliably set:
        # Try to access a property that would fail on a closed mmap object
        try:
            # Attempting to access a closed mmap object should raise a ValueError
            _ = y.formatclass._mmdata.size()
            # If it doesn't raise ValueError, and .closed is not available,
            # it's hard to be certain. However, the close_files method does call _mmdata.close().
            # This path indicates either mmap is not closed or .closed attribute is missing.
            # Given the implementation, we expect ValueError if closed and .closed is missing.
            assert False, "Filterbank mmap object should be closed or .closed attribute should exist and be True."
        except ValueError:
            # This is the expected behavior if the mmap object is closed and .closed is not available
            pass
        except Exception as e:
            # Any other exception is unexpected
            assert False, f"Unexpected error when checking closed status of mmap: {e}"


def test_dispersion_delay(y):
    assert pytest.approx(y.dispersion_delay(1), rel=1e-3) == 0.0013160529703817566
