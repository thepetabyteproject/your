<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L14)</span>

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

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/formats/dada.py#L32)</span>

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

