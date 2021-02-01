<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/heimdall.py#L52)</span>

### HeimdallManager


```python
your.utils.heimdall.HeimdallManager(
    dada_key=None,
    filename=None,
    verbosity=None,
    nsamps_gulp=262144,
    beam=None,
    baseline_length=2,
    output_dir=None,
    dm=None,
    dm_tol=1.25,
    zap_chans=None,
    max_giant_rate=None,
    dm_nbits=32,
    gpu_id=None,
    no_scrunching=False,
    rfi_tol=5,
    rfi_no_narrow=False,
    rfi_no_broad=False,
    boxcar_max=4096,
    fswap=None,
    min_tscrunch_width=None,
)
```


So you want to run heimdall, here is wrapper class which will allow you to do just that.

Args: 

    dada_key (hex): use PSRDADA hexidecimal key
    filename (str): process specified SIGPROC filterbank file
    verbosity (str): v, V, g, G increase verbosity level
    nsamps_gulp (int): number of samples to be read at a time
    beam (int): over-ride beam number
    baseline_length (float): number of seconds over which to smooth the baseline
    output_dir (str): create all output files in specified path
    dm (list): min and max DM
    dm_tol (float): SNR loss tolerance between each DM trial
    zap_chans (int): zap all channels between start and end channels inclusive
    max_giant_rate (int): limit the maximum number of individual detections per minute to nevents
    dm_nbits (int): number of bits per sample in dedispersed time series
    gpu_id (int): run on specified GPU
    no_scrunching (bool): don't use an adaptive time scrunching during dedispersion
    rfi_tol (float): RFI exicision threshold limits
    rfi_no_narrow (bool): disable narrow band RFI excision
    rfi_no_broad (bool): disable 0-DM RFI excision
    boxcar_max (int): maximum boxcar width in samples
    fswap (bool): swap channel ordering for negative DM - SIGPROC 2,4 or 8 bit only
    min_tscrunch_width: vary between high quality (large value) and high performance (low value)


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/heimdall.py#L128)</span>

### run


```python
HeimdallManager.run()
```


Make the heimdall command and run it.


----

