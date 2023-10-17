"""This module provides a wrapper that will work for any OMF data object or
project files.

Example Use
-----------

Use the wrapper provided in ``omfvista`` to wrap any ``omf`` data object:

.. code-block:: python

    import omfvista

    omfvista.wrap(data)


Here's an example using the sample data hosted in the `OMF repository`_.

.. _OMF repository: https://github.com/gmggroup/omf/tree/master/assets

.. code-block:: python

    import omf
    import omfvista

    # Read all elements
    reader = omf.OMFReader('test_file.omf')
    project = reader.get_project()

    # Iterate over the elements and add converted VTK objects to dictionary:
    data = dict()
    for e in project.elements:
        d = omfvista.wrap(e)
        data[e.name] = d

Or better yet, just use the project loader:

.. code-block:: python

    import omfvista
    data = omfvista.load_project('test_file.omf')

"""


__all__ = [
    "wrap",
    "project_to_vtk",
    "load_project",
]

__displayname__ = "Wrapper"

import numpy as np
import omf
import pyvista

import omfvista
from omfvista.lineset import line_set_to_vtk
from omfvista.pointset import point_set_to_vtk
from omfvista.surface import surface_geom_to_vtk, surface_grid_geom_to_vtk, surface_to_vtk
from omfvista.utilities import get_textures, texture_to_vtk
from omfvista.volume import volume_grid_geom_to_vtk, volume_to_vtk


def wrap(data, origin=(0.0, 0.0, 0.0)):
    """Wraps the OMF data object/project as a VTK data object. This is the
    primary function that an end user will harness.

    Args:
        data: any OMF data object

    Example:
        >>> import omf
        >>> import omfvista

        >>> # Read all elements
        >>> reader = omf.OMFReader('test_file.omf')
        >>> project = reader.get_project()

        >>> # Iterate over the elements and add converted VTK objects to dictionary:
        >>> data = dict()
        >>> for e in project.elements:
        >>>     d = omfvista.wrap(e)
        >>>     data[e.name] = d

    """
    # Allow recursion
    if isinstance(data, (list, tuple)):
        multi = pyvista.MultiBlock()
        for i, item in enumerate(data):
            multi.append(wrap(item))
            multi.set_block_name(i, item.name)
        return multi
    # get the class name
    key = data.__class__.__name__
    try:
        if key != "Project":
            return WRAPPERS[key](data, origin=origin)
        else:
            # Project is a special case
            return WRAPPERS[key](data)
    except KeyError:
        raise RuntimeError("Data of type ({}) is not supported currently.".format(key))


def project_to_vtk(project, load_textures=False):
    """Converts an OMF project (:class:`omf.base.Project`) to a
    :class:`pyvista.MultiBlock` data boject
    """
    # Iterate over the elements and add converted VTK objects a MultiBlock
    data = pyvista.MultiBlock()
    textures = {}
    origin = np.array(project.origin)
    for e in project.elements:
        d = omfvista.wrap(e, origin=origin)
        data[e.name] = d
        if hasattr(e, "textures") and e.textures:
            textures[e.name] = get_textures(e)
    if load_textures:
        return data, textures
    return data


def load_project(filename, load_textures=False):
    """Loads an OMF project file into a :class:`pyvista.MultiBlock` dataset"""
    reader = omf.OMFReader(filename)
    project = reader.get_project()
    return project_to_vtk(project, load_textures=load_textures)


WRAPPERS = {
    "LineSetElement": line_set_to_vtk,
    "PointSetElement": point_set_to_vtk,
    # Surfaces
    "SurfaceGeometry": surface_geom_to_vtk,
    "SurfaceGridGeometry": surface_grid_geom_to_vtk,
    "SurfaceElement": surface_to_vtk,
    "ImageTexture": texture_to_vtk,
    # Volumes
    "VolumeGridGeometry": volume_grid_geom_to_vtk,
    "VolumeElement": volume_to_vtk,
    "Project": project_to_vtk,
}


# Now set up the display names for the docs
load_project.__displayname__ = "Load Project File"
project_to_vtk.__displayname__ = "Project to VTK"
wrap.__displayname__ = "The Wrapper"
