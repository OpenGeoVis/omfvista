omfvtk
======

.. image:: https://readthedocs.org/projects/omfvtk/badge/?version=latest
   :target: https://omfvtk.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/omfvtk.svg
   :target: https://pypi.org/project/omfvtk/
   :alt: PyPI

.. image:: https://travis-ci.org/OpenGeoVis/omfvtk.svg?branch=master
   :target: https://travis-ci.org/OpenGeoVis/omfvtk
   :alt: Build Status

.. image:: https://img.shields.io/github/stars/OpenGeoVis/omfvtk.svg?style=social&label=Stars
   :target: https://github.com/OpenGeoVis/omfvtk
   :alt: GitHub


A VTK interface for the `Open Mining Format package`_ (``omf``).

.. _Open Mining Format package: https://omf.readthedocs.io/en/latest/

Example Use
-----------

Use the wraper provided in ``omfvtk`` to wrap any ``omf`` data object:

.. code-block:: python

    import omfvtk

    omfvtk.wrap(data)


Here's an example using the sample data hosted in the `OMF repository`_.

.. _OMF repository: https://github.com/gmggroup/omf/tree/master/assets

.. code-block:: python

    import omf
    import omfvtk

    # Read all elements
    reader = omf.OMFReader('test_file.omf')
    project = reader.get_project()

    # Iterate over the elements and add converted VTK objects to dictionary:
    data = dict()
    for e in project.elements:
        d = omfvtk.wrap(e)
        data[e.name] = d

Or better yet, just use the project loader:

.. code-block:: python

    import omfvtk
    data = omfvtk.load_project('test_file.omf')

See ``omfvtk`` in Action
^^^^^^^^^^^^^^^^^^^^^^^^

Be sure to check out the `Example Notebook`_ that demos ``omfvtk``!

.. _Example Notebook: https://github.com/OpenGeoVis/omfvtk/blob/master/Example.ipynb


Credits
-------

This package was created with `Cookiecutter`_ and the `banesullivan/cookiecutter-gendocs`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`banesullivan/cookiecutter-gendocs`: https://github.com/banesullivan/cookiecutter-gendocs
