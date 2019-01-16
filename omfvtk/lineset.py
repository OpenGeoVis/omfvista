"""Methods to convert line set objects to VTK data objects"""


__all__ = [
    'line_set_to_vtk',
]

__displayname__ = 'Line Set'

import vtk
from vtk.util import numpy_support as nps
import vtki

import numpy as np

def line_set_to_vtk(lse):
    """Convert the line set to a :class:`vtki.PolyData` data object.

    Args:
        lse (:class:`omf.lineset.LineSetElement`): The line set to convert

    Return:
        :class:`vtki.PolyData`
    """

    output = vtk.vtkPolyData()
    cells = vtk.vtkCellArray()
    pts = vtk.vtkPoints()

    # Make a data array for grouping the line segments
    indexArr = vtk.vtkIntArray()
    indexArr.SetNumberOfValues(lse.geometry.num_cells)
    indexArr.SetName('Line Index')

    # Generate VTK Points from the vertices
    pts.SetNumberOfPoints(lse.geometry.num_nodes)
    pts.SetData(nps.numpy_to_vtk(lse.geometry.vertices))

    last = lse.geometry.segments[0][0]
    segi = 0
    for i in range(len(lse.geometry.segments)):
        # Create a VTK Line cell for each segment
        seg = lse.geometry.segments[i]
        aLine = vtk.vtkLine()
        aLine.GetPointIds().SetId(0, seg[0])
        aLine.GetPointIds().SetId(1, seg[1])
        cells.InsertNextCell(aLine)
        # Group segments by connectivity:
        if seg[0] != last:
            segi += 1
        last = seg[1]
        indexArr.SetValue(i, segi)

    # Generate the output
    output.SetPoints(pts)
    output.SetLines(cells)
    output.GetCellData().AddArray(indexArr)

    # Now add data to lines:
    for data in lse.data:
        arr = data.array.array
        c = nps.numpy_to_vtk(num_array=arr)
        c.SetName(data.name)
        output.GetCellData().AddArray(c)

    # TODO: if subtype is borehole make a tube

    return vtki.wrap(output)


line_set_to_vtk.__displayname__ = 'Line Set to VTK'
