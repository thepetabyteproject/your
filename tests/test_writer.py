import os

from your import Your
from your.writer import Writer

_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_fil_to_fil():
    # from fil
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    # test with outname
    w.to_fil(nstart=0, nsamp=2, outname='temp.fil', c=[0, 200], outdir='./', flag_rfi=True, zero_dm_subt=True)
    assert os.path.isfile('temp.fil')
    y = Your('temp.fil')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == 200
    os.remove('temp.fil')

    # test without outname
    w.to_fil(nstart=0, nsamp=1, outdir='./')
    assert os.path.isfile('small_converted.fil')
    y = Your('small_converted.fil')
    assert y.your_header.nspectra == 1
    assert y.your_header.nchans == f.your_header.nchans
    os.remove('small_converted.fil')

def test_fits_to_fil():
    # from fits
    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    # test with outname
    w.to_fil(nstart=0, nsamp=1, outname='temp.fil', outdir='./', c=[0, 200])
    assert os.path.isfile('temp.fil')
    y = Your('temp.fil')
    assert y.your_header.nspectra == 1
    assert y.your_header.nchans == 200
    os.remove('temp.fil')

    # test without outname
    w.to_fil(nstart=0, nsamp=2, outdir='./')
    assert os.path.isfile('small_converted.fil')
    y = Your('small_converted.fil')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == f.your_header.nchans
    os.remove('small_converted.fil')

def test_fil_to_fits():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    # test with outname
    w.to_fits(outname='temp.fits', outdir='./', flag_rfi=True, zero_dm_subt=True, nstart=0, nsamp=2, c=[0, 200])
    assert os.path.isfile('temp.fits')
    y = Your('temp.fits')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == 200
    os.remove('temp.fits')

    # test without  outname
    w.to_fits(outdir='./')
    assert os.path.isfile('small_converted.fits')
    y = Your('small_converted.fits')
    assert y.your_header.nchans == f.your_header.nchans
    os.remove('small_converted.fits')

def test_fits_to_fits():
    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    # test with outname
    w.to_fits(outname='temp.fits', outdir='./', nstart=0, nsamp=2)
    assert os.path.isfile('temp.fits')
    y =Your('temp.fits')
    assert y.your_header.nspectra == 2
    assert y.your_header.nchans == f.your_header.nchans
    os.remove('temp.fits')

    # test without  outname
    w.to_fits(outdir='./', c=[0, 10])
    assert os.path.isfile('small_converted.fits')
    y = Your('small_converted.fits')
    assert y.your_header.nchans == 10
    os.remove('small_converted.fits')
