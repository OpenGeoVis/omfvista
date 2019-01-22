"""This module provides a wrapper that will work for any OMF data object or
project files.

Example Use
-----------

Use the wrapper provided in ``omfvtk`` to wrap any ``omf`` data object:

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

"""


__all__ = [
    'wrap',
    'project_to_vtk',
    'load_project',
]

__displayname__ = 'Wrapper'

import omf
import omfvtk
import vtki


def wrap(data):
    """Wraps the OMF data object/project as a VTK data object. This is the
    primary function that an end user will harness.

    Args:
        data: any OMF data object

    Example:
        >>> import omf
        >>> import omfvtk

        >>> # Read all elements
        >>> reader = omf.OMFReader('test_file.omf')
        >>> project = reader.get_project()

        >>> # Iterate over the elements and add converted VTK objects to dictionary:
        >>> data = dict()
        >>> for e in project.elements:
        >>>     d = omfvtk.wrap(e)
        >>>     data[e.name] = d

    """
    # Allow recursion
    if isinstance(data, (list, tuple)):
        multi = vtki.MultiBlock()
        for i, item in enumerate(data):
            multi.append(wrap(item))
            multi.set_block_name(i, item.name)
        return multi
    # Define wrappers
    wrappers = {
        'LineSetElement': omfvtk.line_set_to_vtk,
        'PointSetElement': omfvtk.point_set_to_vtk,
        # Surfaces
        'SurfaceGeometry': omfvtk.surface_geom_to_vtk,
        'SurfaceGridGeometry': omfvtk.surface_grid_geom_to_vtk,
        'SurfaceElement': omfvtk.surface_to_vtk,
        # Volumes
        'VolumeGridGeometry': omfvtk.volume_grid_geom_to_vtk,
        'VolumeElement': omfvtk.volume_to_vtk,
        'Project': omfvtk.project_to_vtk,
    }
    # get the class name
    key = data.__class__.__name__
    try:
        return wrappers[key](data)
    except KeyError:
        raise RuntimeError('Data of type ({}) is not supported currently.'.format(key))


def project_to_vtk(project):
    """Converts an OMF project (:class:`omf.base.Project`) to a
    :class:`vtki.MultiBlock` data boject
    """
    # Iterate over the elements and add converted VTK objects a MultiBlock
    data = vtki.MultiBlock()
    for i, e in enumerate(project.elements):
        d = omfvtk.wrap(e)
        data[i, e.name] = d
    return data


def load_project(filename):
    """Loads an OMF project file into a :class:`vtki.MultiBlock` dataset"""
    reader = omf.OMFReader(filename)
    project = reader.get_project()
    return project_to_vtk(project)


# Now set up the display names for the docs
load_project.__displayname__ = 'Load Project File'
project_to_vtk.__displayname__ = 'Project to VTK'
wrap.__displayname__ = 'The Wrapper'
