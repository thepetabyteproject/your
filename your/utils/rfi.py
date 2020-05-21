import numpy as np
from scipy.signal import savgol_filter as sg


def savgol_filter(data, foff, fw=15, sig=6):
    """
    Apply savgol filter to the data

    Args:
    
        data (numpy.ndarray): bandpass of the data

        foff (float): channel bandwidth (MHz)

        fw (float): frequency window (MHz)
        
        sig (float): sigma value to apply cutoff on

    Returns (numpy.ndarray): mask for channels

    """
    window = int(np.ceil(fw / np.abs(foff)) // 2 * 2 + 1)
    y = sg(data, window, 2)
    sub = data - y
    sigma = sig * np.std(sub)
    mask = (sub > sigma) | (sub < -sigma)
    return mask



def spectral_kurtosis(data, N=1, d=None):
    """
    Compute spectral kurtosis

    Args:

        data (numpy.ndarray): 2D frequency time data

        N (int): Number of accumulations on the FPGA

        d (float): shape factor


    Returns (numpy.ndarray): Spectral Kurtosis along frequency axis

    """
    S1 = data.sum(0)
    S2 = (data ** 2).sum(0)
    M = data.shape[0]
    if d is None:
        d = (np.nanmean(data.ravel()) / np.nanstd(data)) ** 2
    return ((M * d * N) + 1) * ((M * S2 / (S1 ** 2)) - 1) / (M - 1)
