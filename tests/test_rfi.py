from your.utils.rfi import *


def test_calc_N():
    assert calc_N(channel_bandwidth=-1, tsamp=0.001) == 1000


def test_savgol_filter_on_noise():
    d = np.random.random(100)
    m = savgol_filter(d, -1, 15, 4)
    assert m.sum() == 0


def test_savgol_filter_on_impulse():
    d = np.random.random(100)
    d = d + np.sort(np.random.random(100)) ** 5
    d[10:12] = 5
    m = savgol_filter(d, -1, 15, 4)
    assert m[10:12].sum() == 2


def test_spectral_kurtosis_on_noise():
    d = np.random.random(100)
    sk = spectral_kurtosis(d, 1, None)
    assert np.isclose(sk, 1, atol=0.1)


def test_spectral_kurtosis_on_impulse():
    d = np.random.random(100)
    d[10:12] = 5
    sk = spectral_kurtosis(d, 1, None)
    assert np.isclose(sk, 1, atol=0.1)
