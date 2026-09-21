import os

import numpy as np
import pytest

from your.formats.filwriter import make_sigproc_object
from your.formats.pysigproc import SigprocFile

_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_pysigproc_obj():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    fil_obj = SigprocFile(fil_file)
    assert fil_obj.nchans == 336


def test_get_data_fil():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    fil_obj = SigprocFile(fil_file)
    data = fil_obj.get_data(0, 10)
    assert np.isclose(np.mean(data), 128, atol=1)


def test_pol():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    fil_obj = SigprocFile(fil_file)
    assert fil_obj.poln_order == "I"
    with pytest.raises(AssertionError):
        d = fil_obj.get_data(0, 10, npoln=3)


def _fil_object(nchans=32, nbits=8):
    return make_sigproc_object(
        rawdatafile="positional.fil",
        source_name="fake",
        nchans=nchans,
        foff=-1.0,
        fch1=1500.0,
        tsamp=0.000256,
        tstart=60000.0,
        nbits=nbits,
    )


def _fake_data(nspectra, nchans, dtype=np.uint8):
    rng = np.random.default_rng(seed=nspectra)
    return rng.integers(0, 255, size=(nspectra, nchans)).astype(dtype)


def _write_gulp(args):
    """Worker body for the multiprocessing test. Must be importable."""
    filename, hdrbytes, nchans, nbits, nspectra, start_sample, data = args
    fil_obj = _fil_object(nchans=nchans, nbits=nbits)
    fil_obj.hdrbytes = hdrbytes
    fil_obj.write_spectra_at(data, filename, start_sample, nspectra=nspectra, sync=True)


def test_write_header_sets_hdrbytes(tmp_path):
    fil_obj = _fil_object()
    assert fil_obj.hdrbytes is None
    out = str(tmp_path / "header.fil")
    fil_obj.write_header(out)
    assert fil_obj.hdrbytes == os.path.getsize(out)
    assert fil_obj.hdrbytes > 0


def test_allocate_file(tmp_path):
    nchans, nspectra = 32, 100
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "allocated.fil")
    hdrbytes = fil_obj.allocate_file(out, nspectra)

    assert fil_obj.nspectra_alloc == nspectra
    assert os.path.getsize(out) == hdrbytes + nspectra * nchans
    # untouched bytes are zeros, not data
    assert not np.any(SigprocFile(out).get_data(0, nspectra).squeeze())


def test_write_spectra_at_matches_append(tmp_path):
    """Out-of-order positional writes must give the same bytes as appending."""
    nchans, gulp, ngulps = 32, 16, 8
    nspectra = gulp * ngulps
    data = _fake_data(nspectra, nchans)

    appended = str(tmp_path / "appended.fil")
    fil_obj = _fil_object(nchans=nchans)
    fil_obj.write_header(appended)
    for j in range(0, nspectra, gulp):
        fil_obj.append_spectra(data[j : j + gulp], appended)

    positional = str(tmp_path / "positional.fil")
    fil_obj = _fil_object(nchans=nchans)
    fil_obj.allocate_file(positional, nspectra)
    for j in sorted(range(0, nspectra, gulp), reverse=True):
        fil_obj.write_spectra_at(data[j : j + gulp], positional, j)

    assert os.path.getsize(positional) == fil_obj.hdrbytes + nspectra * nchans
    with open(appended, "rb") as a, open(positional, "rb") as b:
        assert a.read() == b.read()
    assert np.array_equal(SigprocFile(positional).get_data(0, nspectra).squeeze(), data)


def test_write_spectra_at_short_last_gulp(tmp_path):
    """A gulp that does not divide nspectra leaves the file the right length."""
    nchans, gulp, nspectra = 32, 16, 100
    data = _fake_data(nspectra, nchans)

    out = str(tmp_path / "remainder.fil")
    fil_obj = _fil_object(nchans=nchans)
    hdrbytes = fil_obj.allocate_file(out, nspectra)
    for j in range(0, nspectra, gulp):
        fil_obj.write_spectra_at(data[j : j + gulp], out, j)

    assert os.path.getsize(out) == hdrbytes + nspectra * nchans
    assert np.array_equal(SigprocFile(out).get_data(0, nspectra).squeeze(), data)


def test_write_spectra_at_parallel_processes(tmp_path):
    """Round-robin gulps written by four processes, byte-identical to serial."""
    import multiprocessing

    nchans, gulp, ngulps, nworkers = 32, 16, 16, 4
    nspectra = gulp * ngulps
    data = _fake_data(nspectra, nchans)

    serial = str(tmp_path / "serial.fil")
    fil_obj = _fil_object(nchans=nchans)
    fil_obj.allocate_file(serial, nspectra)
    for j in range(0, nspectra, gulp):
        fil_obj.write_spectra_at(data[j : j + gulp], serial, j)

    parallel = str(tmp_path / "parallel.fil")
    coordinator = _fil_object(nchans=nchans)
    hdrbytes = coordinator.allocate_file(parallel, nspectra)

    jobs = []
    for k in range(nworkers):
        for g in range(k, ngulps, nworkers):  # round robin, as the workers do
            j = g * gulp
            jobs.append(
                (parallel, hdrbytes, nchans, 8, nspectra, j, data[j : j + gulp])
            )

    with multiprocessing.Pool(nworkers) as pool:
        # exit codes are the only correctness signal: let the errors raise
        for _ in pool.imap_unordered(_write_gulp, jobs):
            pass

    assert os.path.getsize(parallel) == os.path.getsize(serial)
    with open(serial, "rb") as a, open(parallel, "rb") as b:
        assert a.read() == b.read()


def test_write_spectra_at_extends_file(tmp_path):
    """Without a preallocation the file grows, and the gap is zeros."""
    nchans = 32
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "extended.fil")
    fil_obj.write_header(out)

    data = _fake_data(10, nchans)
    fil_obj.write_spectra_at(data, out, 20)

    assert os.path.getsize(out) == fil_obj.hdrbytes + 30 * nchans
    read_back = SigprocFile(out)
    assert not np.any(read_back.get_data(0, 20))
    assert np.array_equal(read_back.get_data(20, 10).squeeze(), data)


def test_write_spectra_at_never_truncates(tmp_path):
    nchans, nspectra = 32, 64
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "keep_length.fil")
    fil_obj.allocate_file(out, nspectra)
    size = os.path.getsize(out)
    fil_obj.write_spectra_at(_fake_data(8, nchans), out, 0)
    assert os.path.getsize(out) == size


def test_write_spectra_at_guards(tmp_path):
    nchans, nspectra = 32, 64
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "guards.fil")
    fil_obj.allocate_file(out, nspectra)
    data = _fake_data(8, nchans)

    # wrong number of channels
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(_fake_data(8, nchans // 2), out, 0)

    # not cast to the file's dtype
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(data.astype(np.float32), out, 0)

    # no sample axis
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(data.flatten(), out, 0)

    # before the start of the data
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(data, out, -1)

    # past the end of the file
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(data, out, nspectra - 4)

    # the file has to exist already
    with pytest.raises(FileNotFoundError):
        fil_obj.write_spectra_at(data, str(tmp_path / "absent.fil"), 0)

    # a non-contiguous view is copied, not rejected
    fil_obj.write_spectra_at(np.asfortranarray(data), out, 0)
    assert np.array_equal(SigprocFile(out).get_data(0, 8).squeeze(), data)


def test_write_spectra_at_needs_whole_bytes(tmp_path):
    """3 channels at 4 bits is 1.5 bytes a spectrum: no sample has an address."""
    fil_obj = _fil_object(nchans=3, nbits=4)
    out = str(tmp_path / "packed.fil")
    with pytest.raises(ValueError):
        fil_obj.allocate_file(out, 64)

    # but a whole number of bytes at 4 bits is fine
    fil_obj = _fil_object(nchans=32, nbits=4)
    out = str(tmp_path / "packed_ok.fil")
    hdrbytes = fil_obj.allocate_file(out, 64)
    packed = _fake_data(8, 16)
    fil_obj.write_spectra_at(packed, out, 8)
    with open(out, "rb") as f:
        f.seek(hdrbytes + 8 * 16)
        assert f.read(8 * 16) == packed.tobytes()


def test_write_spectra_at_without_hdrbytes(tmp_path):
    """A header of unknown size is an error, not a guess."""
    fil_obj = _fil_object()
    out = str(tmp_path / "unknown.fil")
    fil_obj.write_header(out)
    fil_obj.hdrbytes = None
    with pytest.raises(ValueError):
        fil_obj.write_spectra_at(_fake_data(8, 32), out, 0)


def test_write_spectra_at_from_existing_file(tmp_path):
    """A worker can take the geometry off the file the coordinator made."""
    nchans, nspectra = 32, 64
    out = str(tmp_path / "worker.fil")
    _fil_object(nchans=nchans).allocate_file(out, nspectra)

    data = _fake_data(16, nchans)
    worker_obj = SigprocFile(out)  # read_header sets hdrbytes, nchans, nbits
    worker_obj.write_spectra_at(data, out, 32, nspectra=nspectra)

    assert np.array_equal(SigprocFile(out).get_data(32, 16).squeeze(), data)


def test_write_spectra_at_needs_a_geometry(tmp_path):
    """Without nchans/nbits/nifs there is nothing to compute an offset from."""
    fil_obj = _fil_object()
    out = str(tmp_path / "no_geometry.fil")
    fil_obj.allocate_file(out, 64)
    data = _fake_data(8, 32)

    for name in ("nchans", "nbits", "nifs"):
        broken = _fil_object()
        broken.hdrbytes = fil_obj.hdrbytes
        setattr(broken, name, None)
        with pytest.raises(ValueError, match=name):
            broken.write_spectra_at(data, out, 0)


def test_allocate_file_rejects_negative_nspectra(tmp_path):
    out = str(tmp_path / "negative.fil")
    with pytest.raises(ValueError):
        _fil_object().allocate_file(out, -1)
    assert not os.path.exists(out)  # nothing created, nothing truncated


def test_write_spectra_at_checks_nifs(tmp_path):
    nchans, nspectra = 32, 64
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "ifs.fil")
    fil_obj.allocate_file(out, nspectra)

    # the file has nifs=1, so a 4-IF array is the wrong shape even though
    # its channel axis matches
    four_ifs = _fake_data(2 * 4, nchans).reshape(2, 4, nchans)
    with pytest.raises(ValueError, match="IFs"):
        fil_obj.write_spectra_at(four_ifs, out, 0)


def test_write_spectra_at_sync(tmp_path):
    nchans = 32
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "synced.fil")
    fil_obj.allocate_file(out, 64)
    data = _fake_data(8, nchans)
    fil_obj.write_spectra_at(data, out, 8, sync=True)
    assert np.array_equal(SigprocFile(out).get_data(8, 8).squeeze(), data)


def test_write_spectra_at_partial_write(tmp_path, monkeypatch):
    """A short pwrite must be resumed, and a zero-byte one must not spin."""
    nchans = 32
    fil_obj = _fil_object(nchans=nchans)
    out = str(tmp_path / "partial.fil")
    fil_obj.allocate_file(out, 64)
    data = _fake_data(8, nchans)

    real_pwrite = os.pwrite
    calls = []

    def short_pwrite(fd, buf, offset):
        calls.append(len(buf))
        return real_pwrite(fd, bytes(buf)[:64], offset)  # 64 bytes at a time

    monkeypatch.setattr(os, "pwrite", short_pwrite)
    fil_obj.write_spectra_at(data, out, 0)
    monkeypatch.undo()

    assert len(calls) == data.nbytes // 64  # it kept going, it did not give up
    assert np.array_equal(SigprocFile(out).get_data(0, 8).squeeze(), data)

    monkeypatch.setattr(os, "pwrite", lambda fd, buf, offset: 0)
    with pytest.raises(OSError):
        fil_obj.write_spectra_at(data, out, 0)
