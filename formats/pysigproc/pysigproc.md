<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/pysigproc.py#L15)</span>

### SigprocFile


```python
your.formats.pysigproc.SigprocFile(fp=None, copy_hdr=None)
```


Simple functions for reading sigproc filterbank files from python. Not all possible features are implemented.

Original Source from Paul Demorest's [pysigproc.py](https://github.com/demorest/pysigproc/blob/master/pysigproc.py).

Args: 


    fp (str): file name
    copy_hdr (bool): copy header from another SigprocFile class object

Attributes: 


    rawdatafile (str): Raw data file
    source_name (str): Source Name
    machine_id (int): Machine ID
    barycentric (int): If 1 the data is barycentered
    pulsarcentric (int): Is the data in pulsar's frame of reference?
    src_raj (float): RA of the source (HHMMSS.SS)
    src_deg (float): Dec of the source (DDMMSS.SS)
    az_start (float): Telescope Azimuth (degrees)
    za_start (float): Telescope Zenith Angle (degrees)
    fch1 (float): Frequency of first channel (MHz))
    foff (float): Channel bandwidth (MHz)
    nchans (int): Number of channels
    nbeams (int): Number of beams in the rcvr.
    ibeam (int): Beam number
    nbits (int): Number of bits the data are recorded in.
    tstart (float): Start MJD of the data
    tsamp (float): Sampling interval (seconds)
    nifs (int): Number of IFs in the data.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/pysigproc.py#L277)</span>

### get_data


```python
SigprocFile.get_data(nstart, nsamp, offset=0, pol=0)
```


Return nsamp time slices starting at nstart.

Args: 

    nstart (int): Starting spectra number to start reading from.
    nsamp (int): Number of spectra to read.
    offset (int): Can be used to offset reading from.
    pol (int): Which polarisation to read.

Returns: 

    numpy.ndarray: data.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/pysigproc.py#L308)</span>

### unpack


```python
SigprocFile.unpack(nstart, nsamp)
```


Unpack nsamp time slices starting at nstart to 32-bit floats.

Args: 

    nstart (int): Starting spectra number to start reading from.
    nsamp (int): Number of spectra to read.

Returns: 

    numpy.ndarray: Data


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/pysigproc.py#L367)</span>

### write_header


```python
SigprocFile.write_header(filename)
```


Write the filterbank header

Args: 

    filename (str): name of the filterbank file


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/pysigproc.py#L379)</span>

### append_spectra


```python
SigprocFile.append_spectra(spectra, filename)
```


Append spectra to the end of the file

Args: 

    spectra (numpy.ndarray): numpy array of the data to be dumped into the filterbank file
    filename (str): name of the filterbank file


----

