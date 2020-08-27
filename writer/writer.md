### Writer


```python
your.writer.Writer(
    y,
    nstart=None,
    nsamp=None,
    c_min=None,
    c_max=None,
    outdir=None,
    outname=None,
    flag_rfi=False,
    progress=None,
    sk_sig=4,
    sg_fw=15,
    sg_sig=4,
    zero_dm_subt=False,
)
```


Writer class

Args:

    y: Your object

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

### to_fil


```python
Writer.to_fil()
```


Writes out a Filterbank File.


----

### to_fits


```python
Writer.to_fits(npsub=-1)
```


Writes out a PSRFITS file

Args:

    npsub: number of spectra per subint


----

