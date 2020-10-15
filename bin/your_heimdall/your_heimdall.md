
your_heimdall.py
================

# Description


Your Heimdall Fetch FRB
# Usage:


```bash
usage: your_heimdall.py [-h] [-v] [-f FILES [FILES ...]] [-dm DM DM] [-g GPU_ID] [-rfi_your] [-sk_sigma SPECTRAL_KURTOSIS_SIGMA] [-sg_sigma SAVGOL_SIGMA] [-sg_frequency SAVGOL_FREQUENCY_WINDOW]
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
|`-rfi_your`|`--rfi_your`||Use your to flag RFI|
|`-sk_sigma`|`--spectral_kurtosis_sigma`|`4`|Sigma for spectral kurtosis based RFI mitigation, only applied if -rfi_flag is used.|
|`-sg_sigma`|`--savgol_sigma`|`4`|Sigma for Savgol filter for RFI mitigation, only applied if -rfi_flag is used.|
|`-sg_frequency`|`--savgol_frequency_window`|`15`|Filter window for savgol filter (in MHz), only applied if -rfi_flag is used.|
|`-dm_tol`|`--dm_tol`|`1.25`|SNR loss tolerance between DM trials|
|`-rfi_no_narrow`|`--rfi_no_narrow`||disable narrow band RFI excision|
|`-rfi_no_broad`|`--rfi_no_broad`||disable 0-DM RFI excision|
|`-mask`|`--mask`|`None`|File containting channel numbers to kill|
|`-o`|`--output_dir`|`None`|Output dir for heimdall candidates|
|`-fs`|`--channel_start`|`0`|Start channel for sub band search|
|`-fe`|`--channel_end`|`-1`|End channel for sub band search|
||`--no_progress`||Do not show the tqdm bar|
||`--no_log_file`||Do not write a log file|
