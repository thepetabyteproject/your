import numpy as np

from your.candidate import Candidate

import os
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_Candidate():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    cand = Candidate(fp=fits_file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    assert np.isclose(cand.dispersion_delay(), 0.6254989199749227, atol=1e-3)


def test_candidate_chunk_and_dedispersion():
    fil_file = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=fil_file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    cand.get_chunk()
    assert np.isclose(np.mean(cand.data), 128, atol=1)
    cand.dedisperse()
    assert np.isclose(np.max(cand.dedispersed.T.sum(0)), 47527, atol=1)
    assert np.isclose(np.max(cand.dedispersets()), 47527, atol=1)

    fnout = cand.save_h5()
    assert os.path.isfile(fnout)
    os.remove(fnout)
