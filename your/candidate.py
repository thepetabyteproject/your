#!/usr/bin/env python3

import h5py
from scipy.optimize import golden

from your import Your
from your.utils.gpu import gpu_dedisperse, gpu_dmt
from your.utils.misc import *
from your.utils.misc import _decimate, _resize

logger = logging.getLogger(__name__)


class Candidate(Your):
    """
    Candidate Class

    Args:

        fp : String or a list of files. It can either filterbank or psrfits files.

        dm (float): Dispersion Measure of the candidate

        tcand (float): start time of the candidate in seconds at the highest frequency channel

        width (int): pulse width of the candidate in samples

        label (int): 1 for pulsars/FRBs, 0 for RFI

        snr (float): Signal to Noise Ratio

        min_samp (int): Minimum number of time samples

        device (int): GPU ID if using GPUs

        kill_mask (numpy.ndarray): Boolean mask of channels to kill
    """

    def __init__(self, fp=None, dm=None, tcand=0, width=0, label=-1, snr=0, min_samp=256, device=0,
                 kill_mask=None):
        Your.__init__(self, fp)
        self.dm = dm
        self.tcand = tcand
        self.width = width
        self.label = label
        self.snr = snr
        self.id = f'cand_tstart_{self.tstart:.12f}_tcand_{self.tcand:.7f}_dm_{self.dm:.5f}_snr_{self.snr:.5f}'
        self.data = None
        self.dedispersed = None
        self.dmt = None
        self.device = device
        self.min_samp = min_samp
        self.dm_opt = -1
        self.snr_opt = -1
        self.kill_mask = kill_mask

    def save_h5(self, out_dir=None, fnout=None):
        """
        Save the candidate to a hdf5 file

        Args:

            out_dir (str): path to the output directory

            fnout (str): output name of the file

        Returns:

            str: output name of the file

        """
        cand_id = self.id
        if fnout is None:
            fnout = cand_id + '.h5'
        if out_dir is not None:
            if out_dir[-1] != '/':
                out_dir = out_dir + '/'
            fnout = out_dir + fnout
        logger.info(f'Saving h5 file {fnout}.')
        with h5py.File(fnout, 'w') as f:
            f.attrs['cand_id'] = cand_id
            f.attrs['tcand'] = self.tcand
            f.attrs['dm'] = self.dm
            f.attrs['dm_opt'] = self.dm_opt
            f.attrs['snr'] = self.snr
            f.attrs['snr_opt'] = self.snr_opt
            f.attrs['width'] = self.width
            f.attrs['label'] = self.label

            f.attrs['filelist'] = self.your_header.filelist

            # Copy over header information as attributes
            file_header = vars(self.your_header)
            for key in file_header.keys():
                if key == 'dtype':
                    f.attrs[key] = np.dtype(file_header[key]).name
                else:
                    f.attrs[key] = file_header[key]

            f.attrs['tsamp'] = self.your_header.tsamp
            f.attrs['nchans'] = self.your_header.nchans
            f.attrs['foff'] = self.your_header.foff
            f.attrs['nspectra'] = self.your_header.nspectra

            freq_time_dset = f.create_dataset('data_freq_time', data=self.dedispersed, dtype=self.dedispersed.dtype,
                                              compression="gzip", compression_opts=9)
            freq_time_dset.dims[0].label = b"time"
            freq_time_dset.dims[1].label = b"frequency"

            if self.dmt is not None:
                dm_time_dset = f.create_dataset('data_dm_time', data=self.dmt, dtype=self.dmt.dtype, compression="gzip",
                                                compression_opts=9)
                dm_time_dset.dims[0].label = b"dm"
                dm_time_dset.dims[1].label = b"time"
        return fnout

    def dispersion_delay(self, dms=None):
        """
        Caluclaute the dispersion delay for the candidate DM or at given dispersion DM

        Args:

            dms (Union[float,np.ndarray]) : DM or a list of DMs

        Returns:

            Union[float, np.ndarray]: dispersion delay in seconds

        """
        if dms is None:
            dms = self.dm

        return 4148808.0 * dms * (1 / np.min(self.chan_freqs) ** 2 - 1 / np.max(self.chan_freqs) ** 2) / 1000

    def get_chunk(self, tstart=None, tstop=None, for_preprocessing=True):
        """
        Get a chunk of data. The data is saved in `self.data`.

        Args:

            tstart (float): start time of the chunk in seconds

            tstop (float): stop time of the chunk in seconds

            for_preprocessing (bool): if the data is to be preprocessed later. This will modify the number of samples
            read based on the width of the candidate

        """
        if tstart is None:
            tstart = self.tcand - self.dispersion_delay() - self.width * self.native_tsamp
        if tstop is None:
            tstop = self.tcand + self.dispersion_delay() + self.width * self.native_tsamp

        nstart = int(tstart / self.native_tsamp)
        nsamp = int((tstop - tstart) / self.native_tsamp)
        nsamp_read = nsamp

        if for_preprocessing:
            if self.width > 2:
                nsamp_read *= self.width // 2
            if nsamp_read < self.min_samp:
                nsamp_read = self.min_samp
                nstart_read = nstart - (nsamp_read - nsamp) // 2
            else:
                nstart_read = nstart
        else:
            nstart_read = nstart
        logging.debug(f'nstart_read is {nstart_read}, nsamp_read is {nsamp_read},'
                      f' nstart is {nstart}, nsamp is {nsamp}')

        nspectra = int(self.your_header.nspectra)
        if nstart_read >= 0 and nstart_read + nsamp_read <= nspectra:
            logging.debug(f'nstart_read({nstart_read})>=0 and '
                          f'nstart_read({nstart_read})+nsamp_read({nsamp_read})<=nspectra({nspectra})')
            data = self.get_data(nstart=nstart_read, nsamp=nsamp_read)
        elif nstart_read < 0:
            if nstart_read + nsamp_read <= nspectra:
                logging.debug(f'nstart_read({nstart_read})<0 and nstart_read({nstart_read})'
                              f'+nsamp_read({nsamp_read})<=nspectra({nspectra})')
                logging.debug('Padding with median in the beginning')
                d = self.get_data(nstart=0, nsamp=nsamp_read + nstart_read)
                dmedian = np.median(d, axis=0)
                data = np.ones((nsamp_read, self.your_header.nchans)) * dmedian[None, :]
                data[-nstart_read:, :] = d
            else:
                logging.debug(f'nstart_read({nstart_read})<0 and nstart_read({nstart_read})'
                              f'+nsamp_read({nsamp_read})>nspectra({nspectra})')
                logging.debug('Padding with median in the beginning and the end')
                d = self.get_data(nstart=0, nsamp=nspectra)
                dmedian = np.median(d, axis=0)
                data = np.ones((nsamp_read, self.your_header.nchans)) * dmedian[None, :]
                data[-nstart_read:-nstart_read + nspectra, :] = d
        else:
            logging.debug(f'nstart_read({nstart_read})>=0 and nstart_read({nstart_read})'
                          f'+nsamp_read({nsamp_read})>nspectra({nspectra})')
            logging.debug('Padding with median in the end')
            d = self.get_data(nstart=nstart_read, nsamp=nspectra - nstart_read)
            dmedian = np.median(d, axis=0)
            data = np.ones((nsamp_read, self.your_header.nchans)) * dmedian[None, :]
            data[:nspectra - nstart_read, :] = d

        self.data = data
        if self.kill_mask is not None:
            assert len(self.kill_mask) == self.data.shape[1]
            data_copy = self.data.copy()
            data_copy[:, self.kill_mask] = 0
            self.data = data_copy
            del data_copy
        return self

    def dedisperse(self, dms=None, target='CPU'):
        """
        Dedisperse a chunk of data. Saves the dedispersed chunk in `self.dedispersed`.

        Note:

            Our method rolls the data around while dedispersing it.

        Args:

            dms (float): The DM to dedisperse the data at.

            target (str): 'CPU' to run the code on the CPU or 'GPU' to run it on a GPU.

        """

        if dms is None:
            dms = self.dm
        if self.data is not None:
            if target == 'CPU':
                nt, nf = self.data.shape
                assert nf == len(self.chan_freqs)
                delay_time = 4148808.0 * dms * (1 / (self.chan_freqs[0]) ** 2 - 1 / (self.chan_freqs) ** 2) / 1000
                delay_bins = np.round(delay_time / self.native_tsamp).astype('int64')
                self.dedispersed = np.zeros(self.data.shape, dtype=np.float32)
                for ii in range(nf):
                    self.dedispersed[:, ii] = np.concatenate(
                        [self.data[-delay_bins[ii]:, ii], self.data[:-delay_bins[ii], ii]])
            elif target == 'GPU':
                gpu_dedisperse(self, device=self.device)
        else:
            logger.warning(f"No data in self.data, run self.get_chunk() first")
            self.dedispersed = None
        return self

    def dedispersets(self, dms=None):
        """
        Create a dedispersed time series

        Note:

            Our method rolls the data around while dedispersing it.

        Args:

            dms (float): The DM to dedisperse the data at.

        Returns:
            numpy.ndarray: Dedispersed time series.

        """
        if dms is None:
            dms = self.dm
        if self.data is not None:
            nt, nf = self.data.shape
            assert nf == len(self.chan_freqs)
            delay_time = 4148808.0 * dms * (1 / (self.chan_freqs[0]) ** 2 - 1 / (self.chan_freqs) ** 2) / 1000
            delay_bins = np.round(delay_time / self.native_tsamp).astype('int64')
            ts = np.zeros(nt, dtype=np.float32)
            for ii in range(nf):
                ts += np.concatenate([self.data[-delay_bins[ii]:, ii], self.data[:-delay_bins[ii], ii]])
            return ts

    def dmtime(self, dmsteps=256, target='CPU'):
        """
        Generates DM-time array of the candidate by dedispersing at adjacent DM values. Saves the data in `self.dmt`.

        Note:

            Our method rolls the data around while dedispersing it.

        Args:

            dmsteps (int) : Number of DMs to dedisperse at.

            target (str): 'CPU' to run the code on the CPU or 'GPU' to run it on a GPU.

        """
        if target == 'CPU':
            range_dm = self.dm
            dm_list = self.dm + np.linspace(-range_dm, range_dm, dmsteps)
            self.dmt = np.zeros((dmsteps, self.data.shape[0]), dtype=np.float32)
            for ii, dm in enumerate(dm_list):
                self.dmt[ii, :] = self.dedispersets(dms=dm)
        elif target == 'GPU':
            gpu_dmt(self, device=self.device)
        return self

    def get_snr(self, time_series=None):
        """
        Calculates the SNR of the candidate

        Args:

            time_series: time series array to calculate the SNR of

        Returns:

            float: SNR
        """
        if time_series is None and self.dedispersed is None:
            return None
        if time_series is None:
            x = self.dedispersed.mean(1)
        else:
            x = time_series
        argmax = np.argmax(x)
        mask = np.ones(len(x), dtype=np.bool)
        mask[argmax - self.width // 2:argmax + self.width // 2] = 0
        x -= x[mask].mean()
        std = np.std(x[mask])
        return x.max() / std

    def optimize_dm(self):
        """
        Calculate more precise value of the DM by interpolating between DM values to maximise the SNR

        Note:

            This function has not been fully tested.

        Returns:

            optimnised DM, optimised SNR
        """
        if self.data is None:
            return None

        def dm2snr(dm):
            time_series = self.dedispersets(dm)
            return -self.get_snr(time_series)

        try:
            out = golden(dm2snr, full_output=True, brack=(-self.dm / 2, self.dm, 2 * self.dm), tol=1e-3)
        except (ValueError, TypeError):
            out = golden(dm2snr, full_output=True, tol=1e-3)
        self.dm_opt = out[0]
        self.snr_opt = -out[1]
        return out[0], -out[1]

    def decimate(self, key, decimate_factor, axis, pad=False, **kwargs):
        """
        Decimate FT or DMT data.

        Todo:

            * Update candidate parameters as per decimation factor

        Args:

            key (str): Keywords to chose which data to decimate ('dmt' or 'ft')

            decimate_factor (int): Number of samples to average

            axis (int): Axis to decimate along

            pad (bool): Optional argument if padding is to be done

            **kwargs: kwargs for numpy.pad
        """
        if key == 'dmt':
            logger.debug(
                f'Decimating dmt along axis {axis}, with factor {decimate_factor},  pre-decimation shape: {self.dmt.shape}')
            self.dmt = _decimate(self.dmt, decimate_factor, axis, pad, **kwargs)
            logger.debug(f'Decimated dmt along axis {axis}, post-decimation shape: {self.dmt.shape}')
        elif key == 'ft':
            logger.debug(
                f'Decimating ft along axis {axis}, with factor {decimate_factor}, pre-decimation shape: {self.dedispersed.shape}')
            self.dedispersed = _decimate(self.dedispersed, decimate_factor, axis, pad, **kwargs)
            logger.debug(f'Decimated ft along axis {axis}, post-decimation shape: {self.dedispersed.shape}')
        else:
            raise AttributeError('Key can either be "dmt": DM-Time or "ft": Frequency-Time')
        return self

    def resize(self, key, size, axis, **kwargs):
        """
        Resize FT or DMT data

        Todo:

            * Update candidate parameters as per final size

        Args:

            key (str): Keywords to chose which data to resize ('dmt' or 'ft')

            size: Final size of the data array required

            axis (int) : Axis to resize alone

            **kwargs: Arguments for skimage.transform resize function

        """
        if key == 'dmt':
            self.dmt = _resize(self.dmt, size, axis, **kwargs)
        elif key == 'ft':
            self.dedispersed = _resize(self.dedispersed, size, axis, **kwargs)
        else:
            raise AttributeError('Key can either be "dmt": DM-Time or "ft": Frequency-Time')
        return self
