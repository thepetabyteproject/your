import os
import tarfile
from urllib.request import urlretrieve

import numpy as np
import pytest

from your.candidate import Candidate
from your.pysigproc import SigprocFile
from your.psrfits import PsrfitsFile

import os
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
_install_dir = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="session", autouse=True)
def fil_file(tmpdir_factory):
    temp_dir_path = tmpdir_factory.mktemp("data")
    download_path = str(temp_dir_path) + '/askap_frb_180417.tgz'
    url = 'http://astro.phys.wvu.edu/files/askap_frb_180417.tgz'
    urlretrieve(url, download_path)
    frb_tar = tarfile.open(download_path)
    frb_tar.extractall(path=os.path.dirname(download_path))
    return str(temp_dir_path.join('28.fil'))


def test_pysigproc_obj(fil_file):
    fil_obj = SigprocFile(fil_file)
    assert fil_obj.nchans == 336


def test_get_data_fil(fil_file):
    fil_obj = SigprocFile(fil_file)
    data = fil_obj.get_data(0, 10)
    assert np.isclose(np.mean(data), 128, atol=1)

def test_psrfits_obj():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = PsrfitsFile([fits_file])
    assert fits_obj.nchans == 336

def test_get_data_fits():
    fits_file = os.path.join(_install_dir, 'data/28.fits')
    fits_obj = PsrfitsFile([fits_file])
    data = fits_obj.get_data(0, 10)
    assert np.isclose(np.mean(data), 128, atol=1)

def test_Candidate(fil_file):
    cand = Candidate(fp=fil_file, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    assert np.isclose(cand.dispersion_delay(), 0.6254989199749227, atol=1e-3)

def test_candidate_chunk_and_dedispersion():
    fil = os.path.join(_install_dir, 'data/28.fil')
    cand = Candidate(fp=fil, dm=475.28400, tcand=2.0288800, width=2, label=-1, snr=16.8128, min_samp=256, device=0)
    cand.get_chunk()
    assert np.isclose(np.mean(cand.data), 128, atol=1)
    cand.dedisperse()
    assert np.isclose(np.max(cand.dedispersed.T.sum(0)), 47527, atol=1)
    assert np.isclose(np.max(cand.dedispersets()), 47527, atol=1)

    fnout = cand.save_h5()
    assert os.path.isfile(fnout)
    os.remove(fnout)





