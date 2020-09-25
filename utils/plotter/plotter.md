<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L17)</span>

### figsize


```python
your.utils.plotter.figsize(scale, width_by_height_ratio)
```


Create figure size either a full page or a half page figure

Args:

    scale (float): 0.5 for half page figure, 1 for full page

    width_by_height_ratio (float): ratio of width to height for the figure

Returns:

    list: list of width and height


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L41)</span>

### get_params


```python
your.utils.plotter.get_params(scale=0.5, width_by_height_ratio=1)
```


Create a dictionary for pretty plotting

Args:

    scale (float): 0.5 for half page figure, 1 for full page

    width_by_height_ratio (float): ratio of width to height for the figure

Returns:

    dict: dictionary of parameters


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L83)</span>

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

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/plotter.py#L181)</span>

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

