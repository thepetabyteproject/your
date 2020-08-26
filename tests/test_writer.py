import os

from your import Your
from your.writer import Writer

_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_fil_to_fil():
    # from fil
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f, nstart=0, nsamp=2, outname='temp', c_min=10, c_max=200, outdir='./', flag_rfi=False,
               zero_dm_subt=False)
    # test with outname
    w.to_fil()
    assert os.path.isfile('temp.fil')
    y = Your('temp.fil')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == 190
    assert (y.get_data(0, 2) - f.get_data(0, 2)[:, 10:200]).sum() == 0
    os.remove('temp.fil')

    # test without outname
    w = Writer(f, nstart=0, nsamp=10, outdir='./', flag_rfi=True)
    w.to_fil()
    assert os.path.isfile('small_converted.fil')
    y = Your('small_converted.fil')
    assert y.your_header.nspectra == 10
    assert y.your_header.nchans == f.your_header.nchans
    os.remove('small_converted.fil')


def test_fits_to_fil():
    # from fits
    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f, nstart=0, nsamp=1, outname='temp', outdir='./', c_min=0, c_max=200)
    # test with outname
    w.to_fil()
    assert os.path.isfile('temp.fil')
    y = Your('temp.fil')
    assert y.your_header.nspectra == 1
    assert y.your_header.nchans == 200
    assert (y.get_data(0, 1) - f.get_data(0, 1)[:, 0:200]).sum() == 0
    os.remove('temp.fil')

    # test without outname
    w = Writer(f, outdir='./')
    w.to_fil()
    assert os.path.isfile('small_converted.fil')
    y = Your('small_converted.fil')
    assert y.your_header.nspectra == f.your_header.nspectra
    ns = y.your_header.nspectra
    assert y.your_header.nchans == f.your_header.nchans
    assert (y.get_data(0, ns) - f.get_data(0, ns)).sum() == 0
    os.remove('small_converted.fil')


def test_fil_to_fits():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f, outname='temp', outdir='./', flag_rfi=False, zero_dm_subt=False, nstart=0, nsamp=2, c_min=40,
               c_max=200)
    # test with outname
    w.to_fits()
    assert os.path.isfile('temp.fits')
    y = Your('temp.fits')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == 160
    assert (y.get_data(0, 2) - f.get_data(0, 2)[:, 40:200]).sum() == 0
    os.remove('temp.fits')

    # test without  outname
    w = Writer(f, outdir='./', flag_rfi=True, zero_dm_subt=True)
    w.to_fits()
    assert os.path.isfile('small_converted.fits')
    y = Your('small_converted.fits')
    assert y.your_header.nchans == f.your_header.nchans
    ns = y.your_header.nspectra
    os.remove('small_converted.fits')


def test_fits_to_fits():
    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f, outname='temp', outdir='./', nstart=0, nsamp=2)
    # test with outname
    w.to_fits()
    assert os.path.isfile('temp.fits')
    y = Your('temp.fits')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == f.your_header.nchans
    assert (y.get_data(0, 2) - f.get_data(0, 2)).sum() == 0
    os.remove('temp.fits')

    # test without  outname
    w = Writer(f, outdir='./', c_min=0, c_max=10)
    w.to_fits()
    assert os.path.isfile('small_converted.fits')
    y = Your('small_converted.fits')
    assert y.your_header.nchans == 10
    ns = y.your_header.nspectra
    assert (y.get_data(0, ns) - f.get_data(0, ns)[:, 0:10]).sum() == 0
    os.remove('small_converted.fits')
