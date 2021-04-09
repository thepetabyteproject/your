#!/usr/bin/env python3
"""
Converts files in PSRFITS or Filterbank format
to PSRFITS ot Filterbank format.

"""

import argparse
import logging
from datetime import datetime

from rich.logging import RichHandler

from your import Your
from your.utils.misc import YourArgparseFormatter
from your.writer import Writer

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_writer.py",
        description="Convert/Write files from any format to a single file in any format.",
        formatter_class=YourArgparseFormatter,
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument(
        "-f",
        "--files",
        help="Paths of input files to be converted to an output format.",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "-t", "--type", help="Output file type (fits or fil)", type=str, required=True
    )
    parser.add_argument(
        "-c",
        "--chans",
        help="Required channels (eg -c 0 4096)",
        required=False,
        type=int,
        nargs=2,
        default=[None, None],
    )
    parser.add_argument(
        "-nstart",
        "--nstart",
        help="Start spectra number",
        required=False,
        type=int,
        default=0,
    )
    parser.add_argument(
        "-nsamp",
        "--nsamp",
        help="Number of spectra to convert",
        required=False,
        type=int,
        default=None,
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        help="Output directory for the file",
        default="./",
        required=False,
    )
    parser.add_argument(
        "-name",
        "--out_name",
        type=str,
        help="Output name of the file (do not add the file extension)",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--no_progress",
        help="Do not show the progress bar",
        action="store_false",
    )
    parser.add_argument(
        "-r",
        "--flag_rfi",
        help="Turn on RFI flagging",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-sksig",
        "--spectral_kurtosis_sigma",
        help="Sigma for spectral kurtosis filter",
        type=float,
        default=4,
        required=False,
    )
    parser.add_argument(
        "-sgsig",
        "--savgol_sigma",
        help="Sigma for savgol filter",
        type=float,
        default=4,
        required=False,
    )
    parser.add_argument(
        "-sgfw",
        "--savgol_frequency_window",
        help="Filter window for savgol filter (MHz)",
        type=float,
        default=15,
        required=False,
    )
    parser.add_argument(
        "-zero_dm_subt",
        "--zero_dm_subt",
        help="Enable 0 DM subtraction",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-td",
        "--time_decimation_factor",
        help="Time Decimation Factor",
        required=False,
        type=int,
        default=1,
    )
    parser.add_argument(
        "-fd",
        "--frequency_decimation_factor",
        help="Frequency Decimation Factor",
        required=False,
        type=int,
        default=1,
    )
    parser.add_argument(
        "-g",
        "--gulp_size",
        help="Gulp size in samples",
        required=False,
        type=int,
        default=None,
    )
    parser.add_argument(
        "-npol",
        "--num_polarisation",
        help="Number of output polarisations",
        required=False,
        type=int,
        default=1,
    )
    parser.add_argument(
        "-npsub",
        "--nspectra_per_subint",
        help="Number of spectra per subint (used only for writing psrfits)",
        required=False,
        type=int,
        default=4032,
    )
    parser.add_argument(
        "--replacement_policy",
        type=str,
        choices=["mean", "median", "zero"],
        required=False,
        default="mean",
        help="Replace the RFI flagged values with either mean, median or zero.",
    )
    parser.add_argument(
        "--no_log_file", help="Do not write a log file", action="store_true"
    )
    values = parser.parse_args()

    logging_format = (
        "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
    )
    log_filename = (
        values.outdir
        + "/"
        + datetime.utcnow().strftime("your_writer_%Y_%m_%d_%H_%M_%S_%f.log")
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

    logging.info("Input Arguments:-")
    for arg, value in sorted(vars(values).items()):
        logging.info("Argument %s: %r", arg, value)
    y = Your(values.files)
    w = Writer(
        y,
        c_min=values.chans[0],
        c_max=values.chans[1],
        nstart=values.nstart,
        nsamp=values.nsamp,
        outdir=values.outdir,
        outname=values.out_name,
        progress=values.no_progress,
        flag_rfi=values.flag_rfi,
        spectral_kurtosis_sigma=values.spectral_kurtosis_sigma,
        savgol_frequency_window=values.savgol_frequency_window,
        savgol_sigma=values.savgol_sigma,
        gulp=values.gulp_size,
        zero_dm_subt=values.zero_dm_subt,
        time_decimation_factor=values.time_decimation_factor,
        frequency_decimation_factor=values.frequency_decimation_factor,
        replacement_policy=values.replacement_policy,
        npoln=values.num_polarisation,
    )

    if values.type == "fits":
        w.to_fits(npsub=values.npsub)
    elif values.type == "fil":
        w.to_fil()
    else:
        raise ValueError("Type can either be 'fits' or 'fil'")
