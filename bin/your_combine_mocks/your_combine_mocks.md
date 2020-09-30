
your_combine_mocks.py
=====================

# Description


Combine two bands from mock spectrometer to a filterbank file.
# Usage:


```bash
usage: your_combine_mocks.py [-h] [-v] [-f1 FIRST_BAND] [-f2 SECOND_BAND] [-s NSTART] [-n NSAMP] [-o OUTDIR] [-fil FIL_NAME] [-a ALL_FILES]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`||Be verbose|
|`-f1`|`--first_band`|`None`|Path of files containing one band|
|`-f2`|`--second_band`|`None`|Path of files containing second band|
|`-s`|`--nstart`|`0`|Start sample number|
|`-n`|`--nsamp`|`-1`|Number of samples to read (-1: whole file)|
|`-o`|`--outdir`|`.`|Output directory for Filterbank file|
|`-fil`|`--fil_name`|`None`|Output name of the Filterbank file|
|`-a`|`--all_files`|`None`|Process all files in the given directory|
