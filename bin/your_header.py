#!/usr/bin/env python3
"""
Print your header
"""
import argparse
import logging

from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from your import Your
from your.utils.misc import YourArgparseFormatter


def nice_print(dic):
    """
    Prints out data files into in a nice to view way

    Inputs:
    dic --  dictionary containing data file meta data to be printed
    """
    for key, item in dic.items():
        print(f"{key}\t{item}")


def table_print(dic):
    """
    Prints out data using rich.Table

    Inputs:
    dic --  dictionary containing data file meta data to be printed
    """

    console = Console()
    table = Table(show_header=True, header_style="bold red", box=box.DOUBLE_EDGE)
    table.add_column("Parameter", justify="right")
    table.add_column("Value")
    for key, item in dic.items():
        table.add_row(key, f"{item}")
    console.print(table)


def read_header(f, no_table):
    """
    Makes your header for given files, hands header off to be nicely printed

    Inputs:
    --
    f -- files to create the your header

    no_table -- bool - if true, don't use rich.table
    """
    y = Your(f)
    dic = vars(y.your_header)
    dic["tsamp"] = y.your_header.tsamp
    dic["nchans"] = y.your_header.nchans
    dic["channel_bandwidth"] = y.your_header.foff
    dic["nspectra"] = y.your_header.nspectra
    if no_table:
        nice_print(dic)
    else:
        table_print(dic)


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
    parser.add_argument(
        "--no_table",
        help="Print plain text, don't use rich.table",
        action="store_true",
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

    read_header(values.files, values.no_table)
