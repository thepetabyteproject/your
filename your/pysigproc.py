#!/usr/bin/env python

import mmap
import os
import struct
import sys
from collections import OrderedDict

import numpy


class SigprocFile(object):
    """
    Simple functions for reading sigproc filterbank files from python. Not all possible features are implemented.

    Original Source from Paul Demorest's [pysigproc.py](https://github.com/demorest/pysigproc/blob/master/pysigproc.py).

    Args:

        fp (str): file name

        copy_hdr (bool): copy header from another SigprocFile class object

    Attributes:

        rawdatafile (str): Raw data file

        source_name (str): Source Name

        machine_id (int) : Machine ID

        barycentric (int): If 1 the data is barycentered

        pulsarcentric (int): Is the data in pulsar's frame of reference?

        src_raj (float): RA of the source (HHMMSS.SS)

        src_deg (float): Dec of the source (DDMMSS.SS)

        az_start (float): Telescope Azimuth (degrees)

        za_start (float): Telescope Zenith Angle (degrees)

        fch1 (float): Frequency of first channel (MHz))

        foff (float): Channel bandwidth (MHz)

        nchans (int): Number of channels

        nbeams (int): Number of beams in the rcvr.

        ibeam (int): Beam number

        nbits (int): Number of bits the data are recorded in.

        tstart (float): Start MJD of the data

        tsamp (float): Sampling interval (seconds)

        nifs (int): Number of IFs in the data.

    """
    # List of types
    _type = OrderedDict()
    _type['rawdatafile'] = 'string'
    _type['source_name'] = 'string'
    _type['machine_id'] = 'int'
    _type['barycentric'] = 'int'
    _type['pulsarcentric'] = 'int'
    _type['telescope_id'] = 'int'
    _type['src_raj'] = 'double'
    _type['src_dej'] = 'double'
    _type['az_start'] = 'double'
    _type['za_start'] = 'double'
    _type['data_type'] = 'int'
    _type['fch1'] = 'double'
    _type['foff'] = 'double'
    _type['nchans'] = 'int'
    _type['nbeams'] = 'int'
    _type['ibeam'] = 'int'
    _type['nbits'] = 'int'
    _type['tstart'] = 'double'
    _type['tsamp'] = 'double'
    _type['nifs'] = 'int'

    def __init__(self, fp=None, copy_hdr=None):
        # init all items to None
        for k in list(self._type.keys()):
            setattr(self, k, None)
        if copy_hdr is not None:
            for k in list(self._type.keys()):
                setattr(self, k, getattr(copy_hdr, k))
        if fp is not None:
            try:
                self.fp = open(fp, 'rb')
            except TypeError:
                self.fp = fp
            self.read_header(self.fp)
            self._mmdata = mmap.mmap(self.fp.fileno(), 0, mmap.MAP_PRIVATE,
                                     mmap.PROT_READ)

    # See sigproc send_stuff.c

    @staticmethod
    def send_string(val, f=sys.stdout):
        """
        Encode and write a string.

        Args:

            val: value to encode

            f: file object to write the value into

        """
        val = val.encode()
        f.write(struct.pack('i', len(val)))
        f.write(val)

    def send_num(self, name, val, f=sys.stdout):
        """
        Encode a number

        Args:

            name: name to encode

            val: value to encode

            f: file object to write the value into

        """
        self.send_string(name, f)
        f.write(struct.pack(self._type[name][0], val))

    def send(self, name, f=sys.stdout):
        """

        Encode stuff

        Args:

            name: name to encode

            f: file object to encode the value into

        Returns:

        """
        if not hasattr(self, name): return
        if getattr(self, name) is None: return
        if self._type[name] == 'string':
            self.send_string(name, f)
            self.send_string(getattr(self, name), f)
        else:
            self.send_num(name, getattr(self, name), f)

    # See sigproc filterbank_header.c

    def filterbank_header(self, fout=sys.stdout):
        """

        Write the filterbank header

        Args:

            fout: output file object

        """
        self.send_string("HEADER_START", f=fout)
        for k in list(self._type.keys()):
            self.send(k, fout)
        self.send_string("HEADER_END", f=fout)

    # See sigproc read_header.c

    @staticmethod
    def get_string(fp):
        """
        Read the next sigproc-format string in the file.

        Args:

            fp: file object to read stuff from.

        """
        nchar = struct.unpack('i', fp.read(4))[0]
        if nchar > 80 or nchar < 1:
            return None, 0
        out = fp.read(nchar)
        return out, nchar + 4

    def read_header(self, fp=None):
        """
        Read the header from the specified file pointer.

        Args:

            fp: file object to read stuff from.

        """
        if fp is not None: self.fp = fp
        self.hdrbytes = 0
        (s, n) = self.get_string(self.fp)
        if s != b'HEADER_START':
            self.hdrbytes = 0
            return None
        self.hdrbytes += n
        while True:
            (s, n) = self.get_string(self.fp)
            s = s.decode()
            self.hdrbytes += n
            if s == 'HEADER_END': return
            if self._type[s] == 'string':
                (v, n) = self.get_string(self.fp)
                self.hdrbytes += n
                setattr(self, s, v)
            else:
                datatype = self._type[s][0]
                datasize = struct.calcsize(datatype)
                val = struct.unpack(datatype, self.fp.read(datasize))[0]
                setattr(self, s, val)
                self.hdrbytes += datasize

    @property
    def dtype(self):
        """

        Returns: dtype of the data

        """
        if self.nbits == 8:
            return numpy.uint8
        elif self.nbits == 16:
            return numpy.uint16
        elif self.nbits == 32:
            return numpy.float32
        else:
            raise RuntimeError('nbits=%d not supported' % self.nbits)

    @property
    def bytes_per_spectrum(self):
        """

        Returns: bytes per spectrum

        """
        return self.nbits * self.nchans * self.nifs / 8

    def nspectra(self):
        """

        Returns: Number of specrta in the file

        """
        return (self._mmdata.size() - self.hdrbytes) / self.bytes_per_spectrum

    def native_nspectra(self):
        """

        Native number of spectra in the file. This will be made a property so that it can't be overwritten

        Returns:Number of specrta in the file

        """

        return (self._mmdata.size() - self.hdrbytes) / self.bytes_per_spectrum

    def get_data(self, nstart, nsamp, offset=0, pol=0):
        """
        Return nsamp time slices starting at nstart.

        Args:

            nstart (int): Starting spectra number to start reading from.

            nsamp (int): Number of spectra to read.

            offset (int): Can be used to offset reading from.

            pol (int): Which polarisation to read.

        Returns:

            numpy.ndarray: data.
        """
        bstart = int(nstart) * self.bytes_per_spectrum
        nbytes = int(nsamp) * self.bytes_per_spectrum
        b0 = self.hdrbytes + bstart + (offset * self.bytes_per_spectrum)
        b1 = b0 + nbytes

        data = numpy.frombuffer(self._mmdata[int(b0):int(b1)],
                                dtype=self.dtype).reshape((-1, self.nifs, self.nchans))
        if self.nifs == 1:
            return data
        else:
            if pol == 0:
                return data[:, 0, :]
            elif pol == 1:
                return (data[:, 0, :] + data[:, 3, :]) / 2
            else:
                return (data[:, 0, :] - data[:, 3, :]) / 2

    def unpack(self, nstart, nsamp):
        """
        Unpack nsamp time slices starting at nstart to 32-bit floats.

        Args:

            nstart (int): Starting spectra number to start reading from.

            nsamp (int): Number of spectra to read.

        Returns:

            numpy.ndarray: Data
        """
        if self.nbits >= 8:
            return self.get_data(nstart, nsamp).astype(numpy.float32)
        bstart = int(nstart) * self.bytes_per_spectrum
        nbytes = int(nsamp) * self.bytes_per_spectrum
        b0 = self.hdrbytes + bstart
        b1 = b0 + nbytes
        # reshape with the frequency axis reduced by packing factor
        fac = 8 / self.nbits
        d = numpy.frombuffer(self._mmdata[b0:b1],
                             dtype=numpy.uint8).reshape(
            (nsamp, self.nifs, self.nchans / fac))
        unpacked = numpy.empty((nsamp, self.nifs, self.nchans),
                               dtype=numpy.float32)
        for i in range(fac):
            mask = 2 ** (self.nbits * i) * (2 ** self.nbits - 1)
            unpacked[..., i::fac] = (d & mask) / 2 ** (i * self.nbits)
        return unpacked

    def native_tsamp(self):
        """
        This will be made a property so that it can't be overwritten.

        Returns:

            Native sampling time of the filterbank.

        """
        return self.tsamp

    def native_foff(self):
        """

        This will be made a property so that it can't be overwritten.

        Returns:

            Native channel bandwidth of the filterbank.

        """
        return self.foff

    def native_nchans(self):
        """
        This will be made a property so that it can't be overwritten.

        Returns:

            Native number of channels in the filterbank.

        """
        return self.nchans

    def write_header(self, filename):
        """
        Write the filterbank header

        Args:

            filename (str): name of the filterbank file

        """
        with open(filename, 'wb') as f:
            self.filterbank_header(fout=f)
        return None

    @staticmethod
    def append_spectra(spectra, filename):
        """
        Append spectra to the end of the file

        Args:

            spectra (numpy.ndarray) : numpy array of the data to be dumped into the filterbank file

            filename (str): name of the filterbank file
        """
        with open(filename, 'ab') as f:
            f.seek(0, os.SEEK_END)
            f.write(spectra.flatten().astype(spectra.dtype))
