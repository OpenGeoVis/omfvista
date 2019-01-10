"""Methods to convert point set objects to VTK data objects"""


__all__ = [
    'point_set_to_vtk',
]

import vtk
from vtk.util import numpy_support as nps
import vtki

import numpy as np


def point_set_to_vtk(pse):
    """Convert the point set to a ``vtkPloyData`` data object.

    Args:
        pse (PointSetElement): The point set to convert

    Return:
        vtki.PolyData
    """

    points = pse.geometry.vertices
    npoints = pse.geometry.num_nodes

    # Make VTK cells array
    cells = np.hstack((np.ones((npoints, 1)),
                       np.arange(npoints).reshape(-1, 1)))
    cells = np.ascontiguousarray(cells, dtype=np.int64)
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

    # TODO: handle textures

    # Now add point data:
    for data in pse.data:
        arr = data.array.array
        c = nps.numpy_to_vtk(num_array=arr)
        c.SetName(data.name)
        output.GetPointData().AddArray(c)

    return vtki.wrap(output)
