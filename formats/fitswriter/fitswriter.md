### initialize_psrfits


```python
your.formats.fitswriter.initialize_psrfits(
    outfile, your_object, npsub=-1, nstart=None, nsamp=None, chan_freqs=None
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


----

### ObsInfo


```python
your.formats.fitswriter.ObsInfo()
```


Class to setup observation info for psrfits header


----

