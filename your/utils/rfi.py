import numpy as np
from scipy.signal import savgol_filter


def get_sg_window(foff, fw=15):
    """
    Calculates window size (number of channels)
    for savgol filter

    :param foff: channel width
    :param fw: window size in MHz
    :return: window size for savgol filter
    """
    window = fw / np.abs(foff)
    return int(np.ceil(window) // 2 * 2 + 1)


def mask_finder(data, window, sig):
    """

    :param data: bandpass
    :param window: window (number of channels) for savgol filter
    :param sig: sigma for mask generation
    :return: boolean mask with bad channel locations
    """
    y = savgol_filter(data, window, 2)
    sub = data - y
    sigma = sig * np.std(sub)
    mask = (sub > sigma) | (sub < -sigma)
    return mask


def spectral_kurtosis(data, N=1, d=None):
    """
    Spectral Kurtosis of the data
    :param data: 2D array of the data
    :param N: Accumulation length
    :param d: shape factor
    :return: Spectral Kurtosis of along the frequencies
    """
    S1 = data.sum(0)
    S2 = (data ** 2).sum(0)
    M = data.shape[0]
    if d is None:
        d = (np.nanmean(data.ravel()) / np.nanstd(data)) ** 2
    return ((M * d * N) + 1) * ((M * S2 / (S1 ** 2)) - 1) / (M - 1)
