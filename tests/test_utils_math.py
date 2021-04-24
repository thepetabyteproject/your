from pytest import approx

from your.utils.math import *


def test_bandpass_fitter():
    spike_size = 128
    band = 4 * np.sin(np.linspace(0, np.pi, 1024)) + 256
    band[256] = band[256] + spike_size
    fit = bandpass_fitter(band)
    assert approx(sum(band - fit) - spike_size, rel=1e3) == 0


def test_closest_number():
    assert 1 == closest_number(511, 256)
    assert 0 == closest_number(5, 5)


def test_primes():
    assert [3, 3, 5] == primes(45)


def test_closest_divisor():
    assert 3 == closest_divisor(15, 2)


def test_gcd():
    assert 5 == find_gcd([5, 10, 15])


def test_normalise():
    data = np.random.randint(0, 255, size=(256, 256, 1), dtype=np.uint8)
    data = normalise(data)
    assert approx(np.std(data), rel=1e-3) == 1
    assert approx(np.median(data), rel=1e-3) == 0


def test_smad_plotter():
    data = np.random.normal(0, 1, size=(256, 256))
    data[32, 32] = 255
    new_data = smad_plotter(data)
    assert new_data[32, 32] < 255
    new_data = smad_plotter(data, clip=False)
    assert new_data[32, 32] == 0
