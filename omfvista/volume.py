"""Methods for converting volumetric data objects"""

__all__ = [
    'get_volume_shape',
    'volume_grid_geom_to_vtk',
    'volume_to_vtk',
]

__displayname__ = 'Volume'

import vtk
from vtk.util import numpy_support as nps
import pyvista

from omfvista.utilities import check_orientation, check_orthogonal

import numpy as np


def get_volume_shape(vol):
    """Returns the shape of a gridded volume"""
    return ( len(vol.tensor_u), len(vol.tensor_v), len(vol.tensor_w))


def volume_grid_geom_to_vtk(volgridgeom):
    """Convert the 3D gridded volume to a :class:`pyvista.StructuredGrid`
    (or a :class:`pyvista.RectilinearGrid` when apprropriate) object contatining
    the 2D surface.

    Args:
        volgridgeom (:class:`omf.volume.VolumeGridGeometry`): the grid geometry
            to convert
    """
    volgridgeom._validate_mesh()

    ox, oy, oz = volgridgeom.origin

    # Make coordinates along each axis
    x = ox + np.cumsum(volgridgeom.tensor_u)
    x = np.insert(x, 0, ox)
    y = oy + np.cumsum(volgridgeom.tensor_v)
    y = np.insert(y, 0, oy)
    z = oz + np.cumsum(volgridgeom.tensor_w)
    z = np.insert(z, 0, oz)

    # If axis orientations are standard then use a vtkRectilinearGrid
    if check_orientation(volgridgeom.axis_u, volgridgeom.axis_v, volgridgeom.axis_w):
        output = vtk.vtkRectilinearGrid()
        output.SetDimensions(len(x), len(y), len(z)) # note this subtracts 1
        output.SetXCoordinates(nps.numpy_to_vtk(num_array=x))
        output.SetYCoordinates(nps.numpy_to_vtk(num_array=y))
        output.SetZCoordinates(nps.numpy_to_vtk(num_array=z))
        return pyvista.wrap(output)

    # Otherwise use a vtkStructuredGrid
    output = vtk.vtkStructuredGrid()
    output.SetDimensions(len(x), len(y), len(z)) # note this subtracts 1

    # Build out all nodes in the mesh
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    points = np.c_[xx.ravel('F'), yy.ravel('F'), zz.ravel('F')]

    # Rotate the points based on the axis orientations
    rotation_mtx = np.array([volgridgeom.axis_u, volgridgeom.axis_v, volgridgeom.axis_w])
    points = points.dot(rotation_mtx)

    # Convert points to vtk object
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(len(points))
    pts.SetData(nps.numpy_to_vtk(points))
    # Now build the output
    output.SetPoints(pts)

    return pyvista.wrap(output)


def volume_to_vtk(volelement):
    """Convert the volume element to a VTK data object.

    Args:
        volelement (:class:`omf.volume.VolumeElement`): The volume element to
            convert

    """
    output = volume_grid_geom_to_vtk(volelement.geometry)
    shp = get_volume_shape(volelement.geometry)
    # Add data to output
    for data in volelement.data:
        arr = data.array.array
        arr = np.reshape(arr, shp).flatten(order='F')
        c = nps.numpy_to_vtk(num_array=arr, deep=True)
        c.SetName(data.name)
        loc = data.location
        if loc == 'vertices':
            output.GetPointData().AddArray(c)
        else:
            output.GetCellData().AddArray(c)
    return pyvista.wrap(output)


# Now set up the display names for the docs
volume_to_vtk.__displayname__ = 'Volume to VTK'
volume_grid_geom_to_vtk.__displayname__ = 'Volume Grid Geometry to VTK'
get_volume_shape.__displayname__ = 'Volume Shape'
