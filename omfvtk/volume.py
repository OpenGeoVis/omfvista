"""Methods for converting volumetric data objects"""

__all__ = [
    'get_volume_shape',
    'volume_grid_geom_to_vtk',
    'volume_to_vtk',
]

import vtk
from vtk.util import numpy_support as nps
import vtki

import numpy as np


def get_volume_shape(vol):
    return ( len(vol.tensor_u), len(vol.tensor_v), len(vol.tensor_w))


def volume_grid_geom_to_vtk(volgridgeom):
    """Convert the 3D gridded volume to a ``vtkStructuredGrid``
    (or a ``vtkRectilinearGrid`` when apprropriate) object contatining the
    2D surface.

    Args:
        volgridgeom (VolumeGridGeometry): the grid geom to convert
    """
    volgridgeom._validate_mesh()

    ox, oy, oz = volgridgeom.origin

    def checkOrientation():
        if np.allclose(volgridgeom.axis_u, (1, 0, 0)) and np.allclose(volgridgeom.axis_v, (0, 1, 0)) and np.allclose(volgridgeom.axis_w, (0, 0, 1)):
            return True
        return False

    def rotationMatrix():
        # TODO: is this correct?
        return np.array([volgridgeom.axis_u, volgridgeom.axis_v, volgridgeom.axis_w])

    # Make coordinates along each axis
    x = ox + np.cumsum(volgridgeom.tensor_u)
    x = np.insert(x, 0, ox)
    y = oy + np.cumsum(volgridgeom.tensor_v)
    y = np.insert(y, 0, oy)
    z = oz + np.cumsum(volgridgeom.tensor_w)
    z = np.insert(z, 0, oz)

    # If axis orientations are standard then use a vtkRectilinearGrid
    if checkOrientation():
        output = vtk.vtkRectilinearGrid()
        output.SetDimensions(len(x), len(y), len(z)) # note this subtracts 1
        output.SetXCoordinates(nps.numpy_to_vtk(num_array=x))
        output.SetYCoordinates(nps.numpy_to_vtk(num_array=y))
        output.SetZCoordinates(nps.numpy_to_vtk(num_array=z))
        return vtki.wrap(output)

    # Otherwise use a vtkStructuredGrid
    output = vtk.vtkStructuredGrid()
    output.SetDimensions(len(x), len(y), len(z)) # note this subtracts 1

    # Build out all nodes in the mesh
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    points = np.stack((xx.flatten(), yy.flatten(), zz.flatten())).T

    # Rotate the points based on the axis orientations
    rmtx = rotationMatrix()
    points = points.dot(rmtx)

    # Convert points to vtk object
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(len(points))
    pts.SetData(nps.numpy_to_vtk(points))
    # Now build the output
    output.SetPoints(pts)

    return vtki.wrap(output)


def volume_to_vtk(volelement):
    """Convert the volume element to a VTK data object.

    Args:
        volelement (VolumeElement): The volume ele"""
    output = volume_grid_geom_to_vtk(volelement.geometry)
    shp = get_volume_shape(volelement.geometry)
    # Add data to output
    for data in volelement.data:
        arr = data.array.array
        arr = np.reshape(arr, shp).flatten(order='F')
        c = nps.numpy_to_vtk(num_array=arr, deep=True)
        c.SetName(data.name)
        output.GetCellData().AddArray(c)
    return vtki.wrap(output)
