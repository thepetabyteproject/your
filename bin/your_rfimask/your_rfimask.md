
your_rfimask.py
===============

# Description


Make Bad channel mask
# Usage:


```bash
usage: your_rfimask.py [-h] [-f FILES [FILES ...]] [-n NSPECTRA]
                       [-sk_sigma SPECTRAL_KURTOSIS_SIGMA]
                       [-sg_sigma SAVGOL_SIGMA]
                       [-sg_frequency SAVGOL_FREQUENCY_WINDOW] [-o OUTPUT_DIR]
                       [--no_log_file] [-v]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-f`|`--files`|`None`|filterbank or psrfits|
|`-n`|`--nspectra`|`8192`|Number of spectra to read and apply filters to|
|`-sk_sigma`|`--spectral_kurtosis_sigma`|`0`|Sigma for spectral kurtosis based RFI mitigation, if set to 0 this method will not be used.|
|`-sg_sigma`|`--savgol_sigma`|`0`|Sigma for Savgol filter for RFI mitigation, if set to 0 this method will not be used.|
|`-sg_frequency`|`--savgol_frequency_window`|`15`|Filter window for savgol filter (in MHz), only applied if -rfi_flag is used.|
|`-o`|`--output_dir`|`.`|Output dir for saving the mask|
||`--no_log_file`||Do not write a log file|
|`-v`|`--verbose`||Be verbose|
