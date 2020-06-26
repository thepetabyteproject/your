import numpy as np
from scipy import stats
from scipy.signal import savgol_filter as sg


def savgol_filter(data, foff, fw=15, sig=6):
    """
    Apply savgol filter to the data. See [Agarwal el al. 2020](https://arxiv.org/abs/2003.14272) for details.

    Args:
    
        data (numpy.ndarray): bandpass of the data

        foff (float): channel bandwidth (MHz)

        fw (float): frequency window (MHz)
        
        sig (float): sigma value to apply cutoff on

    Returns:

        numpy.ndarray: mask for channels

    """
    window = int(np.ceil(fw / np.abs(foff)) // 2 * 2 + 1)
    y = sg(data, window, 2)
    sub = data - y
    sigma = sig * np.std(sub)
    mask = (sub > sigma) | (sub < -sigma)
    return mask


def spectral_kurtosis(data, N=1, d=None):
    """
    Compute spectral kurtosis. See [Nita et al. (2016)](https://doi.org/10.1109/RFINT.2016.7833535) for details.

    Args:

        data (numpy.ndarray): 2D frequency time data

        N (int): Number of accumulations on the FPGA

        d (float): shape factor


    Returns:

         numpy.ndarray: Spectral Kurtosis along frequency axis

    """
    data = data.astype('float32')
    S1 = data.sum(0)
    S2 = (data ** 2).sum(0)
    M = data.shape[0]
    if d is None:
        d = (np.nanmean(data.ravel()) / np.nanstd(data)) ** 2
    return ((M * d * N) + 1) * ((M * S2 / (S1 ** 2)) - 1) / (M - 1)


def sk_filter(data, foff, nchans, tsamp, N=None, d=1, sig=5):
    """
    Apply Spectral Kurtosis filter to the data

    Args:

        data (numpy.ndarray): 2D frequency time data

        foff (float): channel bandwidth (MHz)

        nchans (int): number of channels 

        tsamp (float): sampling time (seconds)
        
        N (int): Number of accumulations on the FPGA

        d (float): shape factor

        sig (float): sigma value to apply cutoff on


    Returns:

         numpy.ndarray: mask for channels

    """
    if not N:
        N = calc_N(foff, nchans, tsamp)
    sk = spectral_kurtosis(data, d=d, N=N)
    nan_mask = np.isnan(sk)
    sk[nan_mask] = np.nan
    sk_c = sk[~nan_mask]
    std = 1.4826*stats.median_absolute_deviation(sk_c)
    h = np.median(sk_c) + sig*std
    l = np.median(sk_c) - sig*std
    mask = (sk < h) & (sk > l)
    return ~mask


def calc_N(foff, nchans, tsamp):
    """

    Calculates number of accumulations on FPGA

    Args:

        foff (float): channel bandwidth (MHz)

        nchans (int): number of channels

        tsamp (float): sampling time (seconds)


    Returns:

        int: FPGA accumulation length

    """

    tn = nchans*np.abs(1/(2*foff*nchans*10**6))
    return np.round(tsamp/tn)

