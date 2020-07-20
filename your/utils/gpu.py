import logging
import math
import subprocess

import numpy as np
from numba import cuda

logger = logging.getLogger(__name__)


def gpu_dedisperse(cand, device=0):
    """

    GPU dedispersion (by rolling the array)

    Args:

        cand: Candidate instance

        device (int): GPU ID

    Returns:

        candidate object

    """
    cuda.select_device(device)
    chan_freqs = cuda.to_device(np.array(cand.chan_freqs, dtype=np.float32))
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=cand.your_header.dtype))
    cand_data_out = cuda.to_device(np.zeros_like(cand.data.T, dtype=cand.your_header.dtype))

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
                                               float(cand.your_header.tsamp))

    cand.dedispersed = cand_data_out.copy_to_host().T

    cuda.close()

    return cand


def gpu_dmt(cand, device=0):
    """

    GPU DM-Time bow-tie (by rolling the array)

    Args:

        cand: Candidate instance

        device (int): GPU ID

    Returns:

        candidate object

    """
    cuda.select_device(device)
    chan_freqs = cuda.to_device(np.array(cand.chan_freqs, dtype=np.float32))
    dm_list = cuda.to_device(np.linspace(0, 2 * cand.dm, 256, dtype=np.float32))
    dmt_return = cuda.to_device(np.zeros((256, cand.data.shape[0]), dtype=np.float32))
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=cand.data.dtype))

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

    gpu_dmt[blockspergrid, threadsperblock](cand_data_in, chan_freqs, dm_list, dmt_return,
                                            float(cand.your_header.tsamp))

    cand.dmt = dmt_return.copy_to_host()

    cuda.close()

    return cand


def gpu_dedisp_and_dmt_crop(cand, device=0):
    """

    GPU based dedispersion, DM time bow-time plot and crop it to 256x256 shaped arrays (by rolling the array)

    Args:

        cand: Candidate instance

        device (int): GPU ID

    Returns:

        candidate object

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
    cand_data_in = cuda.to_device(np.array(cand.data.T, dtype=cand.your_header.dtype), stream=stream)
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
                                                                float(cand.your_header.tsamp),
                                                                int(time_decimation_factor),
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
            -1 * 4148808.0 * dms * (
                    1 / (cand.chan_freqs[0]) ** 2 - 1 / (cand.chan_freqs) ** 2) / 1000 / cand.your_header.tsamp)

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
    """
    Get the current gpu free memory

    Args:

        gpu_id (int): GPU id

    Returns:

        int: amount of free GPU RAM
    """
    cmd_list = ['nvidia-smi', "-i", f"{gpu_id}", '--query-gpu=memory.free', '--format=csv,nounits,noheader']
    result = subprocess.check_output(cmd_list)
    return int(result.decode())
