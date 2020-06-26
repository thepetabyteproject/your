import numpy as np

from your.utils.math import *


def test_closest_number():
    assert 1 == closest_number(511, 256)


def test_primes():
    assert [3, 3, 5] == primes(45)


def test_closest_devisor():
    assert 3 == closest_divisor(15, 2)


def test_gcd():
    assert 5 == find_gcd([5, 10, 15])


def test_normalise():
    data = np.random.randint(0, 255, size=(256, 256, 1), dtype=np.uint8)
    data = normalise(data)
    assert data.std() == 1
    assert data.median() == 0
