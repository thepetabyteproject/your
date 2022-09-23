#!/usr/bin/env python3

import argparse
import json
import logging
import os
import textwrap
from datetime import datetime
from multiprocessing import Process

import numpy as np
from rich.logging import RichHandler

from your import Your
from your.utils.heimdall import HeimdallManager
from your.utils.misc import MyEncoder, YourArgparseFormatter
from your.writer import Writer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_heimdall.py",
        description="Your Heimdall Fetch FRB",
        formatter_class=YourArgparseFormatter,
        epilog=textwrap.dedent(
            """\
        `your_heimdall.py` runs Heimdall on Dada buffers for given file(s). Here are some additional notes for this script.
         - To use data present in multiple contiguous PSRFITS format files, just use `-f *.fits`.
         - Use the RFI mitigation algorithms provided in `your` by adding `-flag_rfi` to the command.
         - Do sub-banded search with `--channel_start` and `--channel_end` to specify the channel range to use.
         - Give a channel mask as a text file using `--mask`.
         - All the relevant Heimdall inputs can be set using various command line arguments.
         """
        ),
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="count", default=0)
    parser.add_argument("-f", "--files", help="filterbank or psrfits", nargs="+")
    parser.add_argument(
        "-dm",
        "--dm",
        help="DM (eg -dm 10 1000)",
        type=float,
        nargs=2,
        default=[10, 1000],
    )
    parser.add_argument(
        "-g",
        "--gpu_id",
        help="GPU ID to run heimdall on",
        type=int,
        required=False,
        default=0,
    )
    parser.add_argument(
        "-flag_rfi",
        "--flag_rfi",
        help="Use your to flag RFI",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-sk_sigma",
        "--spectral_kurtosis_sigma",
        help="Sigma for spectral kurtosis based RFI mitigation, only applied if -flag_rfi is used.",
        required=False,
        default=4,
        type=float,
    )
    parser.add_argument(
        "-sg_sigma",
        "--savgol_sigma",
        help="Sigma for Savgol filter for RFI mitigation, only applied if -flag_rfi is used.",
        default=4,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-sg_frequency",
        "--savgol_frequency_window",
        help="Filter window for savgol filter (in MHz), only applied if -flag_rfi is used.",
        default=15,
        required=False,
        type=float,
    )
    parser.add_argument(
        "-dm_tol",
        "--dm_tol",
        help="SNR loss tolerance between DM trials",
        required=False,
        type=float,
        default=1.25,
    )
    parser.add_argument(
        "-rfi_no_narrow",
        "--rfi_no_narrow",
        help="disable narrow band RFI excision",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-rfi_no_broad",
        "--rfi_no_broad",
        help="disable 0-DM RFI excision",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-mask",
        "--mask",
        help="File containing channel numbers to flag",
        required=False,
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output dir for heimdall candidates",
        type=str,
        required=False,
        default=None,
    )
    parser.add_argument(
        "-fs",
        "--channel_start",
        help="Start channel for sub band search",
        type=int,
        required=False,
        default=0,
    )
    parser.add_argument(
        "-fe",
        "--channel_end",
        help="End channel for sub band search",
        type=int,
        required=False,
        default=-1,
    )
    parser.add_argument(
        "-no_scrunching",
        "--no_scrunching",
        help="Disable adaptive scrunching in heimdall",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--no_progress",
        help="Do not show the tqdm bar",
        action="store_false",
    )
    parser.add_argument(
        "--no_log_file", help="Do not write a log file", action="store_true"
    )
    values = parser.parse_args()

    if values.output_dir is None:
        values.output_dir = "{0}/{1}".format(
            os.getcwd(), (".").join(os.path.basename(values.files[0]).split(".")[:-1])
        )
        os.makedirs(values.output_dir, exist_ok=True)

    logging_format = (
        "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
    )

    log_filename = (
        values.output_dir
        + "/"
        + datetime.utcnow().strftime("your_heimdall_%Y_%m_%d_%H_%M_%S_%f.log")
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
        logging.info("%s: %r", arg, value)

    your_object = Your(file=values.files)
    max_delay = your_object.dispersion_delay(dms=np.max(values.dm))
    dispersion_delay_samples = np.ceil(max_delay / your_object.your_header.tsamp)
    logging.info(f"Max Dispersion delay = {max_delay} s")
    logging.info(f"Max Dispersion delay = {dispersion_delay_samples} samples")

    if your_object.your_header.nspectra < 2 ** 18:
        nsamps_gulp = your_object.your_header.nspectra
    else:
        nsamps_gulp = int(
            np.max([(2 ** np.ceil(np.log2(dispersion_delay_samples))), 2 ** 18])
        )

    if values.channel_end > 0:
        c_max = values.channel_end
    else:
        c_max = None

    your_dada_writer = Writer(
        your_object=your_object,
        progress=~values.no_progress,
        c_min=values.channel_start,
        c_max=c_max,
        highest_frequency_first=True,
        savgol_sigma=values.savgol_sigma,
        spectral_kurtosis_sigma=values.spectral_kurtosis_sigma,
        savgol_frequency_window=values.savgol_frequency_window,
        flag_rfi=values.flag_rfi,
    )
    your_dada_writer.setup_dada()  # need to run the set up inorder to get the dada key

    if values.mask:
        logging.info(f"Reading RFI mask from {values.mask}")
        mask = np.loadtxt(values.mask)
        if len(mask.shape) == 1:
            bad_chans = list(mask)
        else:
            logging.warning(
                "RFI mask not understood, can only be 1D. Not using RFI flagging."
            )
            bad_chans = None
    else:
        logging.info("No RFI flagging done.")
        bad_chans = None

    if values.verbose <= 1:
        heimdall_verbosity = "v"
    elif values.verbose == 2:
        heimdall_verbosity = "V"
    elif values.verbose == 3:
        heimdall_verbosity = "g"
    else:
        heimdall_verbosity = "G"

    HM = HeimdallManager(
        dm=values.dm,
        dada_key=your_dada_writer.dada_key,
        boxcar_max=int(50e-3 / your_object.your_header.tsamp),
        verbosity=heimdall_verbosity,
        nsamps_gulp=nsamps_gulp,
        gpu_id=values.gpu_id,
        output_dir=values.output_dir,
        no_scrunching=values.no_scrunching,
        zap_chans=bad_chans,
        rfi_no_broad=values.rfi_no_broad,
        rfi_no_narrow=values.rfi_no_narrow,
        dm_tol=values.dm_tol,
    )

    with open(
        values.output_dir
        + "/"
        + your_object.your_header.basename
        + "_heimdall_inputs.json",
        "w",
    ) as fp:
        json.dump(HM.__dict__, fp, cls=MyEncoder, indent=4)

    dada_process = Process(name="To dada", target=your_dada_writer.to_dada)
    heimdall_process = Process(name="Heimdall", target=HM.run)

    dada_process.start()
    heimdall_process.start()

    try:
        heimdall_process.join()
        dada_process.join()
    except KeyboardInterrupt:
        heimdall_process.terminate()
        dada_process.terminate()

    your_dada_writer.DM.teardown()
    logging.info("Destroyed dada buffers")
