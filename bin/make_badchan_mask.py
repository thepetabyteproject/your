#!/usr/bin/env python3

import argparse
import logging
import numpy as np

from your import Your
from your.utils import get_sg_window, mask_finder, save_bandpass

logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make Bad channel mask",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files', help='filterbank or psrfits', nargs='+')
    parser.add_argument('-sg', '--apply_savgol', help='Apply savgol filter to zap bad channels', action='store_true')
    parser.add_argument('-fw', '--filter_window', help='Window size (MHz) for savgol filter', required=False, 
                        default=15, type=float)
    parser.add_argument('-sig', '--sigma', help='Sigma for the savgol filter', required=False, default=6, type=float)
    parser.add_argument('-o', '--output_dir', help='Output dir for heimdall candidates', type=str, required=False,
                        default='.')    

    args = parser.parse_args()
    
    your_object = Your(file=args.files)
    
    if args.apply_savgol:
        if your_object.nspectra > 8192:
            ns = 8192
        else:
            ns = your_object.nspectra
        bandpass = your_object.bandpass(nspectra=ns)
        window = get_sg_window(your_object.your_header.foff, args.filter_window)
        mask = mask_finder(bandpass, window, args.sigma)
        chan_nos=np.arange(0,bandpass.shape[0], dtype=np.int)
        bad_chans=list(chan_nos[mask])
    else:
        raise ValueError(f"No RFI method selected.")

    basename = f'{args.output_dir}/{your_object.your_header.basename}_w{args.filter_window}_sig{args.sigma}'
    save_bandpass(your_object, bandpass, chan_nos=chan_nos, mask=mask, 
                  outdir=args.output_dir + '/', outname=f'{basename}_bandpass.png')
    kill_mask_file = f'{basename}.bad_chans'
    with open(kill_mask_file,'w') as f:
        np.savetxt(f,chan_nos[mask],fmt='%d',delimiter=' ', newline=' ')