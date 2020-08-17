from your.utils.gpu import *
from your.candidate import Candidate
from your.utils.misc import crop

from numba import cuda
import pytest
import os
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
_install_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.mark.skipif(not cuda.is_available(), reason='requires a GPU')
def test_gpu_dedisperse():
    file = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    cand.get_chunk()
    cand.dedisperse(target='GPU')
    g_dedisp = cand.dedispersed
    cand.dedisperse(target='CPU')
    c_dedisp = cand.dedispersed
    assert np.isclose(np.mean(g_dedisp - c_dedisp), 0, atol=1)
    assert np.isclose(np.max(cand.dedispersed.T.sum(0)), 47527, atol=1)


@pytest.mark.skipif(not cuda.is_available(), reason='requires a GPU')
def test_gpu_dmt():
    file = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=file, dm=10, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    cand.get_chunk()
    cand.dmtime(target='GPU')
    g_dmt = cand.dmt
    cand.dmtime(target='CPU')
    c_dmt = cand.dmt
    assert cand.dmt.shape[0] == 256
    assert np.isclose(np.mean(g_dmt - c_dmt), 0, atol=1)
    assert np.max(g_dmt - c_dmt)/np.max(g_dmt) < 0.05


@pytest.mark.skipif(not cuda.is_available(), reason='requires a GPU')
def test_gpu_dedisp_dmt_crop():
    file = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=file, dm=10, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    cand.get_chunk()
    cand = gpu_dedisp_and_dmt_crop(cand)
    g_dmt = cand.dmt
    g_dedisp = cand.dedispersed
    assert cand.dedispersed.shape[0] == 256
    assert cand.dmt.shape[1] == 256

    cand.dedisperse()
    cand.dmtime()
    crop_start_sample_ft = cand.dedispersed.shape[0] // 2 - 256 // 2
    crop_start_sample_dmt = cand.dmt.shape[1] // 2 - 256 // 2
    c_dmt = crop(cand.dmt, crop_start_sample_dmt, 256, 1)
    c_dedisp = crop(cand.dedispersed, crop_start_sample_ft, 256, 0)

    assert np.isclose(np.sum(g_dmt - c_dmt), 0, atol=1)
    assert np.isclose(np.sum(g_dedisp - c_dedisp), 0, atol=1)
