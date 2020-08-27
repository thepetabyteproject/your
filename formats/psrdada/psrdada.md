### DadaManager


```python
your.formats.dada.DadaManager(size, key=56026, n_readers=1)
```


A manager class for `psrdada` writer.

Args:

    size (int): size of each buffer (in bytes)

    key (hex): hexadecimal dada key

    n_readers (int): Number of dada readers.


----

### setup


```python
DadaManager.setup()
```


Kill any previous buffers with the same key.
Set up the dada buffers and connect to a writer.


----

### dump_header


```python
DadaManager.dump_header(header)
```


Set the psrdada header


----

### dump_data


```python
DadaManager.dump_data(data_input)
```


Dump the data to the buffer

Args:

    data_input (numpy.ndarray): Numpy array of the data.


----

### mark_filled


```python
DadaManager.mark_filled()
```


Mark that data is filled in the buffer page.


----

### eod


```python
DadaManager.eod()
```


Mark the end of data.


----

### teardown


```python
DadaManager.teardown()
```


Disconnect the writer and tear down the buffers.


----

### YourDada


```python
your.formats.dada.YourDada(your_object)
```


Linker class between `psrdada` and `your`.

Args:

    your_object: your object


----

### setup


```python
YourDada.setup()
```


Start the dada manager and make the header.


----

### teardown


```python
YourDada.teardown()
```


Tear down the dada header.


----

### your_dada_header


```python
YourDada.your_dada_header()
```


Make dada header from `your_header`.

Returns:

    dict: dada header as a python dictionary.


----

### to_dada


```python
YourDada.to_dada(progress=None)
```


Dump the data to the dada buffer

Args:

    progress: if `False` will not show the progress bar.


----

