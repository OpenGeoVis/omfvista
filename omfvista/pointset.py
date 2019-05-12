"""Methods to convert point set objects to VTK data objects"""


__all__ = [
    'point_set_to_vtk',
]

__displayname__ = 'Point Set'

import vtk
from vtk.util import numpy_support as nps
import pyvista

import numpy as np

from omfvista.utilities import add_data, add_textures


def point_set_to_vtk(pse):
    """Convert the point set to a :class:`pyvista.PolyData` data object.

    Args:
        pse (:class:`omf.pointset.PointSetElement`): The point set to convert

    Return:
        :class:`pyvista.PolyData`
    """

    points = pse.geometry.vertices
    npoints = pse.geometry.num_nodes

    # Make VTK cells array
    cells = np.hstack((np.ones((npoints, 1)),
                       np.arange(npoints).reshape(-1, 1)))
    cells = np.ascontiguousarray(cells, dtype=np.int64)
    cells = np.reshape(cells, (2*npoints))
    vtkcells = vtk.vtkCellArray()
    vtkcells.SetCells(npoints, nps.numpy_to_vtk(cells, deep=True, array_type=vtk.VTK_ID_TYPE))

    # Convert points to vtk object
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(pse.geometry.num_nodes)
    pts.SetData(nps.numpy_to_vtk(points))

    # Create polydata
    output = vtk.vtkPolyData()
    output.SetPoints(pts)
    output.SetVerts(vtkcells)

    # Now add point data:
    add_data(output, pse.data)

    add_textures(output, pse.textures, pse.name)

    return pyvista.wrap(output)


point_set_to_vtk.__displayname__ = 'Point Set to VTK'
