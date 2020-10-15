#!/usr/bin/env python3

import argparse
import logging
from datetime import datetime

import numpy as np
from rich.logging import RichHandler

from your import Your
from your.utils.plotter import save_bandpass
from your.utils.rfi import savgol_filter

logging_format = "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_rfimask.py",
        description="Make Bad channel mask",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-f", "--files", help="filterbank or psrfits", nargs="+")
    parser.add_argument(
        "-sg",
        "--apply_savgol",
        help="Apply savgol filter to zap bad channels",
        action="store_true",
    )
    parser.add_argument(
        "-frequency_window",
        "--filter_window",
        help="Window size (MHz) for savgol filter",
        required=False,
        default=[15],
        type=float,
        nargs="+",
    )
    parser.add_argument(
        "-sigma",
        "--sigma",
        help="Sigma for the savgol filter",
        required=False,
        default=[6],
        type=float,
        nargs="+",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output dir for heimdall candidates",
        type=str,
        required=False,
        default=".",
    )
    parser.add_argument(
        "--no_log_file", help="Do not write a log file", action="store_true"
    )

    values = parser.parse_args()

    logging_format = (
        "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
    )

    log_filename = (
            values.output_dir
            + "/"
            + datetime.utcnow().strftime("your_rfimask_%Y_%m_%d_%H_%M_%S_%f.log")
    )
    if not values.no_log_file:
        if values.verbose:
            logging.basicConfig(
                filename=log_filename, level=logging.DEBUG, format=logging_format,
            )
        else:
            logging.basicConfig(
                filename=log_filename, level=logging.INFO, format=logging_format
            )
    else:
        if values.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format=logging_format,
                handlers=[RichHandler(rich_tracebacks=True)],
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=logging_format,
                handlers=[RichHandler(rich_tracebacks=True)],
            )

    your_object = Your(file=values.files)

    if values.apply_savgol:
        bandpass = your_object.bandpass(nspectra=8192)
        chan_nos = np.arange(0, bandpass.shape[0], dtype=np.int)
        for fw, sig in zip(values.filter_window, values.sigma):
            mask = savgol_filter(
                bandpass, your_object.your_header.foff, frequency_window=fw, sigma=sig
            )
            basename = (
                f"{values.output_dir}/{your_object.your_header.basename}_w{fw}_sig{sig}"
            )
            save_bandpass(
                your_object,
                bandpass,
                chan_nos=chan_nos,
                mask=mask,
                outdir=values.output_dir + "/",
                outname=f"{basename}_bandpass.png",
            )
            kill_mask_file = f"{basename}.bad_chans"
            with open(kill_mask_file, "w") as f:
                np.savetxt(f, chan_nos[mask], fmt="%d", delimiter=" ", newline=" ")

    else:
        raise ValueError(f"No RFI method selected.")
