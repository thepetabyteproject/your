
your_writer.py
==============

# Description


Convert/Write files from any format to a single file in any format.
# Usage:


```bash
usage: your_writer.py [-h] [-v] -f FILES [FILES ...] -t TYPE [-c CHANS CHANS]
                      [-nstart NSTART] [-nsamp NSAMP] [-o OUTDIR]
                      [-name OUT_NAME] [--no_progress] [-r]
                      [-sksig SPECTRAL_KURTOSIS_SIGMA] [-sgsig SAVGOL_SIGMA]
                      [-sgfw SAVGOL_FREQUENCY_WINDOW] [-zero_dm_subt]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-v`|`--verbose`||Be verbose|
|`-f`|`--files`|`None`|Paths of input files to be converted to an output format.|
|`-t`|`--type`|`None`|Output file type (fits or fil)|
|`-c`|`--chans`|`[None, None]`|Required channels (eg -c 0 4096)|
|`-nstart`|`--nstart`|`None`|Start spectra number|
|`-nsamp`|`--nsamp`|`None`|Number of spectra to convert|
|`-o`|`--outdir`|`.`|Output directory for the file|
|`-name`|`--out_name`|`None`|Output name of the file|
||`--no_progress`|`None`|Do not show the tqdm bar|
|`-r`|`--flag_rfi`||Turn on RFI flagging|
|`-sksig`|`--spectral_kurtosis_sigma`|`4`|Sigma for spectral kurtosis filter|
|`-sgsig`|`--savgol_sigma`|`4`|Sigma for savgol filter|
|`-sgfw`|`--savgol_frequency_window`|`15`|Filter window for savgol filter (MHz)|
|`-zero_dm_subt`|`--zero_dm_subt`||Enable 0 DM subtraction|
