
your_viewer.py
==============

# Description


Read psrfits/filterbank files and show the data
# Epilog




Takes Dynamic Spectra (Frequency-Time data) from filterbank/fits files,

and displays in a GUI.



Shows time series above spectra and bandpass to the right.



It also reports some basic statistics of the data.



Key Binds:

    Left Arrow: Move the previous gulp



    Right Arrow: Move the the next gulp


# Usage:


```bash
usage: your_viewer.py [-h] [-f FILES [FILES ...]] [-s START] [-g GULP] [-e] [-d width height] [-dm DM] [-subtract] [-v]

```
# Arguments

|short|long|default|help|
| :--- | :--- | :--- | :--- |
|`-h`|`--help`||show this help message and exit|
|`-f`|`--files`|`['']`|Fits or filterbank files to view.|
|`-s`|`--start`|`0`|Start index|
|`-g`|`--gulp`|`4096`|Gulp size|
|`-e`|`--chan_std`||Show 1 standard deviation per channel in bandpass|
|`-d`|`--display`|`[1024, 640]`|Display size for the plot|
|`-dm`|`--dm`|`0`|DM to dedisperse the data|
|`-subtract`|`--bandpass_subtract`||subtract a polynomial fitted bandpass|
|`-v`|`--verbose`||Be verbose|
