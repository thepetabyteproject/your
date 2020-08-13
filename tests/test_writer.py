import os

from your import Your
from your.io.writer import Writer

_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_to_fil():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    w.to_fil(nstart=0, nsamp=2, outname='temp.fil', c=[1, 200], outdir='./', flag_rfi=True, zero_dm_subt=True)
    assert os.path.isfile('temp.fil')
    os.remove('temp.fil')

    w.to_fil(nstart=0, nsamp=1, outdir='./')
    assert os.path.isfile('small_converted.fil')
    os.remove('small_converted.fil')

    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    w.to_fil(nstart=0, nsamp=1, outname='temp.fil', outdir='./')
    assert os.path.isfile('temp.fil')
    os.remove('temp.fil')

    w.to_fil(nstart=0, nsamp=2, outdir='./')
    assert os.path.isfile('small_converted.fil')
    os.remove('small_converted.fil')


def test_to_fits():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    w.to_fits(outname='temp.fits', outdir='./', flag_rfi=True, zero_dm_subt=True)
    assert os.path.isfile('temp.fits')
    os.remove('temp.fits')

    w.to_fits(outdir='./')
    assert os.path.isfile('small_converted.fits')
    os.remove('small_converted.fits')

    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    w.to_fits(outname='temp.fits', outdir='./')
    assert os.path.isfile('temp.fits')
    os.remove('temp.fits')

    w.to_fits(outdir='./')
    assert os.path.isfile('small_converted.fits')
    os.remove('small_converted.fits')
