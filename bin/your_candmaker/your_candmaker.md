
your_candmaker.py
=================

# Description


Your candmaker! Make h5 candidates from the candidate csv files
# Epilog



`your_candmaker.py` can be used to make candidate cutout files. Some additional notes for this script: 

- These files are generated in HDF file format. 

- The output candidates have been preprocessed and consists of Dedispersed Frequency-Time and DM-Time information of the candidate. 

- The input should be a csv file containing the parameters of the candidates. The input csv file should contain the following fields: 

        - file: Filterbank or PSRFITs file containing the data. In case of multiple files, this should contain the name of first file. 

        - snr: Signal to Noise of the candidate.

        - width: Width of candidate as log2(number of samples). 

        - dm: DM of candidate

        - label: Label of candidate (can be just set to 0, if not known)

        - stime: Start time (seconds) of the candidate.

        - chan_mask_path: Path of the channel mask file. 

        - num_files: Number of files. 


# Usage:


```bash
usage: your_candmaker.py [-h] [-v] [-fs FREQUENCY_SIZE]
                         [-g GPU_ID [GPU_ID ...]] [-ts TIME_SIZE] -c
                         CAND_PARAM_FILE [-n NPROC] [-o FOUT] [-opt]
                         [--no_log_file]

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
