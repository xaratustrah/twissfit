# PyPI setup file
# thanks to https://stackoverflow.com/a/23265673/5177935
#

from setuptools import setup, find_packages
from twissfit.version import __version__

long_description = ''

try:
    from pypandoc import convert

    def read_md(f): return convert(f, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f): return open(f, 'r').read()

classifiers = [
    'Environment :: Console',
    'Programming Language :: Python',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Physics'
]

setup(
    name='twissfit',
    packages=find_packages(),
    version=__version__,
    description='Collection of tools for dealing with in phase / quadrature time series data.',
    long_description=read_md('README.md'),
    author='Xaratustrah',
    url='https://github.com/xaratustrah/twissfit',  # use the URL to the github repo
    download_url='https://github.com/xaratustrah/twissfit/tarball/{}'.format(
        __version__),
    entry_points={
        'console_scripts': [
            'twissfit = twissfit.__main__:main'
        ]
    },
    license='GPLv3',
    keywords=['physics', 'data', 'accelerator', ],  # arbitrary keywords
    classifiers=classifiers
)
