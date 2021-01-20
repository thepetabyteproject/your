import logging

import numpy as np

from your.utils.math import closest_number

logger = logging.getLogger(__name__)
from skimage.transform import resize

import argparse
import json
import os


def _decimate(data, decimate_factor, axis, pad=False, **kwargs):
    """
    Decimate an input array by an input factor. Optionally padding can also be done.

    Args:
        data (np.ndarray): data array to decimat
        decimate_factor (int): number of samples to combine
        axis (int): axis along which decimation is to be done
        pad (bool): Whether to apply padding if the data axis length is not a multiple of decimation factor
        **kwargs: arguments of padding

    Returns:
        np.ndarray: Decimated array

    """
    if data.shape[axis] % decimate_factor and pad is True:
        logger.info(f"padding along axis {axis}")
        pad_width = closest_number(data.shape[axis], decimate_factor)
        data = pad_along_axis(data, data.shape[axis] + pad_width, axis=axis, **kwargs)
    elif data.shape[axis] % decimate_factor and pad is False:
        raise AttributeError(
            "Axis length should be a multiple of decimate_factor. Use pad=True to force decimation"
        )

    if axis:
        return data.reshape(
            int(data.shape[0]),
            int(data.shape[1] // decimate_factor),
            int(decimate_factor),
        ).mean(2)
    else:
        return data.reshape(
            int(data.shape[0] // decimate_factor),
            int(decimate_factor),
            int(data.shape[1]),
        ).mean(1)


def _resize(data, size, axis, **kwargs):
    """
    Resize an input array to a required size

    Args:
        data (np.ndarray): data array to resize
        size (int): required size of the axis
        axis (int): axis long which resizing is to be done
        **kargs: arguments for skimage.transform resize function

    Returns:
        np.ndarray: Resized array

    """
    if axis:
        return resize(data, (data.shape[0], size), **kwargs)
    else:
        return resize(data, (size, data.shape[1]), **kwargs)


def crop(data, start_sample, length, axis):
    """
    Crops the input array to a required size

    Args:
        data (np.ndarray): Data array to crop
        start_sample (int): Sample to start the output cropped array
        length (int): Final Length along the axis of the output
        axis (int): Axis to crop

    Returns:
        np.ndarray: Cropped array

    """
    if data.shape[axis] > start_sample + length:
        if axis:
            return data[:, start_sample : start_sample + length]
        else:
            return data[start_sample : start_sample + length, :]
    elif data.shape[axis] == length:
        return data
    else:
        raise OverflowError("Specified length exceeds the size of data")


def pad_along_axis(array: np.ndarray, target_length, loc="end", axis=0, **kwargs):
    """
    Pads data along the required axis on the input array to reach a target size

    Args:
        array (np.ndarray): Input array to pad
        target_length (int): Required length of the axis
        loc (int): Location to pad: start: pad in beginning, end: pad in end, else: pad equally on both sides
        axis (int): Axis to pad along
        **kwargs: args for np.pad

    Returns:
        np.ndarray: Padded array

    """
    pad_size = target_length - array.shape[axis]
    axis_nb = len(array.shape)

    if pad_size < 0:
        return array

    npad = [(0, 0) for x in range(axis_nb)]

    if loc == "start":
        npad[axis] = (int(pad_size), 0)
    elif loc == "end":
        npad[axis] = (0, int(pad_size))
    else:
        npad[axis] = (int(pad_size // 2), int(pad_size // 2))

    return np.pad(array, pad_width=npad, **kwargs)


def check_file_exist(file):
    """

    Args:
        file: Path of file to check

    Raises:
        IOError

    """
    if not os.path.isfile(file):
        raise IOError(f"{file} not found")


class MyEncoder(json.JSONEncoder):
    """
    Custom Encoder Class to convert any class to a JSON serializable object

    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class YourArgparseFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    """
    Allows both Raw Text Formatting and Default Args
    """

    pass
