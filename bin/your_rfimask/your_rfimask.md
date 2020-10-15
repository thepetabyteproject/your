
your_rfimask.py
===============

# Description


Make Bad channel mask
# Usage:


```bash
usage: your_rfimask.py [-h] [-f FILES [FILES ...]] [-sg] [-frequency_window FILTER_WINDOW [FILTER_WINDOW ...]] [-sigma SIGMA [SIGMA ...]] [-o OUTPUT_DIR] [--no_log_file]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-f`|`--files`|`None`|filterbank or psrfits|
|`-sg`|`--apply_savgol`||Apply savgol filter to zap bad channels|
|`-frequency_window`|`--filter_window`|`[15]`|Window size (MHz) for savgol filter|
|`-sigma`|`--sigma`|`[6]`|Sigma for the savgol filter|
|`-o`|`--output_dir`|`.`|Output dir for heimdall candidates|
||`--no_log_file`||Do not write a log file|
