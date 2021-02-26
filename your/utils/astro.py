import numpy as np

ARCSECTORAD = float("4.8481368110953599358991410235794797595635330237270e-6")
RADTODEG = float("57.295779513082320876798154814105170332405472466564")


def dec2deg(src_dej):
    """
    Convert the SIGPROC-style DDMMSS.SSSS declination to degrees

    Args:
        src_dej (float): Source dec
    """
    sign = 1.0
    if src_dej < 0:
        sign = -1.0
    xx = np.fabs(src_dej)
    dd = int(np.floor(xx / 10000.0))
    mm = int(np.floor((xx - dd * 10000.0) / 100.0))
    ss = xx - dd * 10000.0 - mm * 100.0
    return sign * ARCSECTORAD * (60.0 * (60.0 * dd + mm) + ss) * RADTODEG


def ra2deg(src_raj):
    """
    Convert the SIGPROC-style HHMMSS.SSSS right ascension to degrees

    Args:
        src_raj (float): Source RA
    """
    return 15.0 * dec2deg(src_raj)


def dedisperse(data, dm, tsamp, chan_freqs=[], delays=[]):
    """
    Dedisperse a chunk of data..

    Note:
        Our method rolls the data around while dedispersing it.

    Args:
        data: data to dedisperse
        dm (float): The DM to dedisperse the data at.
        chan_freqs (float): frequencies
        tsamp (float): sampling time in seconds
        delays (float): dispersion delays for each channel (in seconds)

    Returns:
        dedispersed (float): Dedispersed data
    """
    nf, nt = data.shape
    if np.any(delays):
        assert len(delays) == nf
    else:
        assert nf == len(chan_freqs)
        delays = calc_dispersion_delays(dm, chan_freqs)

    delay_bins = np.round(delays / tsamp).astype("int64")
    dedispersed = np.zeros(data.shape, dtype=np.float32)
    for ii in range(nf):
        dedispersed[ii, :] = np.concatenate(
            [
                data[ii, -delay_bins[ii] :],
                data[ii, : -delay_bins[ii]],
            ]
        )
    return dedispersed


def calc_dispersion_delays(dm, chan_freqs):
    """
    Calculates dispersion delays at an input DM and a frequency array.

    Args:
        dm (float): DM to calculate the delay
        chan_freqs (float): Frequencies

    Returns:
        delays (float): dispersion delays at each frequency channel (in seconds)
    """
    delays = 4148808.0 * dm * (1 / (chan_freqs[0]) ** 2 - 1 / (chan_freqs) ** 2) / 1000
    return delays
