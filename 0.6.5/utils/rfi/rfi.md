<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/rfi.py#L10)</span>

### savgol_filter


```python
your.utils.rfi.savgol_filter(bandpass, channel_bandwidth, frequency_window=15, sigma=6)
```


Apply savgol filter to the data. See [Agarwal el al. 2020](https://arxiv.org/abs/2003.14272) for details.

Args: 

    bandpass (numpy.ndarray): bandpass of the data
    channel_bandwidth (float): channel bandwidth (MHz)
    frequency_window (float): frequency window (MHz)
    sigma (float): sigma value to apply cutoff on

Returns: 

    numpy.ndarray: mask for channels


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/rfi.py#L50)</span>

### spectral_kurtosis


```python
your.utils.rfi.spectral_kurtosis(data, N=1, d=None)
```


Compute spectral kurtosis. See [Nita et al. (2016)](https://doi.org/10.1109/RFINT.2016.7833535) for details.

Args: 

    data (numpy.ndarray): 2D frequency time data
    N (int): Number of accumulations on the FPGA
    d (float): shape factor

Returns: 

     numpy.ndarray: Spectral Kurtosis along frequency axis


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/rfi.py#L73)</span>

### sk_filter


```python
your.utils.rfi.sk_filter(data, channel_bandwidth, tsamp, N=None, d=None, sigma=5)
```


Apply Spectral Kurtosis filter to the data

Args: 

    data (numpy.ndarray): 2D frequency time data
    channel_bandwidth (float): channel bandwidth (MHz)
    tsamp (float): sampling time (seconds)
    N (int): Number of accumulations on the FPGA
    d (float): shape factor
    sigma (float): sigma value to apply cutoff on

Returns: 

     numpy.ndarray: mask for channels


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/rfi.py#L102)</span>

### calc_N


```python
your.utils.rfi.calc_N(channel_bandwidth, tsamp)
```


Calculates number of accumulations on FPGA

Args: 

    channel_bandwidth (float): channel bandwidth (MHz)
    tsamp (float): sampling time (seconds)

Returns: 

    int: FPGA accumulation length


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/rfi.py#L120)</span>

### sk_sg_filter


```python
your.utils.rfi.sk_sg_filter(
    data, your_object, spectral_kurtosis_sigma=6, savgol_frequency_window=15, savgol_sigma=5
)
```


Apply Spectral Kurtosis and Savgol filter to the data

Args: 

    data (numpy.ndarray): 2D frequency time data
    your_object: Your object
    spectral_kurtosis_sigma (float): sigma value to apply cutoff on for SK filter
    savgol_frequency_window (float): frequency window for savgol filter(MHz)
    savgol_sigma (float): sigma value to apply cutoff on for savgol filter


Returns: 

     numpy.ndarray: mask for channels


----

