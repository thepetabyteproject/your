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
