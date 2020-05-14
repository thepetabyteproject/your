import glob

from setuptools import setup, find_packages

setup(
    name='your',
    version='0.4.9',
    packages=find_packages(),
    url='http://github.com/devanshkv/your',
    author='Devansh Agarwal, Kshitij Aggarwal',
    scripts=glob.glob('bin/*'),
    setup_requires=['numpy'],
    install_requires=['h5py', 'scikit-image', 'scipy', 'numba', 'astropy', 'Cython'],
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