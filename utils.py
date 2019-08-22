import numpy as np
import logging 
logger = logging.getLogger(__name__)
from skimage.transform import resize

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
        logging.info(f'padding along axis {axis}')
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
