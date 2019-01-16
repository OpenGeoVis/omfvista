"""``omfvtk``: A VTK interface for the Open Mining Format package"""

from omfvtk.wrapper import wrap, load_project
from omfvtk.lineset import line_set_to_vtk
from omfvtk.pointset import point_set_to_vtk
from omfvtk.surface import surface_geom_to_vtk, surface_grid_geom_to_vtk, surface_to_vtk
from omfvtk.volume import volume_grid_geom_to_vtk, volume_to_vtk


# Package meta data
__author__ = 'Bane Sullivan'
__license__ = 'BSD-3-Clause'
__copyright__ = '2019, Bane Sullivan'
__version__ = '0.0.3'
__displayname__ = 'omfvtk'
__name__ = 'omfvtk'
