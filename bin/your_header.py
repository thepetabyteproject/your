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
        dic = vars(y.your_header)
        dic['tsamp'] = y.your_header.tsamp
        dic['nchans'] = y.your_header.nchans
        dic['foff'] = y.your_header.foff
        dic['nspectra'] = y.your_header.nspectra
        nice_print(dic)
    else:
        print(f"File: {f} does not exist!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Read header from fits/fil and print the your header",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files',
                        help='Fits or filterbank file to read header.',
                        required=True, type=str)
    values = parser.parse_args()
    read_header(values.files)
