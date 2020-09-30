<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L8)</span>

### closest_number


```python
your.utils.math.closest_number(big_num, small_num)
```


Finds the difference between the closest multiple of a smaller number with respect to a bigger number

Args: 

    big_num (int): The bigger number to find the closest of
    small_num (int) : Number whose multiple is to be found and subtracted

Returns: 

    int : The difference between the closest multiple of a smaller number with respect to a bigger number


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L27)</span>

### primes


```python
your.utils.math.primes(n)
```


All the prime factors of a positive number

Args: 


    n (int) : a positive number

Returns: 

    list: List of primes


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L51)</span>

### closest_divisor


```python
your.utils.math.closest_divisor(n, m)
```


Calculates the divisor of n, which is closest to (i.e bigger than) m

Args: 

    n (int) : larger number of which divisor is to be found
    m (int) : divisor closest to this number


Returns: 

    int : The divisor of n, which is closest to (i.e bigger than) m


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L74)</span>

### find_gcd


```python
your.utils.math.find_gcd(list_of_nos)
```


Greatest Common Divisor for a list of nos

Args: 


    list_of_nos (list) : list of numbers

Returns: 


    GCD


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L91)</span>

### normalise


```python
your.utils.math.normalise(data)
```


Subtract median, divide by standard deviations

Args: 

    data (numpy.ndarray): data

Returns: 

    numpy.ndarray: normalised data


----

<span style="float:right;">[[source]](https://github.com/thepetabyteproject/your/blob/master/your/utils/math.py#L108)</span>

### smad_plotter


```python
your.utils.math.smad_plotter(freq_time, sigma=5.0, clip=True)
```


Spectral Median Absolute Deviation clipper

Args: 

    freq_time (np.ndarray) : the frequency time data
    sigma (float): sigma at which to clip data
    clip (bool): if true replaces clips the data else replaces it with zeroes

Returns: 

    np.ndarray: clipped/flagged data


----

