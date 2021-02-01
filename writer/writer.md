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
    progress=True,
    spectral_kurtosis_sigma=4,
    savgol_frequency_window=15,
    savgol_sigma=4,
    gulp=None,
    zero_dm_subt=False,
    time_decimation_factor=1,
    frequency_decimation_factor=1,
    replacement_policy="mean",
)
```


The unified writer class.

Args: 


    your_object: Your object
    nstart (int): Start sample to read from
    nsamp (int): Number of samples to write
    c_min (int): Starting channel index (default: 0)
    c_max (int): End channel index (default: total number of frequencies)
    outdir (str): Output directory for file
    outname (str): Name of the file to write to (without the file extension)
    progress (bool): Set to it to false to disable progress bars
    flag_rfi (bool): To turn on RFI flagging
    spectral_kurtosis_sigma (float): Sigma for spectral kurtosis filter
    savgol_frequency_window (float): Filter window for savgol filter
    savgol_sigma (float):  Sigma for savgol filter
    gulp (int): Gulp size for the data
    zero_dm_subt (bool): Enable zero DM rfi excision
    time_decimation_factor (int): Time Decimation Factor (in number of samples)
    frequency_decimation_factor (int): Frequency Decimation Factor (in number of samples)
    replacement_policy (str): Replace flagged values with mean, median or zeros.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L211)</span>

### to_fil


```python
Writer.to_fil(data=None)
```


Writes out a Filterbank File.

Args: 
 data (np.ndarray):  Write out your custom data from a numpy array. If not specified it will read the
input file and write with the attributes setup in the writer class.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L270)</span>

### to_fits


```python
Writer.to_fits(npsub=-1)
```


Writes out a PSRFITS file

Args: 

    npsub (int): number of spectra per subint


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L167)</span>

### get_data_to_write


```python
Writer.get_data_to_write(start_sample, nsamp)
```


Read data to self.data, selects channels
Optionally perform RFI filtering and zero-DM subtraction

Args: 


    start_sample (int): Start sample number to read from
    nsamp (int): Number of samples to read


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L368)</span>

### dada_header


```python
Writer.dada_header()
```


Create the psrdada header dictionary

Returns: 

    dict: psrdada header dictionary


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L390)</span>

### setup_dada


```python
Writer.setup_dada(dada_key=None, data_step=None)
```


Set up the psrdada buffers.

Args: 

    dada_key (hex): hex key, if left None, key would be chosen randomly
    data_step (int): size of each page in the ring buffer in bytes


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/writer.py#L420)</span>

### to_dada


```python
Writer.to_dada()
```


Start the process of dumping data to the dada buffers till the EOF.


----

