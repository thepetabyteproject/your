<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/misc.py#L73)</span>

### crop


```python
your.utils.misc.crop(data, start_sample, length, axis)
```


Crops the input array to a required size

Args: 

    data (np.ndarray): Data array to crop
    start_sample (int): Sample to start the output cropped array
    length (int): Final Length along the axis of the output
    axis (int): Axis to crop

Returns: 

    np.ndarray: Cropped array


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/misc.py#L98)</span>

### pad_along_axis


```python
your.utils.misc.pad_along_axis(array, target_length, loc="end", axis=0, **kwargs)
```


Pads data along the required axis on the input array to reach a target size

Args: 

    array (np.ndarray): Input array to pad
    target_length (int): Required length of the axis
    loc (int): Location to pad: start: pad in beginning, end: pad in end, else: pad equally on both sides
    axis (int): Axis to pad along
    **kwargs: args for np.pad

Returns: 

    np.ndarray: Padded array


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/misc.py#L145)</span>

### MyEncoder


```python
your.utils.misc.MyEncoder(
    *,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    sort_keys=False,
    indent=None,
    separators=None,
    default=None
)
```


Custom Encoder Class to convert any class to a JSON serializable object


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/misc.py#L162)</span>

### YourArgparseFormatter


```python
your.utils.misc.YourArgparseFormatter(prog, indent_increment=2, max_help_position=24, width=None)
```


Allows both Raw Text Formatting and Default Args


----

