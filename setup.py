"""``omfvtk``: A VTK interface for the Open Mining Format package
"""

import setuptools

__version__ = '0.0.0'

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="omfvtk",
    version=__version__,
    author="Bane Sullivan",
    author_email="info@pvgeo.org",
    description="A VTK interface for the Open Mining Format package",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/OpenGeoVis/omfvtk",
    packages=setuptools.find_packages(),
    install_requires=[
        'omf>=0.9.3',
        'vtki>=0.14.1',
        'numpy',
    ],
    classifiers=(
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Natural Language :: English',
    ),
)
