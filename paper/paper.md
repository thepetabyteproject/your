---
title: 'Your: Your Unified Reader'
tags:
  - Python
  - astronomy
  - fast transients
  - neutron stars
  - fast radio bursts
authors:
  - name: Kshitij Aggarwal
    orcid: 0000-0002-2059-0525
    affiliation: "1, 2" 
  - name: Devansh Agarwal
    orcid: 0000-0003-0385-491X
    affiliation: "1, 2"
  - name: Joseph W Kania
    affiliation: "1, 2"
  - name: William Fiore
    affiliation: "1, 2"
  - name: Reshma Anna Thomas
    affiliation: "1, 2"
  - name: Scott M. Ransom
    affiliation: "3"
  - name: Paul Demorest
    affiliation: "4"
  - name: Robert S. Wharton
    affiliation: "5" 
  - name: Sarah Burke-Spolaor
    affiliation: "1, 2"
  - name: Duncan R. Lorimer
    affiliation: "1, 2"
  - name: Maura A. Mclaughlin
    affiliation: "1, 2"
  - name: Nathaniel Garver-Daniels
    affiliation: "1, 2"
affiliations:
 - name: West Virginia University, Department of Physics and Astronomy, P. O. Box 6315, Morgantown 26506, WV, USA
   index: 1
 - name: Center for Gravitational Waves and Cosmology, West Virginia University, Chestnut Ridge Research Building, Morgantown 26506, WV, USA
   index: 2
 - name: National Radio Astronomy Observatory, Charlottesville, VA 22903, USA
   index: 3
 - name: National Radio Astronomy Observatory, Socorro, NM, 87801, USA
   index: 4
 - name: Max-Planck-Institut für Radioastronomie, Auf dem Hügel 69, D-53121 Bonn, Germany
   index: 5
date: 20 August 2020
bibliography: paper.bib

---


# Summary
The understanding of fast radio transients like pulsars, RRATs, and especially Fast Radio Bursts has evolved rapidly 
over the last decade. This is primarily due to dedicated transient search campaigns by sensitive radio telescopes. 
The advancement in signal processing and GPU processing systems has enabled new transient detectors at various 
telescopes to perform much more sensitive searches than their predecessors due to the ability to find and process FRB 
candidates in real-time or near-real-time. Typically the data output from the telescopes is in one of the two commonly
 used formats: psrfits [@hotan2004] and [`Sigproc filterbank`](http://sigproc.sourceforge.net/). Software developed for
  transient searches also work with either one of these two formats, limiting their general applicability. 
  Therefore, researchers have to write custom scripts to read/write the data in their format of choice before 
  they can begin any data analysis relevant for their 
 research. This has led to the development of several libraries to manage one or the other data format (like 
 [pysigproc](https://github.com/demorest/pysigproc), 
[psrfits](https://github.com/scottransom/presto/blob/master/python/presto/psrfits.py), 
[sigpyproc](https://github.com/FRBs/sigpyproc3), etc). Still, no general tool exists which can work across data formats.

`Your` (Your Unified Reader) is a pure-python-based library that unifies the data processing across multiple commonly 
used formats. `Your` was originally conceived to perform data ingestion for The Petabyte FRB search Project. As this 
project is going to process data in different formats from multiple telescopes worldwide, a unified reader was 
required to streamline the pipeline. `Your` implements a user-friendly interface to read and write in the data format 
of choice. It also generates unified metadata (or header) corresponding to the input data file for a quick 
understanding of observation parameters and provides utilities to perform common data analysis operations. `Your` also 
provide several state-of-the-art Radio Frequency Interference Mitigation algorithms [@agarwal2020; @nita2010], which 
can now be used during any stage of data processing (reading, writing, etc.) to filter out artificial signals.

`Your` can be used at the data ingestion step of any transient search pipeline and can provide data and observation 
parameters in a format-independent manner. Generic tools can thus be used to perform the search and further data 
analysis. It also enables online processing like RFI flagging, decimation, subband search, etc.; functions for some 
of these are already available in `Your`. It can also be used to perform analysis of individual candidate events (using 
`Candidate` class): generate candidate data cutouts, create publication-ready visualizations, and perform GPU accelerated 
pre-processing for candidate classification [@fetch2020]. It also consists of functions to run a commonly used single-pulse search 
software [`Heimdall`](https://sourceforge.net/projects/heimdall-astro/) [@barsdell2012] on any input data format.

`Your` will not only benefit experienced researchers but also new undergraduate and graduate students who 
otherwise have to face a significant bottleneck to understand various data formats and develop custom tools
to access the data, before any analysis can be done on it. Moreover, `Your` is written purely in python, which is a 
commonly used language within Astronomy. It also comes with comprehensive 
[documentation](https://devanshkv.github.io/your/) and 
[example notebooks](https://github.com/devanshkv/your/tree/master/examples) to make it easier to get started. 

`Your` uses the matplotlib library [@Hunter:2007] for plotting, and also makes use of various 
numpy [@oliphant2006guide; @van2011numpy], scipy [@2020SciPy], scikit-image [@van2014scikit], numba [@numba] and 
Pandas [@reback2020pandas; @pandas2010] functions. `Your` also relies heavily on several functions in the 
Astropy package [@astropy:2013; astropy:2018]: fits (astropy.io.fits), units (astropy.units), 
coordinates (astropy.coordinates) and time (astropy.time). 


# Acknowledgements


# References