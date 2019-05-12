"""``omfvista``: 3D visualization for the Open Mining Format (omf)
"""

import setuptools
import os
import sys
import platform
import warnings

__version__ = '0.2.0'

with open("README.rst", "r") as f:
    long_description = f.read()

# Manage requirements
install_requires = [
    'omf>=1.0.0',
    'vectormath>=0.2.0',
    'pyvista>=0.20.0',
    'numpy',
    'matplotlib',
]

# add vtk if not windows and (not Python 3.x or not x64)
if os.name == 'nt' and (int(sys.version[0]) < 3 or '64' not in platform.architecture()[0]):
    warnings.warn('\nYou will need to install VTK manually.' +
                  '  Try using Anaconda.  See:\n'
                  + 'https://anaconda.org/anaconda/vtk')
else:
    install_requires.append('vtk>=8.1.0')

setuptools.setup(
    name="omfvista",
    version=__version__,
    author="Bane Sullivan",
    author_email="info@pvgeo.org",
    description="3D visualization for the Open Mining Format (omf)",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/OpenGeoVis/omfvista",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Natural Language :: English',
    ),
)
