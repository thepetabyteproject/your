from your import Your
from your.utils.plotter import *

os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
_install_dir = os.path.abspath(os.path.dirname(__file__))


def test_save_bandpass():
    fil_file = os.path.join(_install_dir, "data/28.fil")
    y = Your(fil_file)
    bandpass = y.bandpass()
    mask = np.zeros_like(bandpass, dtype=np.bool_)
    mask[:10] = True
    save_bandpass(y, bandpass, outname="28_bp.png")
    assert os.path.isfile("28_bp.png")
    os.remove("28_bp.png")
    save_bandpass(y, bandpass, mask=mask)
    assert os.path.isfile("28_bandpass.png")
    os.remove("28_bandpass.png")


def test_plot_h5():
    h5_file = os.path.join(_install_dir, "data/test.h5")
    plot_h5(h5_file, publication=False, outdir=os.path.join(_install_dir, "data/"))
    png_file = os.path.join(_install_dir, "data/test.png")
    assert os.path.isfile(png_file)
    os.remove(png_file)

    plot_h5(h5_file, publication=True, mad_filter=True)
    png_file = os.path.join(_install_dir, "data/test.png")
    assert os.path.isfile(png_file)
    os.remove(png_file)
