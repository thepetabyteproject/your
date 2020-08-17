import os

import numpy as np
import pytest

from your.candidate import Candidate

os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
_install_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="function", autouse=True)
def cand():
    fil_file = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=fil_file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    return cand


def test_Candidate():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    cand = Candidate(fp=fits_file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256,
                     device=0)
    assert np.isclose(cand.dispersion_delay(), 0.6254989199749227, atol=1e-3)


def test_candidate_chunk(cand):
    cand.get_chunk()
    assert np.isclose(np.mean(cand.data), 128, atol=1)


def test_dedispersion_none(cand):
    cand.dedisperse()
    assert cand.dedispersed == None


def test_dedisperse(cand):
    cand.get_chunk()
    cand.dedisperse()
    assert np.isclose(np.max(cand.dedispersed.T.sum(0)), 47527, atol=1)
    assert np.isclose(np.max(cand.dedispersets()), 47527, atol=1)


def test_snr_none(cand):
    assert cand.get_snr() == None


def test_optimize_dm(cand):
    assert cand.optimize_dm() == None


def test_dmtime_snr_opt_snr(cand):
    cand.get_chunk()
    cand.dedisperse()
    cand.dmtime()
    assert cand.dmt.shape[0] == 256

    fnout = cand.save_h5()
    assert os.path.isfile(fnout)
    os.remove(fnout)

    assert pytest.approx(cand.get_snr(), rel=2) == 13
    assert pytest.approx(cand.optimize_dm()[0], rel=2) == 475
