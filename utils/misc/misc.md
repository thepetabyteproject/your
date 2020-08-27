### crop


```python
your.utils.misc.crop(data, start_sample, length, axis)
```


Crops the input array to a required size

Args:

    data: Data array to crop

    start_sample: Sample to start the output cropped array

    length: Final Length along the axis of the output

    axis: Axis to crop

Returns:

    Cropped array


----

### pad_along_axis


```python
your.utils.misc.pad_along_axis(array, target_length, loc="end", axis=0, **kwargs)
```


Pads data along the required axis on the input array to reach a target size

Args:

    array: Input array to pad

    target_length: Required length of the axis

    loc: Location to pad: start: pad in beginning, end: pad in end, else: pad equally on both sides

    axis: Axis to pad along

Returns:

    Padded array


----

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

