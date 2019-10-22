#!/usr/bin/env python3

import h5py
from scipy.optimize import golden

from your import Your
from your.utils import *

logger = logging.getLogger(__name__)

class Candidate(Your):
    def __init__(self, fp=None, copy_hdr=None, dm=None, tcand=0, width=0, label=-1, snr=0, min_samp=256, device=0,
                 kill_mask=None):
        """

        :param fp: Filepath of the filterbank
        :param copy_hdr: Custom header to the filterbank file
        :param dm: DM of the candidate
        :param tcand: Time of the candidate in filterbank file (seconds)
        :param width: Width of the candidate (number of samples)
        :param label: Label of the candidate (1: for FRB, 0: for RFI)
        :param snr: SNR of the candidate
        :param min_samp: Minimum number of time samples to read
        :param device: If using GPUs, device is the GPU id
        :param kill_mask: Boolean mask of channels to kill
        """
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
        Generates an h5 file of the candidate object
        :param out_dir: Output directory to save the h5 file
        :param fnout: Output name of the candidate file
        :return:
        """
        cand_id = self.id
        if fnout is None:
            fnout = cand_id + '.h5'
        if out_dir is not None:
            fnout = out_dir + fnout
        with h5py.File(fnout, 'w') as f:
            f.attrs['cand_id'] = cand_id
            f.attrs['tcand'] = self.tcand
            f.attrs['dm'] = self.dm
            f.attrs['dm_opt'] = self.dm_opt
            f.attrs['snr'] = self.snr
            f.attrs['snr_opt'] = self.snr_opt
            f.attrs['width'] = self.width
            f.attrs['label'] = self.label

            # Copy over header information as attributes
            for key in list(self._type.keys()):
                if getattr(self, key) is not None:
                    f.attrs[key] = getattr(self, key)
                else:
                    f.attrs[key] = b'None'

            freq_time_dset = f.create_dataset('data_freq_time', data=self.dedispersed, dtype=self.dedispersed.dtype,
                                              compression="lzf")
            freq_time_dset.dims[0].label = b"time"
            freq_time_dset.dims[1].label = b"frequency"

            if self.dmt is not None:
                dm_time_dset = f.create_dataset('data_dm_time', data=self.dmt, dtype=self.dmt.dtype, compression="lzf")
                dm_time_dset.dims[0].label = b"dm"
                dm_time_dset.dims[1].label = b"time"
        return fnout

    def dispersion_delay(self, dms=None):
        """
        Calculates the dispersion delay at a specified DM
        :param dms: DM value to get dispersion delay
        :return:
        """
        if dms is None:
            dms = self.dm
        if dms is None:
            return None
        else:
            return 4148808.0 * dms * (1 / np.min(self.chan_freqs) ** 2 - 1 / np.max(self.chan_freqs) ** 2) / 1000

    def get_chunk(self, tstart=None, tstop=None):
        """
        Read the data around the candidate from the filterbank
        :param tstart: Start time in the fiterbank, to read from
        :param tstop: End time in the filterbank, to read till
        :return:
        """
        if tstart is None:
            tstart = self.tcand - self.dispersion_delay() - self.width * self.tsamp
            if tstart < 0:
                tstart = 0
        if tstop is None:
            tstop = self.tcand + self.dispersion_delay() + self.width * self.tsamp
            if tstop > self.tend:
                tstop = self.tend
        nstart = int(tstart / self.tsamp)
        nsamp = int((tstop - tstart) / self.tsamp)
        if self.width < 2:
            nchunk = self.min_samp
        else:
            nchunk = self.width * self.min_samp // 2
        if nsamp < nchunk:
            # if number of time samples less than nchunk, make it min_samp.
            nstart -= (nchunk - nsamp) // 2
            nsamp = nchunk
        if nstart < 0:
            self.data = self.get_data(nstart=0, nsamp=nsamp + nstart)[:, 0, :]
            logger.debug('median padding data as nstart < 0')
            self.data = pad_along_axis(self.data, nsamp, loc='start', axis=0, mode='median')
        elif nstart + nsamp > self.nspectra:
            self.data = self.get_data(nstart=nstart, nsamp=self.nspectra - nstart)[:, 0, :]
            logger.debug('median padding data as nstop > nspectra')
            self.data = pad_along_axis(self.data, nsamp, loc='end', axis=0, mode='median')
        else:
            self.data = self.get_data(nstart=nstart, nsamp=nsamp)[:, 0, :]

        if self.kill_mask is not None:
            assert len(self.kill_mask) == self.data.shape[1]
            data_copy = self.data.copy()
            data_copy[:, self.kill_mask] = 0
            self.data = data_copy
            del data_copy
        return self

    def dedisperse(self, dms=None, target='CPU'):
        """
        Dedisperse Frequency time data at a specified DM
        :param dms: DM to dedisperse at
        :return:
        """
        if dms is None:
            dms = self.dm
        if self.data is not None:
            if target == 'CPU':
                nt, nf = self.data.shape
                assert nf == len(self.chan_freqs)
                delay_time = 4148808.0 * dms * (1 / (self.chan_freqs[0]) ** 2 - 1 / (self.chan_freqs) ** 2) / 1000
                delay_bins = np.round(delay_time / self.tsamp).astype('int64')
                self.dedispersed = np.zeros(self.data.shape, dtype=np.float32)
                for ii in range(nf):
                    self.dedispersed[:, ii] = np.concatenate(
                        [self.data[-delay_bins[ii]:, ii], self.data[:-delay_bins[ii], ii]])
            elif target == 'GPU':
                from gpu_utils import gpu_dedisperse
                gpu_dedisperse(self, device=self.device)
        else:
            self.dedispersed = None
        return self

    def dedispersets(self, dms=None):
        """
        Dedisperse Frequency time data at a specified DM and return a time series
        :param dms: DM to dedisperse at
        :return: time series
        """
        if dms is None:
            dms = self.dm
        if self.data is not None:
            nt, nf = self.data.shape
            assert nf == len(self.chan_freqs)
            delay_time = 4148808.0 * dms * (1 / (self.chan_freqs[0]) ** 2 - 1 / (self.chan_freqs) ** 2) / 1000
            delay_bins = np.round(delay_time / self.tsamp).astype('int64')
            ts = np.zeros(nt, dtype=np.float32)
            for ii in range(nf):
                ts += np.concatenate([self.data[-delay_bins[ii]:, ii], self.data[:-delay_bins[ii], ii]])
            return ts

    def dmtime(self, dmsteps=256, target='CPU'):
        """
        Generates DM-time array of the candidate by dedispersing at adjacent DM values
        dmsteps: Number of DMs to dedisperse at
        :return:
        """
        if target == 'CPU':
            range_dm = self.dm
            dm_list = self.dm + np.linspace(-range_dm, range_dm, dmsteps)
            self.dmt = np.zeros((dmsteps, self.data.shape[0]), dtype=np.float32)
            for ii, dm in enumerate(dm_list):
                self.dmt[ii, :] = self.dedispersets(dms=dm)
        elif target == 'GPU':
            from gpu_utils import gpu_dmt
            gpu_dmt(self, device=self.device)
        return self

    def get_snr(self, time_series=None):
        """
        Calculates the SNR of the candidate
        :param time_series: time series array to calculate the SNR of
        :return:
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
        This function has not been fully tested.
        :return: optimnised DM, optimised SNR
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
        TODO: Update candidate parameters as per decimation factor
        :param key: Keywords to chose which data to decimate
        :param decimate_factor: Number of samples to average
        :param axis: Axis to decimate along
        :param pad: Optional argument if padding is to be done
        :args: arguments for numpy pad
        :return:
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
        TODO: Update candidate parameters as per final size
        :param key: Keywords to chose which data to decimate
        :param size: Final size of the data array required
        :param axis: Axis to resize alone
        :param args: Arguments for skimage.transform resize function
        :return:
        """
        if key == 'dmt':
            self.dmt = _resize(self.dmt, size, axis, **kwargs)
        elif key == 'ft':
            self.dedispersed = _resize(self.dedispersed, size, axis, **kwargs)
        else:
            raise AttributeError('Key can either be "dmt": DM-Time or "ft": Frequency-Time')
        return self
