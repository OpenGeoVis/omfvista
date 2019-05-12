OMF-VTK
=======

.. image:: https://img.shields.io/readthedocs/omfvista.svg?logo=read%20the%20docs&logoColor=white
   :target: https://omfvista.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/omfvista.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/omfvista/
   :alt: PyPI

.. image:: https://img.shields.io/travis/OpenGeoVis/omfvista/master.svg?label=build&logo=travis
   :target: https://travis-ci.org/OpenGeoVis/omfvista
   :alt: Build Status Linux

.. image:: https://ci.appveyor.com/api/projects/status/y1sbh707jpl8375u?svg=true
   :target: https://ci.appveyor.com/project/banesullivan/omfvista
   :alt: Build Status Windows

.. image:: https://codecov.io/gh/OpenGeoVis/omfvista/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/OpenGeoVis/omfvista

.. image:: https://img.shields.io/github/stars/OpenGeoVis/omfvista.svg?style=social&label=Stars
   :target: https://github.com/OpenGeoVis/omfvista
   :alt: GitHub


A VTK interface for the `Open Mining Format package`_ (``omf``) providing
Python 3D visualization.

.. _Open Mining Format package: https://omf.readthedocs.io/en/latest/


Installation
------------

Installation is simply::

    pip install omfvista

All necessary dependencies will be installed alongside ``omfvista``. Please
note that this package heavily leverages the pyvista_ package.

.. _pyvista: https://github.com/pyvista/pyvista


Questions & Support
-------------------

For general use questions, please join `@OpenGeoVis`_ on our `Slack workspace`_
under the ``#omfvista`` channel. To inquire with the creators of ``omfvista``,
please email `info@opengeovis.org`_.

.. _@OpenGeoVis: https://github.com/OpenGeoVis
.. _Slack workspace: http://slack.opengeovis.org
.. _info@opengeovis.org: mailto:info@opengeovis.org

Example Use
-----------

Be sure to check out the `Example Notebook`_ that demos ``omfvista``!
Here's an example using the sample data hosted in the `OMF repository`_.

.. _Example Notebook: https://github.com/OpenGeoVis/omfvista/blob/master/Example.ipynb
.. _OMF repository: https://github.com/gmggroup/omf/tree/master/assets

.. code-block:: python

    import pyvista
    import omfvista

    project = omfvista.load_project('test_file.omf')
    project

.. image:: https://github.com/OpenGeoVis/omfvista/raw/master/assets/table-repr.png
   :alt: Table Representation


Once the data is loaded as a ``pyvista.MultiBlock`` dataset from ``omfvista``, then
that object can be directly used for interactive 3D visualization from ``pyvista``:

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

Then apply a filtering tool from ``pyvista`` to the volumetric data:

.. code-block:: python

    thresher = pyvista.Threshold(vol)

.. figure:: https://github.com/OpenGeoVis/omfvista/raw/master/assets/threshold.gif
   :alt: IPython Thresholding Tool

Then you can put it all in one environment!

.. code-block:: python

    # Grab the active plotting window
    #  from the thresher tool
    p = thresher.plotter
    # Add our datasets
    p.add_mesh(topo, cmap='gist_earth', opacity=0.5)
    p.add_mesh(assay, color='blue', line_width=3)
    p.add_mesh(dacite, color='yellow', opacity=0.6)
    # Add the bounds axis
    p.show_bounds()


.. figure:: https://github.com/OpenGeoVis/omfvista/raw/master/assets/interactive.gif
   :alt: Interactive Rendering


And once you like what the render view displays, you can save a screenshot:

.. code-block:: python

    p.screenshot('wolfpass.png')

.. image:: https://github.com/OpenGeoVis/omfvista/raw/master/wolfpass.png
   :alt: Wolf Pass Screenshot
