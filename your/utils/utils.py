
import logging
import math
from functools import reduce

import json
import numpy as np

logger = logging.getLogger(__name__)
from skimage.transform import resize

import matplotlib
matplotlib.use('Agg')

ARCSECTORAD = float('4.8481368110953599358991410235794797595635330237270e-6')
RADTODEG = float('57.295779513082320876798154814105170332405472466564')


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
        
def save_bandpass(your_object, bandpass, chan_nos=None, mask=[], outdir=None, outname=None):
    """
    Plots and saves the bandpass
    :param your_object: Your object
    :param bandpass: Bandpass of data
    :param chan_nos: array of channel numbers
    :param mask: boolean array of channel mask 
    :param outdir: output directory to save the plot
    :return: 

    """
    
    freqs = your_object.chan_freqs
    foff = your_object.your_header.foff
        
    if not outdir:
        outdir = './'

    if chan_nos is None:
        chan_nos=np.arange(0,bandpass.shape[0])
        
    if not outname:
        bp_plot=outdir+ your_object.your_header.basename + '_bandpass.png'
    else:
        bp_plot = outname

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax11 = fig.add_subplot(111)
    if foff < 0:
        ax11.invert_xaxis()

    ax11.plot(freqs, bandpass,'k-',label="Bandpass")
    if mask is not None:
        if mask.sum():
            logging.info('Flagged %d channels',mask.sum())
            ax11.plot(freqs[mask],bandpass[mask],'ro',label="Flagged Channels")
    ax11.set_xlabel("Frequency (MHz)")
    ax11.set_ylabel("Arb. Units")
    ax11.legend()

    ax21 = ax11.twiny()
    ax21.plot(chan_nos, bandpass,alpha=0)
    ax21.set_xlabel("Channel Numbers")
    
    return plt.savefig(bp_plot,bbox_inches='tight')


def _decimate(data, decimate_factor, axis, pad=False, **kwargs):
    """

    :param data: data array to decimate
    :param decimate_factor: number of samples to combine
    :param axis: axis along which decimation is to be done
    :param pad: Whether to apply padding if the data axis length is not a multiple of decimation factor
    :param args: arguments of padding
    :return:
    """
    if data.shape[axis] % decimate_factor and pad is True:
        logger.info(f'padding along axis {axis}')
        pad_width = closest_number(data.shape[axis], decimate_factor)
        data = pad_along_axis(data, data.shape[axis] + pad_width, axis=axis, **kwargs)
    elif data.shape[axis] % decimate_factor and pad is False:
        raise AttributeError('Axis length should be a multiple of decimate_factor. Use pad=True to force decimation')

    if axis:
        return data.reshape(int(data.shape[0]), int(data.shape[1] // decimate_factor), int(decimate_factor)).mean(2)
    else:
        return data.reshape(int(data.shape[0] // decimate_factor), int(decimate_factor), int(data.shape[1])).mean(1)


def _resize(data, size, axis, **kwargs):
    """

    :param data: data array to resize
    :param size: required size of the axis
    :param axis: axis long which resizing is to be done
    :param args: arguments for skimage.transform resize function
    :return:
    """
    if axis:
        return resize(data, (data.shape[0], size), **kwargs)
    else:
        return resize(data, (size, data.shape[1]), **kwargs)


def crop(data, start_sample, length, axis):
    """

    :param data: Data array to crop
    :param start_sample: Sample to start the output cropped array
    :param length: Final Length along the axis of the output
    :param axis: Axis to crop
    :return:
    """
    if data.shape[axis] > start_sample + length:
        if axis:
            return data[:, start_sample:start_sample + length]
        else:
            return data[start_sample:start_sample + length, :]
    elif data.shape[axis] == length:
        return data
    else:
        raise OverflowError('Specified length exceeds the size of data')


def pad_along_axis(array: np.ndarray, target_length, loc='end', axis=0, **kwargs):
    """

    :param array: Input array to pad
    :param target_length: Required length of the axis
    :param loc: Location to pad: start: pad in beginning, end: pad in end, else: pad equally on both sides
    :param axis: Axis to pad along
    :return:
    """
    pad_size = target_length - array.shape[axis]
    axis_nb = len(array.shape)

    if pad_size < 0:
        return array
        # return a

    npad = [(0, 0) for x in range(axis_nb)]

    if loc == 'start':
        npad[axis] = (int(pad_size), 0)
    elif loc == 'end':
        npad[axis] = (0, int(pad_size))
    else:
        npad[axis] = (int(pad_size // 2), int(pad_size // 2))

    return np.pad(array, pad_width=npad, **kwargs)


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
    while d*d <= n:
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
        div*=pfs[ind]
        ind+=1
    return div


def dispersion_delay(your_object, dms=5_000):
    return 4148808.0 * dms * (1 / np.min(your_object.chan_freqs) ** 2 - 1 / np.max(your_object.chan_freqs) ** 2) / 1000


def find_gcd(list_of_nos):
    x = reduce(math.gcd, list_of_nos)
    return x

def dec2deg(src_dej):
    """
    dec2deg(src_dej):
       Convert the SIGPROC-style DDMMSS.SSSS declination to degrees
    """
    sign = 1.0
    if (src_dej < 0): sign = -1.0;
    xx = np.fabs(src_dej)
    dd = int(np.floor(xx / 10000.0))
    mm = int(np.floor((xx - dd * 10000.0) / 100.0))
    ss = xx - dd * 10000.0 - mm * 100.0
    return sign * ARCSECTORAD * (60.0 * (60.0 * dd + mm) + ss) * RADTODEG

def ra2deg(src_raj):
    """
    ra2deg(src_raj):
       Convert the SIGPROC-style HHMMSS.SSSS right ascension to degrees
    """
    return 15.0 * dec2deg(src_raj)


