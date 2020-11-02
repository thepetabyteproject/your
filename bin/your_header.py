#!/usr/bin/env python3
"""
Print your header
"""
import argparse
import logging

from rich.logging import RichHandler

from your import Your
from your.utils.misc import YourArgparseFormatter


def nice_print(dic):
    for key, item in dic.items():
        print(f"{key : >27}:\t{item}")


def read_header(f):
    y = Your(f)
    dic = vars(y.your_header)
    dic["tsamp"] = y.your_header.tsamp
    dic["nchans"] = y.your_header.nchans
    dic["channel_bandwidth"] = y.your_header.foff
    dic["nspectra"] = y.your_header.nspectra
    nice_print(dic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="your_header.py",
        description="Read header from psrfits/filterbank files and print the unified header",
        formatter_class=YourArgparseFormatter,
    )
    parser.add_argument(
        "-f",
        "--files",
        help="psrfits or filterbank files to read header.",
        required=True,
        nargs="+",
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    values = parser.parse_args()
    logging_format = (
        "%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s"
    )

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

    read_header(values.files)
