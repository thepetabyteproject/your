<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L17)</span>

### Writer


```python
your.writer.Writer(
    your_object,
    nstart=None,
    nsamp=None,
    c_min=None,
    c_max=None,
    outdir=None,
    outname=None,
    flag_rfi=False,
    progress=None,
    spectral_kurtosis_sigma=4,
    savgol_frequency_window=15,
    savgol_sigma=4,
    zero_dm_subt=False,
)
```


Writer class

Args:

    your_object: Your object

    nstart: Start sample to read from

    nsamp: Number of samples to write

    c_min: Starting channel index (default: 0)

    c_max: End channel index (default: total number of frequencies)

    outdir: Output directory for file

    outname: Name of the file to write to (without the file extension)

    progress: Turn on/off progress bar

    flag_rfi: To turn on RFI flagging

    sk_sig: Sigma for spectral kurtosis filter

    sg_fw: Filter window for savgol filter

    sg_sig: Sigma for savgol filter

    zero_dm_subt: Enable zero DM rfi excision


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L146)</span>

### to_fil


```python
Writer.to_fil()
```


Writes out a Filterbank File.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L190)</span>

### to_fits


```python
Writer.to_fits(npsub=-1)
```


Writes out a PSRFITS file

Args:

    npsub: number of spectra per subint


----

