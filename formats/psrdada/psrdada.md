<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L18)</span>

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

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L36)</span>

### setup


```python
DadaManager.setup()
```


Kill any previous buffers with the same key.
Set up the dada buffers and connect to a writer.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L48)</span>

### dump_header


```python
DadaManager.dump_header(header)
```


Set the psrdada header


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L54)</span>

### dump_data


```python
DadaManager.dump_data(data_input)
```


Dump the data to the buffer

Args:

    data_input (numpy.ndarray): Numpy array of the data.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L68)</span>

### mark_filled


```python
DadaManager.mark_filled()
```


Mark that data is filled in the buffer page.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L74)</span>

### eod


```python
DadaManager.eod()
```


Mark the end of data.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L80)</span>

### teardown


```python
DadaManager.teardown()
```


Disconnect the writer and tear down the buffers.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L89)</span>

### YourDada


```python
your.formats.dada.YourDada(your_object)
```


Linker class between `psrdada` and `your`.

Args:

    your_object: your object


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L125)</span>

### setup


```python
YourDada.setup()
```


Start the dada manager and make the header.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L135)</span>

### teardown


```python
YourDada.teardown()
```


Tear down the dada header.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L142)</span>

### your_dada_header


```python
YourDada.your_dada_header()
```


Make dada header from `your_header`.

Returns:

    dict: dada header as a python dictionary.


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L166)</span>

### to_dada


```python
YourDada.to_dada(progress=None)
```


Dump the data to the dada buffer

Args:

    progress: if `False` will not show the progress bar.


----

