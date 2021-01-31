#!/usr/bin/env python3

import argparse
from datetime import datetime

from rich.logging import RichHandler

from your import Your
from your.utils.misc import YourArgparseFormatter
from your.utils.plotter import save_bandpass
from your.utils.rfi import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_rfimask.py",
        description="Make Bad channel mask",
        formatter_class=YourArgparseFormatter,
    )
    parser.add_argument("-f", "--files", help="filterbank or psrfits", nargs="+")
    parser.add_argument(
        "-n",
        "--nspectra",
        help="Number of spectra to read and apply filters to",
        required=False,
        type=int,
        default=8192,
    )
    parser.add_argument(
        "-sk_sigma",
        "--spectral_kurtosis_sigma",
        help="Sigma for spectral kurtosis based RFI mitigation, if set to 0 this method will not be used.",
        required=False,
        default=0,
        type=float,
    )
    parser.add_argument(
        "-sg_sigma",
        "--savgol_sigma",
        help="Sigma for Savgol filter for RFI mitigation, if set to 0 this method will not be used.",
        default=0,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-sg_frequency",
        "--savgol_frequency_window",
        help="Filter window for savgol filter (in MHz), only applied if -rfi_flag is used.",
        default=15,
        required=False,
        type=float,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output dir for saving the mask",
        type=str,
        required=False,
        default=".",
    )
    parser.add_argument(
        "--no_log_file", help="Do not write a log file", action="store_true"
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")

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
                filename=log_filename,
                level=logging.DEBUG,
                format=logging_format,
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
    bandpass = your_object.bandpass(values.nspectra)

    mask = sk_sg_filter(
        data=your_object.get_data(0, values.nspectra),
        your_object=your_object,
        spectral_kurtosis_sigma=values.spectral_kurtosis_sigma,
        savgol_frequency_window=values.savgol_frequency_window,
        savgol_sigma=values.savgol_sigma,
    )

    basename = f"{values.output_dir}/{your_object.your_header.basename}_your_rfi_mask"
    chan_nos = np.array(range(your_object.your_header.nchans), dtype=int)
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
