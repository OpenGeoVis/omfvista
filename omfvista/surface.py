"""Methods to convert surface objects to VTK data objects"""


__all__ = [
    'surface_geom_to_vtk',
    'surface_grid_geom_to_vtk',
    'surface_to_vtk',
]

__displayname__ = 'Surface'

import vtk
from vtk.util import numpy_support as nps
import pyvista
import omf


import numpy as np

from omfvista.utilities import check_orientation, check_orthogonal
from omfvista.utilities import add_data, add_textures

def surface_geom_to_vtk(surfgeom):
    """Convert the triangulated surface to a :class:`pyvista.UnstructuredGrid`
    object

    Args:
        surfgeom (:class:`omf.surface.SurfaceGeometry`): the surface geomotry to
            convert
    """

    output = vtk.vtkUnstructuredGrid()
    pts = vtk.vtkPoints()
    cells = vtk.vtkCellArray()

    # Generate the points
    pts.SetNumberOfPoints(surfgeom.num_nodes)
    pts.SetData(nps.numpy_to_vtk(surfgeom.vertices))

    # Generate the triangle cells
    cellConn = surfgeom.triangles.array
    cellsMat = np.concatenate(
        (np.ones((cellConn.shape[0], 1), dtype=np.int64)*cellConn.shape[1], cellConn),
        axis=1).ravel()
    cells = vtk.vtkCellArray()
    cells.SetNumberOfCells(cellConn.shape[0])
    cells.SetCells(cellConn.shape[0],
            nps.numpy_to_vtk(cellsMat, deep=True, array_type=vtk.VTK_ID_TYPE))

    # Add to output
    output.SetPoints(pts)
    output.SetCells(vtk.VTK_TRIANGLE, cells)
    return pyvista.wrap(output)


def surface_grid_geom_to_vtk(surfgridgeom):
    """Convert the 2D grid to a :class:`pyvista.StructuredGrid` object.

    Args:
        surfgridgeom (:class:`omf.surface.SurfaceGridGeometry`): the surface
            grid geometry to convert

    """
    surfgridgeom._validate_mesh()

    output = vtk.vtkStructuredGrid()

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

    output.SetDimensions(len(x), len(y), len(z))

    # Build out all nodes in the mesh
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    xx, yy, zz, = xx.ravel('F'), yy.ravel('F'), zz.ravel('F')
    zz += surfgridgeom.offset_w
    points = np.c_[xx, yy, zz]

    # Rotate the points based on the axis orientations
    points = points.dot(rotation_mtx)

    # Convert points to vtk object
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(len(points))
    pts.SetData(nps.numpy_to_vtk(points))
    # Now build the output
    output.SetPoints(pts)

    return pyvista.wrap(output)

def surface_to_vtk(surfel):
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

    output = builder(geom)

    # Now add point data:
    add_data(output, surfel.data)

    add_textures(output, surfel.textures, surfel.name)

    return output


surface_to_vtk.__displayname__ = 'Surface to VTK'
surface_grid_geom_to_vtk.__displayname__ = 'Surface Grid Geometry to VTK'
surface_geom_to_vtk.__displayname__ = 'Surface Geometry to VTK'
