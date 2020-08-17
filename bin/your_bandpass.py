#!/usr/bin/env python3
"""
Generate bandpass of data
"""
import argparse

from your import Your
from your.utils.plotter import save_bandpass


def bandpass(f, time=0, nspectra=8192, outname=None):
    """
    Plots and saves the bandpass
    
    Args:
        f: File to read

        time: Time in seconds to read for bandpass

        nspectra: Number of spectra to read for bandpass
    """

    y = Your(f)
    if time > 0:
        ns = time // y.your_header.native_tsamp
    else:
        ns = nspectra
    bandpass = y.bandpass(nspectra=ns)
    save_bandpass(y, bandpass, chan_nos=None, mask=None, outdir=None, outname=outname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='your_bandpass.py',
                                     description="Generate bandpass of data",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files',
                        help='Fits or filterbank files to read.',
                        required=True, nargs='+')
    parser.add_argument('-n', '--nspectra',
                        help='Number of spectra to use for bandpass.',
                        required=False, type=int, default=8192)
    parser.add_argument('-t', '--time',
                        help='Time (s) to use for bandpass.',
                        required=False, type=float, default=0)
    parser.add_argument('-b', '--name',
                        help='Name of bandpass png', type=str,
                        required=False, default=None)
    values = parser.parse_args()

    bandpass(f=values.files, time=values.time, nspectra=values.nspectra, outname=values.name)
