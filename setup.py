import glob

from setuptools import setup

setup(
    name='your',
    version='0.4.1',
    packages=['your'],
    url='http://github.com/devanshkv/your',
    author='Devansh Agarwal, Kshitij Aggarwal',
    scripts=glob.glob('bin/*'),
    package_dir={'your': 'your'},
    install_requires=['numpy', 'h5py', 'scikit-image', 'scipy', 'numba', 'astropy', 'Cython'],
    tests_require=['pytest'],
    author_email='da0017@mix.wvu.edu, ka0064@mix.wvu.edu',
    zip_safe=False,
    description='A unified reader for sigproc filterbank and psrfits data',
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Astronomy']
)
