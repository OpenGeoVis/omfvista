"""Methods to convert surface objects to VTK data objects"""


__all__ = [
    'surface_geom_to_vtk',
    'surface_grid_geom_to_vtk',
    'surface_to_vtk',
]

__displayname__ = 'Surface'

import numpy as np
import omf
import pyvista

from omfvista.utilities import check_orientation, check_orthogonal
from omfvista.utilities import add_data, add_textures


def surface_geom_to_vtk(surfgeom, origin=(0.0, 0.0, 0.0)):
    """Convert the triangulated surface to a :class:`pyvista.PolyData`
    object

    Args:
        surfgeom (:class:`omf.surface.SurfaceGeometry`): the surface geomotry to
            convert
    """
    pts = np.array(surfgeom.vertices)
    tris = np.array(surfgeom.triangles.array)
    faces = np.c_[np.full(len(tris), 3), tris]
    output = pyvista.PolyData(pts, faces)
    output.points += np.array(origin)
    return output


def surface_grid_geom_to_vtk(surfgridgeom, origin=(0.0, 0.0, 0.0)):
    """Convert the 2D grid to a :class:`pyvista.StructuredGrid` object.

    Args:
        surfgridgeom (:class:`omf.surface.SurfaceGridGeometry`): the surface
            grid geometry to convert

    """
    surfgridgeom._validate_mesh()

    axis_u = np.array(surfgridgeom.axis_u)
    axis_v = np.array(surfgridgeom.axis_v)
    axis_w = np.cross(axis_u, axis_v)
    if not check_orthogonal(axis_u, axis_v, axis_w):
        raise ValueError('axis_u, axis_v, and axis_w must be orthogonal')
    rotation_mtx = np.array([axis_u, axis_v, axis_w])
    ox, oy, oz = surfgridgeom.origin

    # Make coordinates along each axis
    x = ox + np.cumsum(surfgridgeom.tensor_u)
    x = np.insert(x, 0, ox)
    y = oy + np.cumsum(surfgridgeom.tensor_v)
    y = np.insert(y, 0, oy)

    z = np.array([oz])

    # Build out all nodes in the mesh
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    xx, yy, zz, = xx.ravel('F'), yy.ravel('F'), zz.ravel('F')
    zz += surfgridgeom.offset_w
    points = np.c_[xx, yy, zz]

    # Rotate the points based on the axis orientations
    points = points.dot(rotation_mtx)

    # Now build the output
    output = pyvista.StructuredGrid()
    output.points = points
    output.dimensions = len(x), len(y), len(z)

    output.points += np.array(origin)
    return output


def surface_to_vtk(surfel, origin=(0.0, 0.0, 0.0)):
    """Convert the surface to a its appropriate VTK data object type.

    Args:
        surfel (:class:`omf.surface.SurfaceElement`): the surface element to
            convert
    """

    geom = surfel.geometry

    if isinstance(geom, omf.surface.SurfaceGeometry):
        builder = surface_geom_to_vtk
    elif isinstance(geom, omf.surface.SurfaceGridGeometry):
        builder = surface_grid_geom_to_vtk

    output = builder(geom, origin=origin)

    # Now add point data:
    add_data(output, surfel.data)

    add_textures(output, surfel.textures, surfel.name)

    return output


surface_to_vtk.__displayname__ = 'Surface to VTK'
surface_grid_geom_to_vtk.__displayname__ = 'Surface Grid Geometry to VTK'
surface_geom_to_vtk.__displayname__ = 'Surface Geometry to VTK'
