"""Methods to convert surface objects to VTK data objects"""


__all__ = [
    'surface_geom_to_vtk',
    'surface_grid_geom_to_vtk',
    'surface_to_vtk',
]

import vtk
from vtk.util import numpy_support as nps
import vtki

import numpy as np

def surface_geom_to_vtk(surfgeom):
    """Convert the triangulated surface to a ``vtkUnstructuredGrid`` object

    Args:
        surfgeom (SurfaceGeometry): the surface geomotry to convert
    """

    output = vtk.vtkUnstructuredGrid()
    pts = vtk.vtkPoints()
    cells = vtk.vtkCellArray()

    # Generate the points
    pts.SetNumberOfPoints(surfgeom.num_nodes)
    pts.SetData(nps.numpy_to_vtk(surfgeom.vertices))

    # Generate the triangle cells
    cellConn = surfgeom.triangles.array
    cellsMat = np.concatenate((np.ones((cellConn.shape[0], 1), dtype=np.int64)*cellConn.shape[1], cellConn), axis=1).ravel()
    cells = vtk.vtkCellArray()
    cells.SetNumberOfCells(cellConn.shape[0])
    cells.SetCells(cellConn.shape[0], nps.numpy_to_vtk(cellsMat, deep=True, array_type=vtk.VTK_ID_TYPE))

    # Add to output
    output.SetPoints(pts)
    output.SetCells(vtk.VTK_TRIANGLE, cells)
    return vtki.wrap(output)


def surface_grid_geom_to_vtk(surfgridgeom):
    """Convert the 2D grid to a ``vtkStructuredGrid`` object.

    Args:
        surfgridgeom (SurfaceGridGeometry): the surface grid geometry to convert

    """

    output = vtk.vtkStructuredGrid()

    # TODO: build!
    # Build out all nodes in the mesh

    # Add to output

    return vtki.wrap(output)

def surface_to_vtk(surfel):
    """Convert the surface to a its appropriate VTK data object type.

    Args:
        surfel (SurfaceElement): the surface element to convert
    """

    output = surface_geom_to_vtk(surfel.geometry)

    # TODO: handle textures

    # Now add point data:
    for data in surfel.data:
        arr = data.array.array
        c = nps.numpy_to_vtk(num_array=arr)
        c.SetName(data.name)
        output.GetPointData().AddArray(c)

    return vtki.wrap(output)
