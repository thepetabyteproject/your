#!/usr/bin/env python

import logging
import mmap
import os
import struct
import sys
import tempfile
from collections import OrderedDict

import numpy

from your.utils.astro import dec2deg, ra2deg


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
        machine_id (int): Machine ID
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
    _type["rawdatafile"] = "string"
    _type["source_name"] = "string"
    _type["machine_id"] = "int"
    _type["barycentric"] = "int"
    _type["pulsarcentric"] = "int"
    _type["telescope_id"] = "int"
    _type["src_raj"] = "double"
    _type["src_dej"] = "double"
    _type["az_start"] = "double"
    _type["za_start"] = "double"
    _type["data_type"] = "int"
    _type["fch1"] = "double"
    _type["foff"] = "double"
    _type["nchans"] = "int"
    _type["nbeams"] = "int"
    _type["ibeam"] = "int"
    _type["nbits"] = "int"
    _type["tstart"] = "double"
    _type["tsamp"] = "double"
    _type["nifs"] = "int"

    def __init__(self, fp=None, copy_hdr=None):
        # init all items to None
        for k in list(self._type.keys()):
            setattr(self, k, None)
        # Set by read_header when reading, by write_header when writing.
        self.hdrbytes = None
        # Set by allocate_file: the number of spectra the file is sized for.
        self.nspectra_alloc = None
        if copy_hdr is not None:
            for k in list(self._type.keys()):
                setattr(self, k, getattr(copy_hdr, k))
        if fp is not None:
            try:
                self.fp = open(fp, "rb")
            except TypeError:
                self.fp = fp
            self.read_header(self.fp)
            self._mmdata = mmap.mmap(
                self.fp.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ
            )

            self.bw = self.nchans * self.foff
            self.cfreq = self.fch1 + (self.bw / 2) - (self.foff / 2)
            if self.nifs == 1:
                self.poln_order = "I"
            elif self.nifs == 4:
                self.poln_order = "IQUV"
            else:
                raise ValueError("Invalid number of ifs in Filterbank file.")
            if self.src_raj and self.src_dej:
                self.ra_deg = ra2deg(self.src_raj)
                self.dec_deg = dec2deg(self.src_dej)
            else:
                self.ra_deg = None
                self.dec_deg = None

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
        f.write(struct.pack("i", len(val)))
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

        """
        if not hasattr(self, name):
            return
        if getattr(self, name) is None:
            return
        if self._type[name] == "string":
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
        nchar = struct.unpack("i", fp.read(4))[0]
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
        if fp is not None:
            self.fp = fp
        self.hdrbytes = 0
        s, n = self.get_string(self.fp)
        logging.debug(f"Reading {s} from the Filterbank file header.")
        if s != b"HEADER_START":
            self.hdrbytes = 0
            return None
        self.hdrbytes += n
        while True:
            s, n = self.get_string(self.fp)
            logging.debug(f"Reading parameter {s, n} from the Filterbank file header.")
            try:
                s = s.decode()
                self.hdrbytes += n
                if s in self._type and n > 0:
                    if self._type[s] == "string":
                        v, n = self.get_string(self.fp)
                        self.hdrbytes += n
                        setattr(self, s, v)
                    else:
                        datatype = self._type[s][0]
                        datasize = struct.calcsize(datatype)
                        val = struct.unpack(datatype, self.fp.read(datasize))[0]
                        setattr(self, s, val)
                        self.hdrbytes += datasize
                elif "HEADER_END" in s:
                    return
                else:
                    logging.warning(
                        f"Unknown header parameter: {s}. Skipping it and continuing. This may lead to "
                        f"incorrect header values."
                    )
                    self.hdrbytes += n
                    logging.warning("Skipping next 4 bytes of data.")
                    self.fp.read(4)
            except AttributeError:
                logging.warning(
                    f"Unknown header parameter: {s}. This may lead to incorrect header values."
                )
                self.hdrbytes += n

    @property
    def dtype(self):
        """

        Returns:
            dtype of the data

        """
        if self.nbits == 8:
            return numpy.uint8
        elif self.nbits == 16:
            return numpy.uint16
        elif self.nbits == 32:
            return numpy.float32
        else:
            raise RuntimeError("nbits=%d not supported" % self.nbits)

    @property
    def bytes_per_spectrum(self):
        """

        Returns:
            bytes per spectrum

        """
        return self.nbits * self.nchans * self.nifs / 8

    def nspectra(self):
        """

        Returns:
            Number of specrta in the file

        """
        return (self._mmdata.size() - self.hdrbytes) / self.bytes_per_spectrum

    def native_nspectra(self):
        """

        Native number of spectra in the file. This will be made a property so that it can't be overwritten

        Returns:
            Number of specrta in the file

        """

        return (self._mmdata.size() - self.hdrbytes) / self.bytes_per_spectrum

    def get_data(self, nstart, nsamp, offset=0, pol=0, npoln=1):
        """
        Return nsamp time slices starting at nstart.

        Args:
            nstart (int): Starting spectra number to start reading from.
            nsamp (int): Number of spectra to read.
            offset (int): Can be used to offset reading from.
            pol (int): Which polarisation to read.
            npoln (int): Number of polarisations to read.

        Returns:
            numpy.ndarray: data.
        """
        assert npoln in [1, 4], "npoln can only be 1 or 4"

        bstart = int(nstart) * self.bytes_per_spectrum
        nbytes = int(nsamp) * self.bytes_per_spectrum
        b0 = self.hdrbytes + bstart + (offset * self.bytes_per_spectrum)
        b1 = b0 + nbytes

        data = numpy.frombuffer(
            self._mmdata[int(b0) : int(b1)], dtype=self.dtype
        ).reshape((-1, self.nifs, self.nchans))

        if self.nifs == 1:
            return data

        if npoln == 1:
            if pol == 0:
                return data[:, 0, :]
            elif pol == 1:
                return (data[:, 0, :] + data[:, 3, :]) / 2
            else:
                return (data[:, 0, :] - data[:, 3, :]) / 2
        else:
            return data

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
        d = numpy.frombuffer(self._mmdata[b0:b1], dtype=numpy.uint8).reshape(
            (nsamp, self.nifs, self.nchans / fac)
        )
        unpacked = numpy.empty((nsamp, self.nifs, self.nchans), dtype=numpy.float32)
        for i in range(fac):
            mask = 2 ** (self.nbits * i) * (2**self.nbits - 1)
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

        Note:
            This opens the file in `"wb"` mode, which truncates it. Never call
            it on a file another process is writing data to.

            The size of the header just written is recorded in
            :attr:`hdrbytes`, so that positional writes
            (:meth:`write_spectra_at`) know where the data starts. Until this
            is called (or :meth:`read_header`), `hdrbytes` is not set.

        Args:
            filename (str): name of the filterbank file

        """
        with open(filename, "wb") as f:
            self.filterbank_header(fout=f)
        # hdrbytes is otherwise only set by read_header. Take it from the file
        # size now, while the file is nothing but a header.
        self.hdrbytes = os.path.getsize(filename)
        return None

    @staticmethod
    def append_spectra(spectra, filename):
        """
        Append spectra to the end of the file

        Args:
            spectra (numpy.ndarray): numpy array of the data to be dumped into the filterbank file
            filename (str): name of the filterbank file
        """
        with open(filename, "ab") as f:
            f.seek(0, os.SEEK_END)
            f.write(spectra.flatten().astype(spectra.dtype))

    def _spectrum_nbytes(self):
        """
        Bytes on disk per spectrum, as an int, for addressing samples.

        Unlike :attr:`bytes_per_spectrum`, which is a float, this refuses a
        geometry it cannot address rather than returning a fraction.

        Returns:
            int: bytes per spectrum.

        Raises:
            ValueError: if any of `nchans`, `nbits` or `nifs` is unset, or if
                one spectrum is not a whole number of bytes.

        """
        for name in ("nchans", "nbits", "nifs"):
            if getattr(self, name) is None:
                raise ValueError(f"{name} is not set, cannot address samples.")

        # Guard 1: a spectrum must be a whole number of bytes, else sample n
        # does not start on a byte boundary and cannot be written on its own.
        bits = int(self.nbits) * int(self.nchans) * int(self.nifs)
        if bits % 8:
            raise ValueError(
                f"{self.nchans} channels x {self.nifs} IFs at {self.nbits} "
                f"bits is {bits / 8} bytes per spectrum, not a whole number. "
                "Packed data with this geometry cannot be written positionally."
            )
        return bits // 8

    def _byte_geometry(self):
        """
        The geometry needed to address a spectrum by its sample number.

        Returns:
            tuple: `(hdrbytes, bytes_per_spectrum)`, both ints.

        Raises:
            ValueError: if the header size is unknown, or the geometry cannot
                address samples (see :meth:`_spectrum_nbytes`).

        """
        if self.hdrbytes is None:
            raise ValueError(
                "hdrbytes is not set, so the start of the data is unknown. It "
                "is set by read_header() and by write_header(); for a file "
                "written elsewhere, set it to the size of the header in bytes."
            )
        return int(self.hdrbytes), self._spectrum_nbytes()

    def allocate_file(self, filename, nspectra):
        """
        Write the header and size the file for `nspectra` spectra of data.

        This is the coordinator's half of a parallel write: it is the only
        step that truncates, so it must happen once, before any worker opens
        the file. Afterwards every byte of data has an address, and workers
        can fill non-overlapping sample ranges with :meth:`write_spectra_at`
        in any order. On ext4 the file is sparse until written, so this costs
        nothing and allocates nothing.

        Sizing the file up front also makes a short final gulp a non-issue:
        the file is already the right length whatever the last worker writes.

        Note:
            A worker that dies part way through leaves a hole of zeros that
            looks like data. Check that every worker exited zero before
            treating the file as complete.

        Args:
            filename (str): name of the filterbank file
            nspectra (int): number of spectra the finished file will hold

        Returns:
            int: size of the header in bytes (also stored as `hdrbytes`)

        Raises:
            ValueError: if `nspectra` is negative, or the geometry cannot
                address samples (see :meth:`_byte_geometry`).

        """
        nspectra = int(nspectra)
        if nspectra < 0:
            raise ValueError(f"nspectra must be >= 0, got {nspectra}")
        # Check the geometry before write_header, which truncates: a file this
        # cannot address is better left uncreated than left empty.
        bps = self._spectrum_nbytes()

        self.write_header(filename)
        hdrbytes = self.hdrbytes

        with open(filename, "r+b") as f:
            f.truncate(hdrbytes + nspectra * bps)

        self.nspectra_alloc = nspectra
        logging.debug(
            f"Allocated {filename}: {hdrbytes} byte header + {nspectra} "
            f"spectra x {bps} bytes."
        )
        return hdrbytes

    @staticmethod
    def check_work_division(ranges, nspectra):
        """
        Check that the work division covers every sample exactly once.

        Nothing inside :meth:`write_spectra_at` can see this: a call is given
        one range and has no knowledge of the others. The check belongs here,
        at the coordinator, where the division is decided -- and before any
        worker starts, which is the last moment an overlap or a gap is free to
        fix. It is arithmetic on the range list; it does not touch the file.

        Args:
            ranges: iterable of `(start_sample, nsamples)`, one per unit of
                work, in any order. Empty ranges are ignored, so a worker with
                nothing to do can be left in.
            nspectra (int): number of spectra the finished file will hold.

        Returns:
            None

        Raises:
            ValueError: if any range is negative, or if the ranges overlap,
                leave a gap, or run past `nspectra`. The message names the
                offending sample ranges.

        """
        nspectra = int(nspectra)
        if nspectra < 0:
            raise ValueError(f"nspectra must be >= 0, got {nspectra}")

        work = []
        for start, nsamples in ranges:
            start, nsamples = int(start), int(nsamples)
            if start < 0 or nsamples < 0:
                raise ValueError(
                    f"({start}, {nsamples}) is not a valid range: both the "
                    "start sample and the length must be >= 0."
                )
            if nsamples:
                work.append((start, nsamples))
        work.sort()

        overlaps, gaps, end = [], [], 0
        for start, nsamples in work:
            if start < end:
                overlaps.append((start, min(end, start + nsamples) - start))
            elif start > end:
                gaps.append((end, start - end))
            end = max(end, start + nsamples)
        if end < nspectra:
            gaps.append((end, nspectra - end))

        problems = []
        if overlaps:
            problems.append(f"{len(overlaps)} overlap(s): {overlaps[:4]}")
        if gaps:
            problems.append(f"{len(gaps)} gap(s): {gaps[:4]}")
        if end > nspectra:
            problems.append(f"work runs to sample {end}, past {nspectra}")
        if problems:
            raise ValueError(
                "The work division does not cover samples 0-"
                f"{nspectra} exactly once. " + "; ".join(problems)
            )
        logging.debug(
            f"Work division checked: {len(work)} ranges tile {nspectra} spectra."
        )
        return None

    def write_spectra_at(
        self, spectra, filename, start_sample, nspectra=None, sync=False
    ):
        """
        Write spectra so that their first row is sample `start_sample`.

        Unlike :meth:`append_spectra`, which opens the file in `"ab"` mode and
        so lands every write at the end of the file whatever the seek, this
        addresses the data by sample number. Non-overlapping ranges can
        therefore be written concurrently, by any number of threads or
        processes, in any order: the write is a single `os.pwrite` against an
        fd private to this call, which POSIX makes atomic with respect to
        other writers of other ranges. Overlapping ranges are the caller's
        problem; nothing here detects them.

        The file must already exist with its header written, normally by
        :meth:`allocate_file`. It is opened `"r+b"` and never truncated. A
        write past the end extends the file, leaving a hole of zeros in
        between.

        Note:
            Written as is: `spectra` must already have the file's on-disk
            dtype, since nothing here casts it. The size check below will
            catch the common mistakes, but not, say, `int8` for `uint8`.

        Args:
            spectra (numpy.ndarray): data to write, shaped `(nsamples,
                nchans)`, or `(nsamples, nifs, nchans)` when `nifs > 1`.
            filename (str): name of the filterbank file
            start_sample (int): sample number of the first row of `spectra`
            nspectra (int): total number of spectra the file will hold, used
                to bound the write. Defaults to `nspectra_alloc`, set by
                :meth:`allocate_file`. If neither is known the upper bound is
                not checked and the file is extended as needed.
            sync (bool): fsync the file before returning. A worker that writes
                many gulps wants this off, and one fsync before it exits.

        Returns:
            None

        Raises:
            ValueError: if the geometry cannot address samples, if `spectra`
                does not match the file's shape or dtype, or if the write
                falls outside the file.
            FileNotFoundError: if `filename` does not exist. Write the header
                first; this function will not create the file, because doing
                so would hide a worker pointed at the wrong path.

        """
        hdrbytes, bps = self._byte_geometry()
        start_sample = int(start_sample)

        spectra = numpy.ascontiguousarray(spectra)  # guard 3
        if spectra.ndim < 2:
            raise ValueError(
                f"spectra must have a sample axis and a channel axis, got "
                f"shape {spectra.shape}."
            )
        nsamples = spectra.shape[0]

        # Guard 2: the channel axis must match the file. For nbits >= 8 the
        # last axis is channels; for packed data it is channels/(8/nbits),
        # which the byte count below covers.
        if self.nbits >= 8 and spectra.shape[-1] != self.nchans:
            raise ValueError(
                f"spectra has {spectra.shape[-1]} channels, the file has {self.nchans}."
            )
        if spectra.ndim == 3 and spectra.shape[1] != self.nifs:
            raise ValueError(
                f"spectra has {spectra.shape[1]} IFs, the file has {self.nifs}."
            )
        if spectra.nbytes != nsamples * bps:
            raise ValueError(
                f"{nsamples} spectra of dtype {spectra.dtype} and shape "
                f"{spectra.shape} are {spectra.nbytes} bytes, but the file "
                f"holds {bps} bytes per spectrum ({nsamples * bps} in total). "
                "Cast the data to the file's dtype before writing."
            )

        # Guard 4: stay inside the file.
        if start_sample < 0:
            raise ValueError(f"start_sample must be >= 0, got {start_sample}")
        if nspectra is None:
            nspectra = self.nspectra_alloc
        if nspectra is not None and start_sample + nsamples > int(nspectra):
            raise ValueError(
                f"Writing {nsamples} spectra at sample {start_sample} runs to "
                f"{start_sample + nsamples}, past the {int(nspectra)} spectra "
                "this file holds."
            )

        offset = hdrbytes + start_sample * bps
        # "r+b", i.e. O_RDWR: never O_APPEND, under which Linux ignores the
        # offset given to pwrite and puts the data at the end of the file.
        fd = os.open(filename, os.O_RDWR)
        try:
            view = memoryview(spectra.data).cast("B")
            while len(view):
                written = os.pwrite(fd, view, offset)
                if written == 0:
                    raise OSError(f"Wrote 0 of {len(view)} bytes to {filename}")
                view = view[written:]
                offset += written
            if sync:
                os.fsync(fd)
        finally:
            os.close(fd)
        logging.debug(
            f"Wrote samples {start_sample}-{start_sample + nsamples} to {filename}."
        )
        return None

    @staticmethod
    def _holes_are_reported(directory):
        """
        Does this filesystem report unwritten extents as holes?

        A filesystem that does not know about holes answers `SEEK_HOLE` with
        the end of the file, which reads as "no holes found", which reads as
        "the file is complete". That false pass is worse than no check, so
        :meth:`find_holes` asks this first and refuses rather than guesses.
        ext4 reports holes; NFS does not, before v4.2.

        Args:
            directory (str): where to put the probe file. Must be on the same
                filesystem as the file about to be scanned.

        Returns:
            bool: True if a known hole was reported as one.

        """
        try:
            with tempfile.NamedTemporaryFile(dir=directory) as probe:
                fd = probe.fileno()
                os.ftruncate(fd, 1 << 20)
                # Allocate the last block only; everything before it is a hole.
                os.pwrite(fd, b"\0", (1 << 20) - 1)
                os.fsync(fd)
                return os.lseek(fd, 0, os.SEEK_HOLE) == 0
        except OSError as error:
            logging.debug(f"Could not probe {directory} for holes: {error}")
            return False

    def find_holes(self, filename, nspectra=None):
        """
        Find the samples of a preallocated file that were never written.

        :meth:`allocate_file` sizes the file with `truncate`, so it is sparse:
        a range no worker ever wrote is an unallocated extent, not zeros on
        disk. `SEEK_HOLE` enumerates those in a couple of syscalls per hole,
        without reading a byte -- which is the point, since a worker that dies
        mid-range leaves a file of exactly the right length whose missing
        samples no length check and no checksum can see.

        Note:
            Run this after the workers have finished and before anything else
            rewrites the file; a hole that gets written over stops being one.

            Holes are found to filesystem-block precision, so a gap of one
            spectrum may or may not be visible, while a gap of a whole gulp
            always is. It reports what was never *written*, not what was
            written *wrongly*: a worker that wrote nonsense passes.

        Args:
            filename (str): name of the filterbank file
            nspectra (int): number of spectra the file should hold. Defaults
                to `nspectra_alloc`, then to the file's own length.

        Returns:
            list: `(start_sample, nsamples)` of each unwritten range, in
            sample order. Empty if every sample was written.

        Raises:
            OSError: if the filesystem cannot report holes, so that a file
                this check cannot vouch for is never reported as complete.

        """
        hdrbytes, bps = self._byte_geometry()
        on_disk = os.path.getsize(filename)
        if nspectra is None:
            nspectra = self.nspectra_alloc
        if nspectra is None:
            nspectra = (on_disk - hdrbytes) // bps
        nspectra = int(nspectra)
        size = hdrbytes + nspectra * bps

        directory = os.path.dirname(os.path.abspath(filename))
        if not self._holes_are_reported(directory):
            raise OSError(
                f"{directory} does not report holes, or could not be probed, "
                f"so an unwritten range in {filename} is indistinguishable "
                "from a written one. Check the workers' exit codes instead. "
                "Run with debug logging to see which of the two it was."
            )

        byte_holes = []
        fd = os.open(filename, os.O_RDONLY)
        try:
            position = hdrbytes
            while position < min(size, on_disk):
                hole = os.lseek(fd, position, os.SEEK_HOLE)
                if hole >= min(size, on_disk):
                    break
                try:
                    data = os.lseek(fd, hole, os.SEEK_DATA)
                except OSError:
                    data = on_disk  # the hole runs to the end of the file
                byte_holes.append((hole, min(data, size)))
                position = data
        finally:
            os.close(fd)
        # A file shorter than it should be is missing its tail, not holed.
        if on_disk < size:
            byte_holes.append((max(on_disk, hdrbytes), size))

        holes = []
        for first_byte, last_byte in byte_holes:
            # Round outwards: a spectrum that only partly overlaps a hole was
            # not written whole, so it is missing too.
            first = max(0, (first_byte - hdrbytes) // bps)
            last = min(nspectra, -((hdrbytes - last_byte) // bps))
            # Rounding outwards can make two holes meet, when a block of
            # written data between them is shorter than one spectrum.
            if holes and first <= holes[-1][0] + holes[-1][1]:
                start, nsamples = holes[-1]
                holes[-1] = (start, max(start + nsamples, last) - start)
            else:
                holes.append((first, last - first))
        return holes

    def verify_complete(self, filename, nspectra=None):
        """
        Check that a finished file is the right length and has no holes.

        The two halves catch different failures. The length catches a file
        that was never preallocated, or was truncated after the fact. The hole
        scan catches a worker that died inside its range -- which leaves the
        length correct, and is the reason the length assertion alone is not
        enough once :meth:`allocate_file` is in use.

        Args:
            filename (str): name of the filterbank file
            nspectra (int): number of spectra the file should hold. Defaults
                to `nspectra_alloc`.

        Returns:
            None

        Raises:
            ValueError: if the file is the wrong length, or if any sample was
                never written. The message names the missing sample ranges.
            OSError: if the filesystem cannot report holes (see
                :meth:`find_holes`).

        """
        hdrbytes, bps = self._byte_geometry()
        if nspectra is None:
            nspectra = self.nspectra_alloc
        if nspectra is None:
            raise ValueError(
                "nspectra is not known, so there is nothing to check the file "
                "against. Pass it, or use the object that called "
                "allocate_file()."
            )
        nspectra = int(nspectra)

        expected = hdrbytes + nspectra * bps
        on_disk = os.path.getsize(filename)
        if on_disk != expected:
            raise ValueError(
                f"{filename} is {on_disk} bytes, expected {expected} "
                f"({hdrbytes} byte header + {nspectra} x {bps})."
            )

        holes = self.find_holes(filename, nspectra=nspectra)
        if holes:
            missing = sum(nsamples for _, nsamples in holes)
            raise ValueError(
                f"{filename} is the right length but {missing} spectra were "
                f"never written, in {len(holes)} range(s): {holes[:4]}. Treat "
                "it as a failed file, not a partial one."
            )
        logging.debug(f"{filename} is complete: {nspectra} spectra, no holes.")
        return None
