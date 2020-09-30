<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L19)</span>

### Writer


```python
your.writer.Writer(
    your_object,
    nstart=0,
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


The unified writer class.

Args: 


    your_object: Your object
    nstart (int) : Start sample to read from
    nsamp (int) : Number of samples to write
    c_min (int) : Starting channel index (default: 0)
    c_max (int) : End channel index (default: total number of frequencies)
    outdir (str) : Output directory for file
    outname (str) : Name of the file to write to (without the file extension)
    progress: Turn on/off progress bar
    flag_rfi (bool) : To turn on RFI flagging
    spectral_kurtosis_sigma (float) : Sigma for spectral kurtosis filter
    savgol_frequency_window (float) : Filter window for savgol filter
    savgol_sigma (float) : Sigma for savgol filter
    zero_dm_subt (bool) : Enable zero DM rfi excision


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L158)</span>

### to_fil


```python
Writer.to_fil()
```


Writes out a Filterbank File.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L215)</span>

### to_fits


```python
Writer.to_fits(npsub=-1)
```


Writes out a PSRFITS file

Args: 

    npsub (int) : number of spectra per subint


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L310)</span>

### dada_header


```python
Writer.dada_header()
```


Create the psrdada header dictionary

Returns: 

    dict: psrdada header dictionary


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L335)</span>

### setup_dada


```python
Writer.setup_dada(dada_key=None, data_step=None)
```


Set up the psrdada buffers.

Args: 

    dada_key (hex): hex key, if left None, key would be chosen randomly
    data_step (int): size of each page in the ring buffer in bytes


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L367)</span>

### to_dada


```python
Writer.to_dada()
```


Start the process of dumping data to the dada buffers till the EOF.


----

