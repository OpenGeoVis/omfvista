"""``omfvista``: 3D visualization for the Open Mining Format (omf)
"""

from omfvista.lineset import line_set_to_vtk
from omfvista.pointset import point_set_to_vtk
from omfvista.surface import surface_geom_to_vtk, surface_grid_geom_to_vtk, surface_to_vtk
from omfvista.utilities import (
    add_data,
    add_texture_coordinates,
    check_orientation,
    check_orthogonal,
    texture_to_vtk,
)
from omfvista.volume import volume_grid_geom_to_vtk, volume_to_vtk
from omfvista.wrapper import load_project, project_to_vtk, wrap

# Package meta data
__author__ = "Bane Sullivan"
__license__ = "BSD-3-Clause"
__copyright__ = "2019-2022, Bane Sullivan"
__version__ = "0.3.1"
__displayname__ = "OMF-VTK"
__name__ = "omfvista"


def ignore_warnings():
    """Sets a warning filter for pillow's annoying ``DecompressionBombWarning``"""
    import warnings

    from PIL import Image

    warnings.simplefilter(action="ignore", category=Image.DecompressionBombWarning)


ignore_warnings()


def download_forge_example(load_textures=True):
    """Download and load the FORGE geothermal prroject data."""
    from pyvista import examples

    print("Downloading FORGE data... Please be patient.")
    filename, _ = examples.downloads._download_file("FORGE.omf")
    print("FORGE Data Downloaded!")
    return load_project(filename, load_textures=load_textures)
