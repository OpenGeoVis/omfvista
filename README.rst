OMF-VTK
=======

.. image:: https://readthedocs.org/projects/omfvtk/badge/?version=latest
   :target: https://omfvtk.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/omfvtk.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/omfvtk/
   :alt: PyPI

.. image:: https://img.shields.io/travis/OpenGeoVis/omfvtk/master.svg?label=build&logo=travis
   :target: https://travis-ci.org/OpenGeoVis/omfvtk
   :alt: Build Status

.. image:: https://img.shields.io/github/stars/OpenGeoVis/omfvtk.svg?style=social&label=Stars
   :target: https://github.com/OpenGeoVis/omfvtk
   :alt: GitHub


A VTK interface for the `Open Mining Format package`_ (``omf``).

.. _Open Mining Format package: https://omf.readthedocs.io/en/latest/

Example Use
-----------

Be sure to check out the `Example Notebook`_ that demos ``omfvtk``!
Here's an example using the sample data hosted in the `OMF repository`_.

.. _Example Notebook: https://github.com/OpenGeoVis/omfvtk/blob/master/Example.ipynb
.. _OMF repository: https://github.com/gmggroup/omf/tree/master/assets

.. code-block:: python

    >>> import vtki
    >>> import omfvtk

    >>> project = omfvtk.load_project('test_file.omf')
    >>> project

.. raw:: html

    <embed>
    <table><tr><th>Information</th><th>Blocks</th></tr><tr><td>
    <table>
    <tr><th>vtkMultiBlockDataSet</th><th>Values</th></tr>
    <tr><td>N Blocks</td><td>9</td></tr>
    <tr><td>X Bounds</td><td>443941.105, 447059.611</td></tr>
    <tr><td>Y Bounds</td><td>491941.536, 495059.859</td></tr>
    <tr><td>Z Bounds</td><td>2330.000, 3555.942</td></tr>
    </table>
    </td><td>
    <table>
    <tr><th>Index</th><th>Name</th><th>Type</th></tr>
    <tr><th>0</th><th>collar</th><th>vtkPolyData</th></tr>
    <tr><th>1</th><th>wolfpass_WP_assay</th><th>vtkPolyData</th></tr>
    <tr><th>2</th><th>Topography</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>3</th><th>Basement</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>4</th><th>Early Diorite</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>5</th><th>Intermineral diorite</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>6</th><th>Dacite</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>7</th><th>Cover</th><th>vtkUnstructuredGrid</th></tr>
    <tr><th>8</th><th>Block Model</th><th>vtkRectilinearGrid</th></tr>
    </table>
    </td></tr> </table>
    </embed>


Once the data is loaded as a `vtki.MultiBlock` dataset from ``omfvtk``, then
that object can be directly used for interactive 3D visualization from ``vtki``:

.. code-block:: python

    >>> project.plot(notebook=False)

Or an interactive scene can be created and manipulated to create a compelling
figure directly in a Jupyter notebook. First, grab the elements from the project:

.. code-block:: python

    # Grab a few elements of interest and plot em up!
    >>> vol = project['Block Model']
    >>> assay = project['wolfpass_WP_assay']
    >>> topo = project['Topography']
    >>> dacite = project['Dacite']

Then apply a filtering tool from `vtki` to the volumetric data:

.. code-block:: python

    >>> thresher = vtki.Threshold(vol)

.. figure:: https://github.com/OpenGeoVis/omfvtk/blob/master/threshold.gif

Then you can put it all in one environment!

.. code-block:: python

    >>> p = vtki.BackgroundPlotter()#Plotter(notebook=False)


    >>> p.add_mesh(topo, colormap='gist_earth', showedges=False, opacity=0.5)
    >>> p.add_mesh(assay, color='blue', linethick=3)
    >>> p.add_mesh(thresher.output_dataset, showedges=False, rng=vol.get_data_range(), colormap='jet')
    >>> p.add_mesh(dacite, showedges=False, color='yellow', opacity=0.6)

    >>> p.add_bounds_axes(topo)

And once you like what the render view displays, you can save a screenshot:

.. code-block:: python

    >>> p.screenshot('wolfpass.png')

.. image:: https://github.com/OpenGeoVis/omfvtk/blob/master/wolfpass.png
