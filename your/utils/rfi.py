import numpy as np
from scipy.signal import savgol_filter


def get_sg_window(foff, fw=15):
    """
    Find window length from channel bandwidth and window size in MHz

    Args:
        foff: channel bandwidth (MHz)

        fw: frequency window (MHz)

    Returns: window length in samples

    """
    window = fw / np.abs(foff)
    return int(np.ceil(window) // 2 * 2 + 1)


def mask_finder(data, window, sig):
    """
    Run savgol filter

    Args:
        data: bandpass of the data

        window: number of samples in the window (should be odd)

        sig: sigma value to apply cutoff on


    Returns: mask for channels

    """
    y = savgol_filter(data, window, 2)
    sub = data - y
    sigma = sig * np.std(sub)
    mask = (sub > sigma) | (sub < -sigma)
    return mask


def spectral_kurtosis(data, N=1, d=None):
    """
    Compute spectral kurtosis

    Args:
        data: 2D frequency time data

        N: Number of accumulations on the FPGA

        d: shape factor


    Returns: Spectral Kurtosis along frequency axis

    """
    S1 = data.sum(0)
    S2 = (data ** 2).sum(0)
    M = data.shape[0]
    if d is None:
        d = (np.nanmean(data.ravel()) / np.nanstd(data)) ** 2
    return ((M * d * N) + 1) * ((M * S2 / (S1 ** 2)) - 1) / (M - 1)
