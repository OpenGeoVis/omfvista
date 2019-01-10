"""This module provides a wrapper that will work for any OMF data object
"""


__all__ = [
    'wrap',
    'load_project',
]

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
    }
    # get the class name
    key = data.__class__.__name__
    try:
        return wrappers[key](data)
    except KeyError:
        raise RuntimeError('Data of type ({}) is not supported currently.'.format(key))


def load_project(filename):
    """Loads an OMF project file into a vtki.MultiBlock dataset"""

    # Read all elements
    reader = omf.OMFReader(filename)
    project = reader.get_project()

    # Iterate over the elements and add converted VTK objects a MultiBlock
    data = vtki.MultiBlock()
    for i, e in enumerate(project.elements):
        d = omfvtk.wrap(e)
        data[i, e.name] = d

    return data
