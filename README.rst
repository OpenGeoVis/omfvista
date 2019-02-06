OMF-VTK
=======

.. image:: https://img.shields.io/readthedocs/omfvtk.svg?logo=read%20the%20docs&logoColor=white
   :target: https://omfvtk.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/omfvtk.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/omfvtk/
   :alt: PyPI

.. image:: https://img.shields.io/travis/OpenGeoVis/omfvtk/master.svg?label=build&logo=travis
   :target: https://travis-ci.org/OpenGeoVis/omfvtk
   :alt: Build Status Linux

.. image:: https://ci.appveyor.com/api/projects/status/y1sbh707jpl8375u?svg=true
   :target: https://ci.appveyor.com/project/banesullivan/omfvtk
   :alt: Build Status Windows

.. image:: https://codecov.io/gh/OpenGeoVis/omfvtk/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/OpenGeoVis/omfvtk

.. image:: https://img.shields.io/github/stars/OpenGeoVis/omfvtk.svg?style=social&label=Stars
   :target: https://github.com/OpenGeoVis/omfvtk
   :alt: GitHub


A VTK interface for the `Open Mining Format package`_ (``omf``) providing
Python 3D visualization.

.. _Open Mining Format package: https://omf.readthedocs.io/en/latest/


Installation
------------

Installation is simply::

    pip install omfvtk

All necessary dependencies will be installed alongside ``omfvtk``. Please
note that this package heavily leverages the vtki_ package.

.. _vtki: https://github.com/akaszynski/vtki


Example Use
-----------

Be sure to check out the `Example Notebook`_ that demos ``omfvtk``!
Here's an example using the sample data hosted in the `OMF repository`_.

.. _Example Notebook: https://github.com/OpenGeoVis/omfvtk/blob/master/Example.ipynb
.. _OMF repository: https://github.com/gmggroup/omf/tree/master/assets

.. code-block:: python

    import vtki
    import omfvtk

    project = omfvtk.load_project('test_file.omf')
    project

.. image:: https://github.com/OpenGeoVis/omfvtk/raw/master/assets/table-repr.png
   :alt: Table Representation


Once the data is loaded as a ``vtki.MultiBlock`` dataset from ``omfvtk``, then
that object can be directly used for interactive 3D visualization from ``vtki``:

.. code-block:: python

    project.plot(notebook=False)

Or an interactive scene can be created and manipulated to create a compelling
figure directly in a Jupyter notebook. First, grab the elements from the project:

.. code-block:: python

    # Grab a few elements of interest and plot em up!
    vol = project['Block Model']
    assay = project['wolfpass_WP_assay']
    topo = project['Topography']
    dacite = project['Dacite']

Then apply a filtering tool from ``vtki`` to the volumetric data:

.. code-block:: python

    thresher = vtki.Threshold(vol, display_params={'show_edges':False})

.. figure:: https://github.com/OpenGeoVis/omfvtk/raw/master/assets/threshold.gif
   :alt: IPython Thresholding Tool

Then you can put it all in one environment!

.. code-block:: python

    # Grab the active plotting window
    #  from the thresher tool
    p = thresher.plotter
    # Add our datasets
    p.add_mesh(topo, cmap='gist_earth', show_edges=False, opacity=0.5)
    p.add_mesh(assay, color='blue', line_width=3)
    p.add_mesh(dacite, show_edges=False, color='yellow', opacity=0.6)
    # Add the bounds axis
    p.add_bounds_axes()


.. figure:: https://github.com/OpenGeoVis/omfvtk/raw/master/assets/interactive.gif
   :alt: Interactive Rendering


And once you like what the render view displays, you can save a screenshot:

.. code-block:: python

    p.screenshot('wolfpass.png')

.. image:: https://github.com/OpenGeoVis/omfvtk/raw/master/wolfpass.png
   :alt: Wolf Pass Screenshot
