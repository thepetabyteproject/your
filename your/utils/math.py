import math
from functools import reduce

import numpy as np


def closest_number(big_num, small_num):
    """
    Finds the difference between the closest multiple of a smaller number with respect to a bigger number
    :param big_num: The bigger number to find the closest of
    :param small_num: Number whose multiple is to be found and subtracted
    :return:
    """
    if big_num % small_num == 0:
        return 0
    else:
        q = big_num // small_num
        return (q + 1) * small_num - big_num


def primes(n):
    """
    Returns all the prime factors of a positive number
    :param n: input positive number
    """
    primfac = []
    d = 2
    while d * d <= n:
        while (n % d) == 0:
            primfac.append(d)
            n //= d
        d += 1
    if n > 1:
        primfac.append(n)
    return primfac


def closest_divisor(n, m):
    """
    Calculates the divisor of n, which is closest to (i.e bigger than) m
    :param n: larger number of which divisor is to be found
    :param m: divisor closest to this number
    """
    pfs = primes(n)
    div = 1
    ind = 0
    while div < m:
        div *= pfs[ind]
        ind += 1
    return div


def find_gcd(list_of_nos):
    x = reduce(math.gcd, list_of_nos)
    return x


def normalise(data):
    """
    Noramlise the data by unit standard deviation and zero median
    :param data: data
    :return:
    """
    data = np.array(data, dtype=np.float32)
    data -= np.median(data)
    data /= np.std(data)
    return data
