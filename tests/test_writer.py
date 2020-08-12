from your.writer import Writer
from your import Your

import os
_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_to_fil():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    w.to_fil(nstart=0, nsamp=10, filfile='temp.fil', outdir='./')
    assert os.path.isfile('temp.fil')
    os.remove('temp.fil')

    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    w.to_fil(nstart=0, nsamp=10, filfile='temp.fil', outdir='./')
    assert os.path.isfile('temp.fil')
    os.remove('temp.fil')


def test_to_fits():
    file = os.path.join(_install_dir, 'data/small.fil')
    f = Your(file)
    w = Writer(f)
    w.to_fits(fitsfile='temp.fits', outdir='./')
    assert os.path.isfile('temp.fits')
    os.remove('temp.fits')

    file = os.path.join(_install_dir, 'data/small.fits')
    f = Your(file)
    w = Writer(f)
    w.to_fits(fitsfile='temp.fits', outdir='./')
    assert os.path.isfile('temp.fits')
    os.remove('temp.fits')

