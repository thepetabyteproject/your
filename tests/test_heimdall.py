import your
from your.utils.heimdall import *


def test_dm_list():
    _install_dir = os.path.abspath(os.path.dirname(__file__))
    fil_file = os.path.join(_install_dir, 'data/28.fil')
    y = your.Your(fil_file)
    dm_list = generate_dm_list(dm_start=0, dm_end=1000, dt=y.your_header.tsamp, f0=y.your_header.fch1,
                               df=y.your_header.foff, ti=40e-6,
                               nchans=y.your_header.nchans, tol=1.25)
    assert len(dm_list) == 208
