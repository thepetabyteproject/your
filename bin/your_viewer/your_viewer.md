
your_viewer.py
==============

# Description


Read psrfits/filterbank files and show the data
# Epilog



This script can be used to visualize the data (Frequency-Time, bandpass and time series). It also reports some basic statistics of the data. 


# Usage:


```bash
usage: your_viewer.py [-h] [-f FILES [FILES ...]] [-s START] [-g GULP] [-e] [-d width height] [-v]

```
# Arguments

|short|long|default|help|
| :---: | :---: | :---: | :---: |
|`-h`|`--help`||show this help message and exit|
|`-f`|`--files`|`['']`|Fits or filterbank files to view.|
|`-s`|`--start`|`0`|Start index|
|`-g`|`--gulp`|`4096`|Gulp size|
|`-e`|`--chan_std`||Show 1 standard devation per channel in bandpass|
|`-d`|`--display`|`[1024, 640]`|Display size for the plot|
|`-v`|`--verbose`||Be verbose|
