import logging
import math
from functools import reduce

import numpy as np
from scipy import stats


def bandpass_fitter(
    bandpass: float, poly_order: int = 20, mask_sigma: float = 6
) -> float:
    """
    Fits bandpasses by polyfitting the bandpass, looking for channels that
    are far from this fit, excluding these channels and refitting the bandpass

    Args:
        bandpass: the bandpass to fit

        polyorder: order of polynomial to fit

        mask_sigma: standard deviation at which to mask outlying channels

    Returns:
        Fit to bandpass
    """
    channels = np.arange(0, len(bandpass))
    fit_values = np.polyfit(channels, bandpass, poly_order)  # fit a polynomial
    poly = np.poly1d(fit_values)  # get the values of the fitted bandpass
    diff = bandpass - poly(
        channels
    )  # find the difference between fitted and real bandpass
    std_diff = stats.median_abs_deviation(diff, scale="normal")
    logging.info(f"Standard Deviation of fit: {std_diff:.4}")
    mask = np.abs(diff - np.median(diff)) < mask_sigma * std_diff

    fit_values_clean = np.polyfit(
        channels[mask], bandpass[mask], poly_order
    )  # refit masking the outliers
    poly_clean = np.poly1d(fit_values_clean)
    best_fit_bandpass = poly_clean(channels)
    logging.info(
        f"chi^2: {stats.chisquare(bandpass, best_fit_bandpass, poly_order)[0]:.4}"
    )
    return best_fit_bandpass


def closest_number(big_num, small_num):
    """
    Finds the difference between the closest multiple of a smaller number with respect to a bigger number

    Args:
        big_num (int): The bigger number to find the closest of
        small_num (int) : Number whose multiple is to be found and subtracted

    Returns:
        int : The difference between the closest multiple of a smaller number with respect to a bigger number

    """
    if big_num % small_num == 0:
        return 0
    else:
        q = big_num // small_num
        return (q + 1) * small_num - big_num


def primes(n):
    """
    All the prime factors of a positive number

    Args:

        n (int): a positive number

    Returns:
        list: List of primes
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

    Args:
        n (int):  larger number of which divisor is to be found
        m (int): divisor closest to this number


    Returns:
        int: The divisor of n, which is closest to (i.e bigger than) m

    """
    pfs = primes(n)
    div = 1
    ind = 0
    while div < m:
        div *= pfs[ind]
        ind += 1
    return div


def find_gcd(list_of_nos):
    """
    Greatest Common Divisor for a list of nos

    Args:

        list_of_nos (list): list of numbers

    Returns:

        GCD

    """
    x = reduce(math.gcd, list_of_nos)
    return x


def normalise(data):
    """
    Subtract median, divide by standard deviations

    Args:
        data (numpy.ndarray): data

    Returns:
        numpy.ndarray: normalised data

    """
    data = np.array(data, dtype=np.float32)
    data -= np.median(data)
    data /= np.std(data)
    return data


def smad_plotter(freq_time, sigma=5.0, clip=True):
    """
    Spectral Median Absolute Deviation clipper

    Args:
        freq_time (np.ndarray): the frequency time data
        sigma (float): sigma at which to clip data
        clip (bool): if true replaces clips the data else replaces it with zeroes

    Returns:
        np.ndarray: clipped/flagged data
    """
    medians = np.median(freq_time, axis=0)
    sigs = 1.4826 * sigma * stats.median_abs_deviation(freq_time, axis=0)
    if clip:
        return np.clip(freq_time, a_min=medians - sigs, a_max=medians + sigs)
    else:
        for j, sig in enumerate(sigs):
            freq_time[np.absolute(freq_time[:, j] - medians[j]) >= sig, j] = 0.0
        return freq_time
