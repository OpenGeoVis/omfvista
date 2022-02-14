"""``omfvista``: 3D visualization for the Open Mining Format (omf)
"""

import setuptools
import os
import sys
import platform
import warnings

__version__ = '0.2.4'

with open("README.rst", "r") as f:
    long_description = f.read()

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
    install_requires=[
        'omf>=1.0.0',
        'vectormath>=0.2.2',
        'pyvista>=0.20.1',
        'numpy',
        'matplotlib',
    ],
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Natural Language :: English',
    ),
)
