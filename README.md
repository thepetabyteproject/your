# your

  
[![GitHub issues](https://img.shields.io/github/issues/thepetabyteproject/your?style=flat-square)](https://github.com/thepetabyteproject/your/issues)
[![GitHub forks](https://img.shields.io/github/forks/thepetabyteproject/your?style=flat-square)](https://github.com/thepetabyteproject/your/network)
[![GitHub stars](https://img.shields.io/github/stars/thepetabyteproject/your?style=flat-square)](https://github.com/thepetabyteproject/your/stargazers)
[![GitHub license](https://img.shields.io/github/license/thepetabyteproject/your?style=flat-square)](https://github.com/thepetabyteproject/your/blob/master/LICENSE)
[![HitCount](http://hits.dwyl.com/devanshkv/your.svg)](http://hits.dwyl.com/devanshkv/your)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/your?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/your?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/your?style=flat-square)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

[![codecov](https://codecov.io/gh/thepetabyteproject/your/branch/master/graph/badge.svg?style=flat-square)](https://codecov.io/gh/thepetabyteproject/your)
![Python package](https://github.com/thepetabyteproject/your/workflows/Python%20package/badge.svg?style=flat-square)
[![status](https://joss.theoj.org/papers/798844ebd352f563de28bb75515da674/status.svg?style=flat-square)](https://joss.theoj.org/papers/798844ebd352f563de28bb75515da674)



`your` stands for Your Unified Reader. This library can read data in [Sigproc Filterbank](http://sigproc.sourceforge.net), 
[PSRFITS](https://www.atnf.csiro.au/research/pulsar/psrfits_definition/Psrfits.html), 
and [PSRDADA](http://psrdada.sourceforge.net) formats in a unified way and can convert from one format to another. 


| Format        | Read                     | Write               |
| ------------- |:-------------:           | -----:              |
| filterbank    | :white_check_mark:       | :white_check_mark:  |
| psrfits       | :white_check_mark:       | :white_check_mark:  |
| psrdada       | :x:                      | :white_check_mark:  |

`your` implements a user-friendly interface to read and write in the data format of choice. It also generates unified 
metadata corresponding to the input data file for a quick understanding of observation parameters and provides 
utilities to perform common data analysis operations. `your` can be used at the data ingestion step of any transient 
search pipeline and can provide data and observation parameters in a format-independent manner. Generic tools can thus 
be used to perform the search and further data analysis. It also enables online processing like RFI flagging, 
decimation, subband search, etc.; functions for some of these are already available in `your`.

`your` will not only be useful to experienced researchers but also new undergraduate and graduate students who otherwise 
have to face a significant bottleneck to understand various data formats and develop custom tools to access the data 
before any analysis can be done on it. 

The inspiration for the name comes from the introduction of every [Daily Dose of Internet](https://www.youtube.com/channel/UCdC0An4ZPNr_YiFiYoVbwaw) video.

# Installation
You can install `your` directly using `pip`

```bash
pip install your
```
Or if you want to try out the lastest stuff,
```bash
pip install git+https://github.com/thepetabyteproject/your.git
```

or you can do: 
```bash
git clone https://github.com/thepetabyteproject/your.git
cd your
pip install -r requirements.txt
python setup.py install
``` 

**Note**:
    To use the `psrdada` format, you would need to install [psrdada-python](https://github.com/TRASAL/psrdada-python). [`your_heimdall.py`](https://thepetabyteproject.github.io/your/bin/your_heimdall/) requires [Heimdall](https://sourceforge.net/projects/heimdall-astro/) and [psrdada-python](https://github.com/TRASAL/psrdada-python). 
    To run the tests you would need to install `pytest`. 


# Documentation
Have a look at our [docs](https://thepetabyteproject.github.io/your/) for the documentation.

# Tutorials
Here are some [tutorial notebooks](https://github.com/devanshkv/your/tree/master/examples) to get you started.

**Note**: 
    To run the tutorial notebooks you would need to install `jupyter`. 

# Code Contributions
We welcome all types of code contribution. Please have a look at our [guideline](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md).

# Citation
If you use `Your`, please cite our [JOSS Paper](https://joss.theoj.org/papers/10.21105/joss.02750):

```bash
@article{Aggarwal2020,
  doi = {10.21105/joss.02750},
  url = {https://doi.org/10.21105/joss.02750},
  year = {2020},
  publisher = {The Open Journal},
  volume = {5},
  number = {55},
  pages = {2750},
  author = {Kshitij Aggarwal and Devansh Agarwal and Joseph W. Kania and William Fiore and Reshma Anna Thomas and Scott M. Ransom and Paul B. Demorest and Robert S. Wharton and Sarah Burke-Spolaor and Duncan R. Lorimer and Maura A. Mclaughlin and Nathaniel Garver-Daniels},
  title = {Your: Your Unified Reader},
  journal = {Journal of Open Source Software}
}
```
