
your_heimdall.py
================

# Description


Your Heimdall Fetch FRB
# Usage:


```bash
usage: your_heimdall.py [-h] [-v] [-p PROBABILITY] [-f FILES [FILES ...]] [-dm DM DM] [-g GPU_ID] [-sg] [-frequency_window FILTER_WINDOW] [-sigma SIGMA] [-m MASK] [-dm_tol DM_TOL] [-rfi_no_narrow] [-rfi_no_broad] [-o OUTPUT_DIR] [--no_progress]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`||Be verbose|
|`-p`|`--probability`|`0.5`|Detection threshold|
|`-f`|`--files`|`None`|filterbank or psrfits|
|`-dm`|`--dm`|`[10, 1000]`|DM (eg -dm 10 1000)|
|`-g`|`--gpu_id`|`0`|GPU ID to run heimdall on|
|`-sg`|`--apply_savgol`||Apply savgol filter to zap bad channels|
|`-frequency_window`|`--filter_window`|`15`|Window size (MHz) for savgol filter|
|`-sigma`|`--sigma`|`6`|Sigma for the savgol filter|
|`-m`|`--mask`|`None`|Input RFI mask (could be 1-D bad channel mask or 2-D FT mask)|
|`-dm_tol`|`--dm_tol`|`1.25`|SNR loss tolerance between DM trials|
|`-rfi_no_narrow`|`--rfi_no_narrow`||disable narrow band RFI excision|
|`-rfi_no_broad`|`--rfi_no_broad`||disable 0-DM RFI excision|
|`-o`|`--output_dir`|`None`|Output dir for heimdall candidates|
||`--no_progress`|`None`|Do not show the tqdm bar|
