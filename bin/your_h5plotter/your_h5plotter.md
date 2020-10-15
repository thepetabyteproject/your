
your_h5plotter.py
=================

# Description


Plot candidate h5 files
# Usage:


```bash
usage: your_h5plotter.py [-h] [-v] [-f FILES [FILES ...]] [-c RESULTS_CSV] [--publish] [--no_detrend_ft] [--no_save] [-o OUT_DIR] [-mad [MAD_FILTER]] [-n NPROC] [--no_progress] [--no_log_file]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`||Be verbose|
|`-f`|`--files`|`None`|h5 files to be plotted|
|`-c`|`--results_csv`|`None`|Plot positives in results.csv|
||`--publish`||Make publication quality plots|
||`--no_detrend_ft`||Detrend the frequency-time plot|
||`--no_save`||Do not save the plot|
|`-o`|`--out_dir`|`None`|Directory to save pngs (default: h5 dir)|
|`-mad`|`--mad_filter`||Median Absolute Deviation spectal clipper, default 3 sigma|
|`-n`|`--nproc`|`4`|Number of processors to use in parallel (default: 4)|
||`--no_progress`||Do not show the tqdm bar|
||`--no_log_file`||Do not write a log file|
