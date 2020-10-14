#!/usr/bin/env python3

import argparse
import json
import logging
import os
from datetime import datetime
from multiprocessing import Process

import numpy as np
from rich.logging import RichHandler

from your import Your
from your.utils.heimdall import HeimdallManager
from your.utils.misc import MyEncoder
from your.writer import Writer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_heimdall.py",
        description="Your Heimdall Fetch FRB",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        "-rfi_your",
        "--rfi_your",
        help="Use your to flag RFI",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-sk_sigma",
        "--spectral_kurtosis_sigma",
        help="Sigma for spectral kurtosis based RFI mitigation, only applied if -rfi_flag is used.",
        required=False,
        default=4,
        type=float,
    )
    parser.add_argument(
        "-sg_sigma",
        "--savgol_sigma",
        help="Sigma for Savgol filter for RFI mitigation, only applied if -rfi_flag is used.",
        default=4,
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
        help="File containting channel numbers to kill",
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
        "--no_progress", help="Do not show the tqdm bar", action="store_false",
    )
    parser.add_argument(
        "--no_log_file", help="Do not write a log file", action="store_true"
    )
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = "{0}/{1}".format(
            os.getcwd(), (".").join(os.path.basename(args.files[0]).split(".")[:-1])
        )
        os.makedirs(args.output_dir, exist_ok=True)

    logging_format = (
        "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
    )

    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

    if args.no_log_file:
        log_filename = (
                args.output_dir
                + "/"
                + datetime.utcnow().strftime("your_heimdall_%Y_%m_%d_%H_%M_%S_%f.log")
        )

        fileHandler = logging.FileHandler(log_filename)
        fileHandler.setFormatter(logging.Formatter(logging_format))
        logging.getLogger().addHandler(fileHandler)
    else:
        rich_handler = RichHandler(rich_tracebacks=True)
        logging.getLogger().addHandler(rich_handler)

    logging.info("Input Arguments:-")
    for arg, value in sorted(vars(args).items()):
        logging.info("%s: %r", arg, value)

    your_object = Your(file=args.files)
    max_delay = your_object.dispersion_delay(dms=np.max(args.dm))
    dispersion_delay_samples = np.ceil(max_delay / your_object.your_header.tsamp)
    logging.info(f"Max Dispersion delay = {max_delay} s")
    logging.info(f"Max Dispersion delay = {dispersion_delay_samples} samples")

    if your_object.your_header.nspectra < 2 ** 18:
        nsamps_gulp = your_object.your_header.nspectra
    else:
        nsamps_gulp = int(
            np.max([(2 ** np.ceil(np.log2(dispersion_delay_samples))), 2 ** 18])
        )

    if args.channel_end > 0:
        c_max = args.channel_end
    else:
        c_max = None

    your_dada_writer = Writer(
        your_object=your_object,
        progress=~args.no_progress,
        c_min=args.channel_start,
        c_max=c_max,
        savgol_sigma=args.savgol_sigma,
        spectral_kurtosis_sigma=args.spectral_kurtosis_sigma,
        savgol_frequency_window=args.savgol_frequency_window,
        flag_rfi=args.rfi_your,
    )
    your_dada_writer.setup_dada()  # need to run the set up inorder to get the dada key

    if args.mask:
        logging.info(f"Reading RFI mask from {args.mask}")
        mask = np.loadtxt(args.mask)
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

    if args.verbose <= 1:
        heimdall_verbosity = "v"
    elif args.verbose == 2:
        heimdall_verbosity = "V"
    elif args.verbose == 3:
        heimdall_verbosity = "g"
    else:
        heimdall_verbosity = "G"

    HM = HeimdallManager(
        dm=args.dm,
        dada_key=your_dada_writer.dada_key,
        boxcar_max=int(50e-3 / your_object.your_header.tsamp),
        verbosity=heimdall_verbosity,
        nsamps_gulp=nsamps_gulp,
        gpu_id=args.gpu_id,
        output_dir=args.output_dir,
        zap_chans=bad_chans,
        rfi_no_broad=args.rfi_no_broad,
        rfi_no_narrow=args.rfi_no_narrow,
        dm_tol=args.dm_tol,
    )

    with open(
            args.output_dir
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
