"""This module provides a wrapper that will work for any OMF data object
"""


__all__ = [
    'wrap',
]

import omfvtk


def wrap(data):
    """Wraps the OMF data object/project as a VTK data object"""
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
