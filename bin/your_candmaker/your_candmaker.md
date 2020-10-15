
your_candmaker.py
=================

# Description


Your candmaker! Make h5 candidates from the candidate csv files
# Usage:


```bash
usage: your_candmaker.py [-h] [-v] [-fs FREQUENCY_SIZE] [-g GPU_ID [GPU_ID ...]] [-ts TIME_SIZE] -c CAND_PARAM_FILE [-n NPROC] [-o FOUT] [-opt] [--no_log_file] [--show_logs]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`||Be verbose|
|`-fs`|`--frequency_size`|`256`|Frequency size after rebinning|
|`-g`|`--gpu_id`|`[-1]`|GPU ID (use -1 for CPU). To use multiple GPUs (say with id 2 and 3 use -g 2 3|
|`-ts`|`--time_size`|`256`|Time length after rebinning|
|`-c`|`--cand_param_file`|`None`|csv file with candidate parameters|
|`-n`|`--nproc`|`2`|number of processors to use in parallel (default: 2)|
|`-o`|`--fout`|`.`|Output file directory for candidate h5|
|`-opt`|`--opt_dm`||Optimise DM|
||`--no_log_file`||Do not write a log file|
||`--show_logs`||Display logs on screen|
