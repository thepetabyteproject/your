
your_heimdall.py
================

# Description


Your Heimdall Fetch FRB
# Epilog



`your_heimdall.py` runs Heimdall on Dada buffers for given file(s). Here are some additional notes for this script.

 - To use data present in multiple contiguous PSRFITS format files, just use `-f *.fits`.

 - Use the RFI mitigation algorithms provided in `your` by adding `-flag_rfi` to the command.

 - Do sub-banded search with `--channel_start` and `--channel_end` to specify the channel range to use.

 - Give a channel mask as a text file using `--mask`.

 - All the relevant Heimdall inputs can be set using various command line arguments.


# Usage:


```bash
usage: your_heimdall.py [-h] [-v] [-f FILES [FILES ...]] [-dm DM DM] [-g GPU_ID] [-flag_rfi] [-sk_sigma SPECTRAL_KURTOSIS_SIGMA] [-sg_sigma SAVGOL_SIGMA] [-sg_frequency SAVGOL_FREQUENCY_WINDOW]
                        [-dm_tol DM_TOL] [-rfi_no_narrow] [-rfi_no_broad] [-mask MASK] [-o OUTPUT_DIR] [-fs CHANNEL_START] [-fe CHANNEL_END] [--no_progress] [--no_log_file]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`|`0`|Be verbose|
|`-f`|`--files`|`None`|filterbank or psrfits|
|`-dm`|`--dm`|`[10, 1000]`|DM (eg -dm 10 1000)|
|`-g`|`--gpu_id`|`0`|GPU ID to run heimdall on|
|`-flag_rfi`|`--flag_rfi`||Use your to flag RFI|
|`-sk_sigma`|`--spectral_kurtosis_sigma`|`4`|Sigma for spectral kurtosis based RFI mitigation, only applied if -flag_rfi is used.|
|`-sg_sigma`|`--savgol_sigma`|`4`|Sigma for Savgol filter for RFI mitigation, only applied if -flag_rfi is used.|
|`-sg_frequency`|`--savgol_frequency_window`|`15`|Filter window for savgol filter (in MHz), only applied if -flag_rfi is used.|
|`-dm_tol`|`--dm_tol`|`1.25`|SNR loss tolerance between DM trials|
|`-rfi_no_narrow`|`--rfi_no_narrow`||disable narrow band RFI excision|
|`-rfi_no_broad`|`--rfi_no_broad`||disable 0-DM RFI excision|
|`-mask`|`--mask`|`None`|File containing channel numbers to flag|
|`-o`|`--output_dir`|`None`|Output dir for heimdall candidates|
|`-fs`|`--channel_start`|`0`|Start channel for sub band search|
|`-fe`|`--channel_end`|`-1`|End channel for sub band search|
||`--no_progress`||Do not show the tqdm bar|
||`--no_log_file`||Do not write a log file|
