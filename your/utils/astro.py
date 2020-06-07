import numpy as np

ARCSECTORAD = float('4.8481368110953599358991410235794797595635330237270e-6')
RADTODEG = float('57.295779513082320876798154814105170332405472466564')


def dec2deg(src_dej):
    """
    Convert the SIGPROC-style DDMMSS.SSSS declination to degrees

    Args:

        src_dej (float): Source dec

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
    Convert the SIGPROC-style HHMMSS.SSSS right ascension to degrees

    Args:

        src_raj (float): Source RA

    """
    return 15.0 * dec2deg(src_raj)
