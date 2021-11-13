<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/filwriter.py#L8)</span>

### sigproc_object_from_writer


```python
your.formats.filwriter.sigproc_object_from_writer(your_writer)
```


Convert a `your_writer` object to Sigproc object for writing

Args: 

    your_writer: `your_writer` object

Returns: 

    sigproc object


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/filwriter.py#L72)</span>

### make_sigproc_object


```python
your.formats.filwriter.make_sigproc_object(
    rawdatafile,
    source_name,
    nchans,
    foff,
    fch1,
    tsamp,
    tstart,
    src_raj=112233.44,
    src_dej=112233.44,
    machine_id=0,
    nbeams=0,
    ibeam=0,
    nbits=8,
    nifs=1,
    barycentric=0,
    pulsarcentric=0,
    telescope_id=6,
    data_type=0,
    az_start=-1,
    za_start=-1,
)
```


Create a Sigprocfile from scratch.

Args: 

    rawdatafile (str): Raw file name
    source_name (str): Source Name
    nchans (int): Number of channels
    foff (float): Channel Bandwidth (MHz)
    fch1 (float): Frequncy of first channel (MHz)
    tsamp (float): Sampling interval (seconds)
    tstart (float): MJD of the start sample
    src_raj (float): RA of the source in format HHMMSS.SS
    src_dej (float): Dec of source in format DDMMSS.SS
    machine_id (int): Machine ID
    nbeams (int): Number of beams in the rcvr
    ibeam (int): Beam number
    nbits (int): Number of bits
    nifs (int): Number of IFs
    barycentric (int): 0 for not barycentered data, 1 otherwise.
    pulsarcentric (int): 0 for not pulsarcentered data, 1 otherwise.
    telescope_id (int): Telescope ID
    data_type (int): Data Type
    az_start (float): Azimuth Angle start
    za_start (float):  Zenith Angle start

Returns: 

    sigproc object


----

