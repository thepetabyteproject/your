import os

import numpy as np
import pytest

from your.candidate import Candidate

os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
_install_dir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="function", autouse=True)
def cand_fil():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    cand = Candidate(
        fp=fil_file,
        dm=475.28400,
        tcand=2.0288800,
        width=2,
        label=-1,
        snr=16.8128,
        min_samp=256,
        device=0,
    )
    return cand


@pytest.fixture(scope="function", autouse=True)
def cand_fits():
    fil_file = os.path.join(_install_dir, "data/28.fits")
    cand = Candidate(
        fp=fil_file,
        dm=475.28400,
        tcand=2.0288800,
        width=2,
        label=-1,
        snr=16.8128,
        min_samp=256,
        device=0,
    )
    return cand


def test_Candidate():
    fits_file = os.path.join(_install_dir, "data/28.fits")
    cand = Candidate(
        fp=fits_file,
        dm=475.28400,
        tcand=2.0288800,
        width=2,
        label=-1,
        snr=16.8128,
        min_samp=256,
        device=0,
    )
    assert np.isclose(cand.dispersion_delay(), 0.6254989199749227, atol=1e-3)


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_candidate_chunk(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    assert np.isclose(np.mean(cand.data), 128, atol=1)


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_dedispersion_none(cand, request):
    cand = request.getfixturevalue(cand)
    cand.dedisperse()
    assert cand.dedispersed == None


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_dedisperse(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dedisperse()
    assert np.isclose(np.max(cand.dedispersed.T.sum(0)), 47527, atol=1)
    assert np.isclose(np.max(cand.dedispersets()), 47527, atol=1)


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_snr_none(cand, request):
    cand = request.getfixturevalue(cand)
    assert cand.get_snr() == None


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_optimize_dm(cand, request):
    cand = request.getfixturevalue(cand)
    assert cand.optimize_dm() == None


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_dmtime_snr_opt_snr(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dedisperse()
    cand.dmtime()
    assert cand.dmt.shape[0] == 256

    fnout = cand.save_h5()
    assert os.path.isfile(fnout)
    os.remove(fnout)

    assert pytest.approx(cand.get_snr(), rel=2) == 13
    assert pytest.approx(cand.optimize_dm()[0], rel=2) == 475


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_h5(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dedisperse()
    cand.dmtime()
    cand.save_h5()
    assert os.path.isfile(str(cand.id) + ".h5")
    os.remove(str(cand.id) + ".h5")


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_decimate_on_dedispersed(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dedisperse()
    ts_orig = cand.dedispersed.T.mean(0)
    orig_dedispersed_data = cand.dedispersed
    orig_std = np.std(orig_dedispersed_data)
    orig_mean = np.mean(orig_dedispersed_data)
    bp_orig = orig_dedispersed_data.mean(0)

    cand.decimate(key="ft", axis=0, pad=True, decimate_factor=4, mode="median")
    assert cand.dedispersed.shape[0] == 248
    assert np.isclose(np.std(cand.dedispersed), orig_std / 2, atol=2)
    assert np.isclose(np.mean(cand.dedispersed), orig_mean, atol=1)

    cand.dedispersed = orig_dedispersed_data
    cand.decimate(key="ft", axis=1, pad=True, decimate_factor=16, mode="median")
    assert cand.dedispersed.shape[1] == 21
    assert np.isclose(np.std(cand.dedispersed), orig_std / 4, atol=2)
    assert np.isclose(np.mean(cand.dedispersed), orig_mean, atol=1)

    cand.dedispersed = orig_dedispersed_data
    cand.decimate(key="ft", axis=1, pad=True, decimate_factor=336, mode="median")
    assert cand.dedispersed.shape == (991, 1)
    assert (ts_orig - cand.dedispersed[:, 0]).sum() == 0

    cand.dedispersed = orig_dedispersed_data
    cand.decimate(key="ft", axis=0, pad=True, decimate_factor=991, mode="median")
    assert cand.dedispersed.shape == (1, 336)
    assert (bp_orig - cand.dedispersed[0, :]).sum() == 0


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_decimate_on_dmt(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dmtime()
    dmt_orig = cand.dmt
    orig_mean = np.mean(dmt_orig)

    cand.decimate(key="dmt", axis=0, pad=True, decimate_factor=4, mode="median")
    assert cand.dmt.shape == (256 // 4, 991)
    assert np.isclose(np.mean(cand.dmt), orig_mean, atol=1)

    cand.dmt = dmt_orig
    cand.decimate(key="dmt", axis=1, pad=True, decimate_factor=4, mode="median")
    assert cand.dmt.shape == (256, 248)
    assert np.isclose(np.mean(cand.dmt), orig_mean, atol=1)

    with pytest.raises(AttributeError):
        cand.decimate(key="at", axis=0, pad=True, decimate_factor=4, mode="median")


@pytest.mark.parametrize("cand", ["cand_fil", "cand_fits"])
def test_resize(cand, request):
    cand = request.getfixturevalue(cand)
    cand.get_chunk()
    cand.dedisperse()
    cand.dmtime()

    cand.resize("ft", size=200, axis=1, anti_aliasing=True, mode="constant")
    cand.resize("ft", size=300, axis=0, anti_aliasing=True, mode="constant")
    assert cand.dedispersed.shape == (300, 200)

    cand.resize("dmt", size=100, axis=1, anti_aliasing=True, mode="constant")
    cand.resize("dmt", size=500, axis=0, anti_aliasing=True, mode="constant")
    assert cand.dmt.shape == (500, 100)

    with pytest.raises(AttributeError):
        cand.resize("at", size=200, axis=1, anti_aliasing=True, mode="constant")


def test_rfi_mask():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    cand = Candidate(
        fp=fil_file,
        dm=475.28400,
        tcand=2.0288800,
        width=2,
        label=-1,
        snr=16.8128,
        min_samp=256,
        device=0,
        spectral_kurtosis_sigma=4,
        savgol_frequency_window=15,
        savgol_sigma=4,
        flag_rfi=True,
    )
    cand.get_chunk()
    assert cand.data[:, cand.rfi_mask].sum() == 0
    assert cand.data[:, 172:177].sum() == 0
    assert cand.data[:, ~cand.rfi_mask].sum() != 0


def test_kill_mask():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    km = np.zeros(336, dtype="bool")
    km[[10, 12, 25, 100, 300]] = True
    cand = Candidate(
        fp=fil_file,
        dm=475.28400,
        tcand=2.0288800,
        width=2,
        label=-1,
        snr=16.8128,
        min_samp=256,
        device=0,
        flag_rfi=False,
        kill_mask=km,
    )
    cand.get_chunk()
    assert cand.data[:, cand.kill_mask].sum() == 0
    assert cand.data[:, [10, 12, 300]].sum() == 0
    assert cand.data[:, ~cand.kill_mask].sum() != 0
