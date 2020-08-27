
import numpy as np
from scipy import stats
from scipy.signal import savgol_filter as sg
import logging
logger = logging.getLogger(__name__)


def savgol_filter(bandpass, channel_bandwidth, frequency_window=15, sigma=6):
    """
    Apply savgol filter to the data. See [Agarwal el al. 2020](https://arxiv.org/abs/2003.14272) for details.

    Args:
    
        bandpass (numpy.ndarray): bandpass of the data

        channel_bandwidth (float): channel bandwidth (MHz)

        frequency_window (float): frequency window (MHz)
        
        sigma (float): sigma value to apply cutoff on

    Returns:

        numpy.ndarray: mask for channels

    """
    window = int(np.ceil(frequency_window / np.abs(channel_bandwidth)) // 2 * 2 + 1)
    y = sg(bandpass, window, 2)
    sub = bandpass - y
    sigma = sigma * np.std(sub)
    mask = (sub > sigma) | (sub < -sigma)
    return mask


def spectral_kurtosis(data, N=1, d=None):
    """
    Compute spectral kurtosis. See [Nita et al. (2016)](https://doi.org/10.1109/RFINT.2016.7833535) for details.

    Args:

        data (numpy.ndarray): 2D frequency time data

        N (int): Number of accumulations on the FPGA

        d (float): shape factor



         numpy.ndarray: Spectral Kurtosis along frequency axis

    """
    data = data.astype('float32')
    S1 = data.sum(0)
    S2 = (data ** 2).sum(0)
    M = data.shape[0]
    if d is None:
        d = (np.nanmean(data.ravel()) / np.nanstd(data)) ** 2
    return ((M * d * N) + 1) * ((M * S2 / (S1 ** 2)) - 1) / (M - 1)


def sk_filter(data, channel_bandwidth, nchans, tsamp, N=None, d=1, sigma=5):
    """
    Apply Spectral Kurtosis filter to the data

    Args:

        data (numpy.ndarray): 2D frequency time data

        channel_bandwidth (float): channel bandwidth (MHz)

        nchans (int): number of channels 

        tsamp (float): sampling time (seconds)
        
        N (int): Number of accumulations on the FPGA

        d (float): shape factor

        sigma (float): sigma value to apply cutoff on


    Returns:

         numpy.ndarray: mask for channels

    """
    if not N:
        N = calc_N(channel_bandwidth, nchans, tsamp)
    sk = spectral_kurtosis(data, d=d, N=N)
    nan_mask = np.isnan(sk)
    sk[nan_mask] = np.nan
    sk_c = sk[~nan_mask]
    std = 1.4826 * stats.median_absolute_deviation(sk_c)
    h = np.median(sk_c) + sigma * std
    l = np.median(sk_c) - sigma * std
    mask = (sk < h) & (sk > l)
    return ~mask


def calc_N(channel_bandwidth, nchans, tsamp):
    """

    Calculates number of accumulations on FPGA

    Args:

        channel_bandwidth (float): channel bandwidth (MHz)

        nchans (int): number of channels

        tsamp (float): sampling time (seconds)


    Returns:

        int: FPGA accumulation length

    """

    tn = nchans * np.abs(1 / (2 * channel_bandwidth * nchans * 10 ** 6))
    return np.round(tsamp / tn)


def sk_sg_filter(data, your_object, nchans, spectral_kurtosis_sigma=6, savgol_frequency_window=15, savgol_sigma=5):
    """

    Apply Spectral Kurtosis and Savgol filter to the data

    Args:

        data (numpy.ndarray): 2D frequency time data

        your_object: Your object

        nchans (int): number of channels

        spectral_kurtosis_sigma (float): sigma value to apply cutoff on for SK filter

        savgol_frequency_window (float): frequency window for savgol filter(MHz)

        savgol_sigma (float): sigma value to apply cutoff on for savgol filter


    Returns:

         numpy.ndarray: mask for channels

    """
    
    logger.info(f'Applying spectral kurtosis filter with sigma={spectral_kurtosis_sigma}')
    sk_mask = sk_filter(data=data, channel_bandwidth=your_object.your_header.foff, nchans=nchans, tsamp=your_object.your_header.tsamp,
                        sigma=spectral_kurtosis_sigma)
    bp = data.sum(0)[~sk_mask]
    logger.info(f'Applying savgol filter with frequency_window={savgol_frequency_window} and sigma={savgol_sigma}')
    sg_mask = savgol_filter(bandpass=bp, channel_bandwidth=your_object.your_header.foff, frequency_window=savgol_frequency_window,
                            sigma=savgol_sigma)
    mask = np.zeros(data.shape[1], dtype=np.bool)
    mask[sk_mask] = True
    mask[np.where(mask == False)[0][sg_mask]] = True
    return mask
