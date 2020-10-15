<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L14)</span>

### Candidate


```python
your.candidate.Candidate(
    fp=None, dm=None, tcand=0, width=0, label=-1, snr=0, min_samp=256, device=0, kill_mask=None
)
```


Candidate Class

Args: 

    fp Union[str, List]: String or a list of files. It can either filterbank or psrfits files.
    dm (float): Dispersion Measure of the candidate
    tcand (float): start time of the candidate in seconds at the highest frequency channel
    width (int): pulse width of the candidate in samples
    label (int): 1 for pulsars/FRBs, 0 for RFI
    snr (float): Signal to Noise Ratio
    min_samp (int): Minimum number of time samples
    device (int): GPU ID if using GPUs
    kill_mask (numpy.ndarray): Boolean mask of channels to kill


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L58)</span>

### save_h5


```python
Candidate.save_h5(out_dir=None, fnout=None)
```


Save the candidate to a hdf5 file

Args: 

    out_dir (str): path to the output directory
    fnout (str): output name of the file

Returns: 

    str: output name of the file


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L125)</span>

### dispersion_delay


```python
Candidate.dispersion_delay(dms=None)
```


Calculate the dispersion delay for the candidate DM or at given dispersion DM

Args: 

    dms (Union[float,np.ndarray]) : DM or a list of DMs

Returns: 

    Union[float, np.ndarray]: dispersion delay in seconds


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L146)</span>

### get_chunk


```python
Candidate.get_chunk(tstart=None, tstop=None, for_preprocessing=True)
```


Get a chunk of data. The data is saved in `self.data`.

Args: 

    tstart (float): start time of the chunk in seconds
    tstop (float): stop time of the chunk in seconds
    for_preprocessing (bool): if the data is to be preprocessed later. This will modify the number of samples
    read based on the width of the candidate


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L233)</span>

### dedisperse


```python
Candidate.dedisperse(dms=None, target="CPU")
```


Dedisperse a chunk of data. Saves the dedispersed chunk in `self.dedispersed`.

!!! note
    Our method rolls the data around while dedispersing it.

Args: 

    dms (float): The DM to dedisperse the data at.
    target (str): 'CPU' to run the code on the CPU or 'GPU' to run it on a GPU.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L274)</span>

### dedispersets


```python
Candidate.dedispersets(dms=None)
```


Create a dedispersed time series

!!! note
    Our method rolls the data around while dedispersing it.

Args: 

    dms (float): The DM to dedisperse the data at.

Returns: 

    numpy.ndarray: Dedispersed time series.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L307)</span>

### dmtime


```python
Candidate.dmtime(dmsteps=256, target="CPU")
```


Generates DM-time array of the candidate by dedispersing at adjacent DM values. Saves the data in `self.dmt`.

!!! note
    Our method rolls the data around while dedispersing it.

Args: 

    dmsteps (int) : Number of DMs to dedisperse at.
    target (str): 'CPU' to run the code on the CPU or 'GPU' to run it on a GPU.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L329)</span>

### get_snr


```python
Candidate.get_snr(time_series=None)
```


Calculates the SNR of the candidate

Args: 

    time_series (np.ndarray) : time series array to calculate the SNR of

Returns: 

    float: SNR


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L352)</span>

### optimize_dm


```python
Candidate.optimize_dm()
```


Calculate more precise value of the DM by interpolating between DM values to maximise the SNR

!!! note
    This function has not been fully tested.

Returns: 

    optimnised DM, optimised SNR


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L382)</span>

### decimate


```python
Candidate.decimate(key, decimate_factor, axis, pad=False, **kwargs)
```


Decimate FT or DMT data.

Todo:
    * Update candidate parameters as per decimation factor

Args: 

    key (str): Keywords to chose which data to decimate ('dmt' or 'ft')
    decimate_factor (int): Number of samples to average
    axis (int): Axis to decimate along
    pad (bool): Optional argument if padding is to be done
    **kwargs: kwargs for numpy.pad


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/candidate.py#L420)</span>

### resize


```python
Candidate.resize(key, size, axis, **kwargs)
```


Resize FT or DMT data

Todo:
    * Update candidate parameters as per final size

Args: 

    key (str): Keywords to chose which data to resize ('dmt' or 'ft')
    size: Final size of the data array required
    axis (int) : Axis to resize alone
    **kwargs: Arguments for skimage.transform resize function


----

