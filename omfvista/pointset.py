"""Methods to convert point set objects to VTK data objects"""


__all__ = [
    'point_set_to_vtk',
]

__displayname__ = 'Point Set'

import numpy as np
import pyvista

from omfvista.utilities import add_data, add_textures


def point_set_to_vtk(pse, origin=(0.0, 0.0, 0.0)):
    """Convert the point set to a :class:`pyvista.PolyData` data object.

    Args:
        pse (:class:`omf.pointset.PointSetElement`): The point set to convert

    Return:
        :class:`pyvista.PolyData`
    """
    points = np.array(pse.geometry.vertices)
    output = pyvista.PolyData(points)

    # Now add point data:
    add_data(output, pse.data)

    add_textures(output, pse.textures, pse.name)

    output.points += np.array(origin)
    return output


point_set_to_vtk.__displayname__ = 'Point Set to VTK'
