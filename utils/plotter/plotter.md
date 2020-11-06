<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L17)</span>

### plot_h5


```python
your.utils.plotter.plot_h5(
    h5_file, save=True, detrend_ft=True, publication=False, mad_filter=False, outdir=None
)
```


Plot the h5 candidates

Args: 

    mad_filter (int): use MAD filter to clip data
    h5_file (str): Name of the h5 file
    save (bool): Save the file as a png
    detrend_ft (bool): detrend the frequency time plot
    publication (bool): make publication quality plot
    outdir (str): Path to the save the files into.

Returns: 

    None


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L132)</span>

### save_bandpass


```python
your.utils.plotter.save_bandpass(
    your_object, bandpass, chan_nos=None, mask=None, outdir=None, outname=None
)
```


Plots and saves the bandpass

Args: 

    your_object: Your object
    bandpass (np.ndarray): Bandpass of the data
    chan_nos (np.ndarray): Array of channel numbers
    mask (np.ndarray): Boolean Array of channel mask
    outdir (str) : Output directory to save the plot
    outname (str): Name of the bandpass file


----

