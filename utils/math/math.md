### closest_number


```python
your.utils.math.closest_number(big_num, small_num)
```


Finds the difference between the closest multiple of a smaller number with respect to a bigger number

Args:

    big_num: The bigger number to find the closest of

    small_num: Number whose multiple is to be found and subtracted

Returns:

    The difference between the closest multiple of a smaller number with respect to a bigger number


----

### primes


```python
your.utils.math.primes(n)
```


All the prime factors of a positive number

Args:

    n: a positive number

Returns: primes


----

### closest_divisor


```python
your.utils.math.closest_divisor(n, m)
```


Calculates the divisor of n, which is closest to (i.e bigger than) m

Args:

    n: larger number of which divisor is to be found

    m: divisor closest to this number


Returns:

    The divisor of n, which is closest to (i.e bigger than) m


----

### find_gcd


```python
your.utils.math.find_gcd(list_of_nos)
```


Greatest Common Divisor for a list of nos

Args:

    list_of_nos: list of numbers

Returns:

    GCD


----

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

### smad_plotter


```python
your.utils.math.smad_plotter(freq_time, sigma=5.0, clip=True)
```


spectal Median Absolute Deviation clipper

Args:
    
    freq_time: the frequency time data

    sigma (float): sigma at which to clip data

    clip (bool): if true replaces clips the data else replaces it with zeroes

Returns:

    np.ndarray: clipped/flagged data


----

