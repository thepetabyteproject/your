<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/fitswriter.py#L262)</span>

### initialize_psrfits


```python
your.formats.fitswriter.initialize_psrfits(
    outfile, your_object, npsub=-1, nstart=None, nsamp=None, chan_freqs=None, npoln=1, poln_order="AA+BB"
)
```


Set up a PSRFITS file with everything set up EXCEPT
the DATA.

Args: 

    outfile: path to the output fits file to write to
    your_object: your object with the input Filterbank file
    npsub: number of spectra in a subint
    nstart: start sample to read from (for the input file)
    nsamp: number of spectra to read
    chan_freqs: array with frequencies of all the channels
    npoln: number of polarisations in the output file
    poln_order: polsarisation order


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/fitswriter.py#L18)</span>

### ObsInfo


```python
your.formats.fitswriter.ObsInfo()
```


Class to setup observation info for psrfits header


----

