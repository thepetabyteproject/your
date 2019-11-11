
import logging
import math
import subprocess
from functools import reduce

import numpy as np
from numba import cuda

logger = logging.getLogger(__name__)
from skimage.transform import resize

ARCSECTORAD = float('4.8481368110953599358991410235794797595635330237270e-6')
RADTODEG = float('57.295779513082320876798154814105170332405472466564')


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


def gpu_dedisperse(cand, device=0):
    """
    :param cand: Candidate object
    :param device: GPU id
    :return:
    """
    cuda.select_device(device)
    chan_freqs = cuda.to_device(np.array(cand.chan_freqs, dtype=np.float32))
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=np.uint8))
    cand_data_out = cuda.to_device(np.zeros_like(cand.data.T, dtype=np.uint8))

    @cuda.jit
    def gpu_dedisp(cand_data_in, chan_freqs, dm, cand_data_out, tsamp):
        ii, jj = cuda.grid(2)
        if ii < cand_data_in.shape[0] and jj < cand_data_in.shape[1]:
            disp_time = int(-4148808.0 * dm * (1 / (chan_freqs[0]) ** 2 - 1 / (chan_freqs[ii]) ** 2) / 1000 / tsamp)
            cand_data_out[ii, jj] = cand_data_in[ii, (jj + disp_time) % cand_data_in.shape[1]]

    threadsperblock = (32, 32)
    blockspergrid_x = math.ceil(cand_data_in.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(cand_data_in.shape[1] / threadsperblock[1])

    blockspergrid = (blockspergrid_x, blockspergrid_y)

    gpu_dedisp[blockspergrid, threadsperblock](cand_data_in, chan_freqs, float(cand.dm), cand_data_out,
                                               float(cand.tsamp))

    cand.dedispersed = cand_data_out.copy_to_host().T

    cuda.close()

    return cand


def gpu_dmt(cand, device=0):
    """
    :param cand: Candidate object
    :param device: GPU id
    :return:
    """
    cuda.select_device(device)
    chan_freqs = cuda.to_device(np.array(cand.chan_freqs, dtype=np.float32))
    dm_list = cuda.to_device(np.linspace(0, 2 * cand.dm, 256, dtype=np.float32))
    dmt_return = cuda.to_device(np.zeros((256, cand.data.shape[0]), dtype=np.float32))
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=np.uint8))

    @cuda.jit
    def gpu_dmt(cand_data_in, chan_freqs, dms, cand_data_out, tsamp):
        ii, jj, kk = cuda.grid(3)
        if ii < cand_data_in.shape[0] and jj < cand_data_in.shape[1] and kk < dms.shape[0]:
            disp_time = int(
                -1 * 4148808.0 * dms[kk] * (1 / (chan_freqs[0]) ** 2 - 1 / (chan_freqs[ii]) ** 2) / 1000 / tsamp)
            cuda.atomic.add(cand_data_out, (kk, jj), cand_data_in[ii, (jj + disp_time) % cand_data_in.shape[1]])

    threadsperblock = (16, 8, 8)
    blockspergrid_x = math.ceil(cand_data_in.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(cand_data_in.shape[1] / threadsperblock[1])
    blockspergrid_z = math.ceil(dm_list.shape[0] / threadsperblock[2])

    blockspergrid = (blockspergrid_x, blockspergrid_y, blockspergrid_z)

    gpu_dmt[blockspergrid, threadsperblock](cand_data_in, chan_freqs, dm_list, dmt_return, float(cand.tsamp))

    cand.dmt = dmt_return.copy_to_host()

    cuda.close()

    return cand


def gpu_dedisp_and_dmt_crop(cand, device=0):
    """
    :param cand: Candidate object
    :param device: GPU id
    :return:
    """

    if cand.width < 3:
        time_decimation_factor = 1
    else:
        time_decimation_factor = cand.width // 2

    if cand.data.shape[1] < 256:
        raise IndexError(f"GPU candmaker will not work if nchans < 256.")

    frequency_decimation_factor = math.floor(cand.data.shape[1] // 256)

    logger.debug(f"Freq decimation factor: {frequency_decimation_factor}")
    logger.debug(f"Time decimation factor: {time_decimation_factor}")

    cuda.select_device(device)
    stream = cuda.stream()

    logger.debug("Created CUDA Stream")

    chan_freqs = cuda.to_device(np.array(cand.chan_freqs, dtype=np.float32), stream=stream)
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=np.float32), stream=stream)
    dmt_on_device = cuda.device_array((256, int(cand.data.shape[0] // time_decimation_factor)), dtype=np.float32,
                                      stream=stream)
    cand_dedispersed_on_device = cuda.device_array(
        (int(cand.data.shape[1] / frequency_decimation_factor), int(cand.data.shape[0] // time_decimation_factor)),
        dtype=np.float32, stream=stream)
    cand_dedispersed_out = cuda.device_array(shape=(int(cand.data.shape[1] / frequency_decimation_factor), 256),
                                             dtype=np.float32, stream=stream)
    dmt_return = cuda.device_array(shape=(256, 256), dtype=np.float32, stream=stream)
    dm_list = cuda.to_device(np.linspace(0, 2 * cand.dm, 256, dtype=np.float32), stream=stream)

    logger.debug("Allocated arrays on the GPU")

    @cuda.jit
    def crop_time(data_in, data_out, side_stride):
        ii, jj = cuda.grid(2)
        if ii < data_out.shape[0] and jj < data_out.shape[1]:
            data_out[ii, jj] = data_in[ii, jj + side_stride]

    @cuda.jit
    def gpu_dedisp(cand_data_in, chan_freqs, dm, cand_data_out, tsamp, time_decimation_factor,
                   frequency_decimation_factor):
        ii, jj = cuda.grid(2)
        if ii < cand_data_in.shape[0] and jj < cand_data_in.shape[1]:
            disp_time = int(-4148808.0 * dm * (1 / (chan_freqs[0]) ** 2 - 1 / (chan_freqs[ii]) ** 2) / 1000 / tsamp)
            cuda.atomic.add(cand_data_out, (int(ii / frequency_decimation_factor), int(jj / time_decimation_factor)),
                            cand_data_in[ii, (jj + disp_time) % cand_data_in.shape[1]])

    threadsperblock_2d = (32, 32)
    blockspergrid_x_2d_in = math.ceil(cand_data_in.shape[0] / threadsperblock_2d[0])
    blockspergrid_y_2d_in = math.ceil(cand_data_in.shape[1] / threadsperblock_2d[1])

    blockspergrid_2d_in = (blockspergrid_x_2d_in, blockspergrid_y_2d_in)

    gpu_dedisp[blockspergrid_2d_in, threadsperblock_2d, stream](cand_data_in, chan_freqs, float(cand.dm),
                                                                cand_dedispersed_on_device,
                                                                float(cand.tsamp), int(time_decimation_factor),
                                                                int(frequency_decimation_factor))

    blockspergrid_x_2d_out = math.ceil(cand_dedispersed_on_device.shape[0] / threadsperblock_2d[0])
    blockspergrid_y_2d_out = math.ceil(cand_dedispersed_on_device.shape[1] / threadsperblock_2d[0])

    blockspergrid_2d_out = (blockspergrid_x_2d_out, blockspergrid_y_2d_out)
    crop_time[blockspergrid_2d_out, threadsperblock_2d, stream](cand_dedispersed_on_device, cand_dedispersed_out,
                                                                int(int(cand_dedispersed_on_device.shape[1] / 2) - 128))
    cand.dedispersed = cand_dedispersed_out.copy_to_host(stream=stream).T

    logger.debug("cand.dedisersed set!")

    disp_time = np.zeros(shape=(cand_data_in.shape[0], 256), dtype=np.int)
    for idx, dms in enumerate(np.linspace(0, 2 * cand.dm, 256)):
        disp_time[:, idx] = np.round(
            -1 * 4148808.0 * dms * (1 / (cand.chan_freqs[0]) ** 2 - 1 / (cand.chan_freqs) ** 2) / 1000 / cand.tsamp)

    all_delays = cuda.to_device(disp_time, stream=stream)

    @cuda.jit
    def gpu_dmt(cand_data_in, all_delays, dms, cand_data_out, time_decimation_factor):
        ii, jj, kk = cuda.grid(3)
        if ii < cand_data_in.shape[0] and jj < cand_data_in.shape[1] and kk < dms.shape[0]:
            cuda.atomic.add(cand_data_out, (kk, int(jj / time_decimation_factor)),
                            cand_data_in[ii, (jj + all_delays[ii, kk]) % cand_data_in.shape[1]])

    threadsperblock_3d = (1, 32, 32)
    blockspergrid_x = math.ceil(cand_data_in.shape[0] / threadsperblock_3d[0])
    blockspergrid_y = math.ceil(cand_data_in.shape[1] / threadsperblock_3d[1])
    blockspergrid_z = math.ceil(dm_list.shape[0] / threadsperblock_3d[2])

    blockspergrid = (blockspergrid_x, blockspergrid_y, blockspergrid_z)

    gpu_dmt[blockspergrid, threadsperblock_3d, stream](cand_data_in, all_delays, dm_list, dmt_on_device,
                                                       int(time_decimation_factor))

    crop_time[blockspergrid_2d_out, threadsperblock_2d, stream](dmt_on_device, dmt_return,
                                                                int(int(cand_dedispersed_on_device.shape[1] / 2) - 128))

    cand.dmt = dmt_return.copy_to_host(stream=stream)

    logger.debug("cand.dmt set!")

    cuda.close()
    return cand


def get_gpu_memory_map(gpu_id):
    """Get the current gpu free_mem.
    """
    cmd_list = ['nvidia-smi', "-i", f"{gpu_id}", '--query-gpu=memory.free', '--format=csv,nounits,noheader']
    result = subprocess.check_output(cmd_list)
    return int(result.decode())
