import logging
import math
import os


def generate_dm_list(dm_start: float, dm_end: float, dt: float, ti: float, f0: float, df: float, nchans: int,
                     tol: float) -> list:
    """
    Code to generate Heimdall's DM list. Taken from [dedisp](https://github.com/ajameson/dedisp/blob/master/src/kernels.cuh#L56)

    Args:

        dm_start (float): Start DM

        dm_end (float): End DM

        dt (float): Sampling interval (in seconds)

        ti (float): pulse width (in seconds)

        f0 (float): Frequency of first channel (MHz)

        df (float): Channel Bandwidth (MHz)

        nchans (int): Number of channels

        tol (float): Tolerance level

    Returns:

        list : List of DMs for which Heimdall will do the search

    """
    dt *= 1e6
    ti *= 1e6
    center_freq = (f0 + (nchans / 2) * df) * 1e-3
    a = 8.3 * df / (center_freq ** 3)
    b = a ** 2 * nchans ** 2 / 16
    c = (dt ** 2 + ti ** 2) * (tol ** 2 - 1)

    dm_list = []
    dm_list.append(dm_start)
    while dm_list[-1] < dm_end:
        k = c + tol ** 2 * a ** 2 * dm_list[-1] ** 2
        dm = (b * dm_list[-1] + math.sqrt(-a ** 2 * b * dm_list[-1] ** 2 + (a ** 2 + b) * k)) / (a ** 2 + b)
        dm_list.append(dm)
    return dm_list


class HeimdallManager:
    """
    So you want to run heimdall, here is wrapper class which will allow you to do just that.

    Args:

        dada_key (hex): use PSRDADA hexidecimal key

        filename (str): process specified SIGPROC filterbank file

        verbosity (str): v, V, g, G increase verbosity level

        nsamps_gulp (int): number of samples to be read at a time

        beam (int) : over-ride beam number

        baseline_length (float): number of seconds over which to smooth the baseline

        output_dir (str) : create all output files in specified path

        dm (list): min and max DM

        dm_tol (float): SNR loss tolerance between each DM trial

        zap_chans (int): zap all channels between start and end channels inclusive

        max_giant_rate (int): limit the maximum number of individual detections per minute to nevents

        dm_nbits (int): number of bits per sample in dedispersed time series

        gpu_id (int): run on specified GPU

        no_scrunching (bool): don't use an adaptive time scrunching during dedispersion

        rfi_tol (float): RFI exicision threshold limits

        rfi_no_narrow (bool): disable narrow band RFI excision

        rfi_no_broad (bool): disable 0-DM RFI excision

        boxcar_max (int): maximum boxcar width in samples

        fswap (bool): swap channel ordering for negative DM - SIGPROC 2,4 or 8 bit only

        min_tscrunch_width: vary between high quality (large value) and high performance (low value)

    """

    def __init__(self, dada_key=None, filename=None, verbosity=None, nsamps_gulp=262144, beam=None, baseline_length=2,
                 output_dir=None, dm=None, dm_tol=1.25, zap_chans=None, max_giant_rate=None, dm_nbits=32, gpu_id=None,
                 no_scrunching=False, rfi_tol=5, rfi_no_narrow=False, rfi_no_broad=False, boxcar_max=4096, fswap=None,
                 min_tscrunch_width=None):

        self.k = dada_key
        self.f = filename
        self.verbosity = verbosity
        self.nsamps_gulp = nsamps_gulp
        self.beam = beam
        self.baseline_length = baseline_length
        self.output_dir = output_dir
        self.dm = dm
        self.dm_tol = dm_tol
        self.zap_chans = zap_chans
        self.max_gaint_rate = max_giant_rate
        self.dm_nbits = dm_nbits
        self.gpu_id = gpu_id
        self.no_scrunching = no_scrunching
        self.rfi_tol = rfi_tol
        self.rfi_no_narrow = rfi_no_narrow
        self.rfi_no_broad = rfi_no_broad
        self.boxcar_max = boxcar_max
        self.fswap = fswap
        self.min_tscrunch_width = min_tscrunch_width

        if (self.k is None) and (self.f is None):
            raise IOError(f"Need either a dada key or a filterbank file to run")

    def run(self):
        """

        Make the heimdall command and run it.

        """
        cmd = 'heimdall '
        for attribute, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, list):
                    if attribute == 'zap_chans':
                        for chans in value:
                            cmd += ' -zap_chans '
                            cmd += str(chans) + ' '
                            cmd += str(chans)
                    else:
                        cmd += str(f' -{attribute} ')
                        cmd += ' '.join(map(str, value))
                elif attribute == 'verbosity':
                    if value in ['V', 'v', 'g', 'G']:
                        cmd += str(f' -{value} ')
                    else:
                        logging.warning(f"Allowed verbosity is v,V,g,G")
                        logging.warning(f"Using v for now!")
                        cmd += f" -v "
                elif attribute == 'no_scrunching' or attribute == 'rfi_no_narrow' or attribute == 'rfi_no_broad':
                    if value:
                        cmd += str(f' -{attribute}')
                else:
                    cmd += str(f' -{attribute} {value}')

        logging.info(f"Using cmd: \n{cmd}")
        os.system(cmd)
