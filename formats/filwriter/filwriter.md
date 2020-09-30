<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/filwriter.py#L11)</span>

### make_sigproc_obj


```python
your.formats.filwriter.make_sigproc_obj(filfile, your_object, nchans, chan_freq, nstart)
```


Use Your class to make Sigproc class object with relevant parameters

Args: 

    filfile (str) : Name of the Filterbank file
    your_object : Your object for the PSRFITS files
    nchans (int) : No. of channels in the frequency range
    chan_freq (np.ndarray) : An array of required frequency channel range
    nstart (int): Start sample

Returns: 

    Object of class SigprocFile


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/filwriter.py#L80)</span>

### write_fil


```python
your.formats.filwriter.write_fil(
    data, your_object, nchans=None, chan_freq=None, filename=None, outdir=None, nstart=None
)
```


Write Filterbank file given the Your object

Args: 

    data (np.ndarray): Data to write to the Filterbank file
    your_object: Your object for the PSRFITS files
    nchans (int) : No. of channels in the frequency range
    chan_freq (np.ndarray) : Required frequency channel range
    filename (str) : Output name of the Filterbank file
    outdir (str): Output directory for the Filterbank file
    nstart (int): Start sample number


----

