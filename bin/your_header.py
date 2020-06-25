#!/usr/bin/env python3
"""
Print your header
"""
import argparse
import os.path
from your import Your

def nice_print(dic):
    for key, item in dic.items():
        print(f"{key : >27}:\t{item}")

def read_header(f):
    if os.path.isfile(f):
        y = Your(f)	
        nice_print(vars(y.your_header))
    else:
        print(f"File: {f} does not exist!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Read header from file and print the your header",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files',
                        help='Paths of PSRFITS files to be converted to a single file in Filterbank format. Surround '
                             'with quotes, and either use wildcards or separate with spaces',
                        required=True, type=str)
    values = parser.parse_args()
    read_header(values.files)
