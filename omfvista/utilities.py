__all__ = [
    'check_orientation',
    'check_orthogonal',
    'add_data',
    'add_textures',
]


import numpy as np
import vtk
from vtk.util import numpy_support as nps
import pyvista
from PIL import Image


def check_orientation(axis_u, axis_v, axis_w):
    """This will check if the given ``axis_*`` vectors are the typical
    cartesian refernece frame (i.e. rectilinear).
    """
    if ( np.allclose(axis_u, (1, 0, 0)) and
         np.allclose(axis_v, (0, 1, 0)) and
         np.allclose(axis_w, (0, 0, 1)) ):
        return True
    return False


def check_orthogonal(axis_u, axis_v, axis_w):
    """Makes sure that the three input vectors are orthogonal"""
    if not (np.abs(axis_u.dot(axis_v) < 1e-6) and
            np.abs(axis_v.dot(axis_w) < 1e-6) and
            np.abs(axis_w.dot(axis_u) < 1e-6)):
        #raise ValueError('axis_u, axis_v, and axis_w must be orthogonal')
        return False
    return True


def add_data(output, data):
    """Adds data arrays to an output VTK data object"""
    for d in data:
        arr = d.array.array
        c = nps.numpy_to_vtk(num_array=arr)
        c.SetName(d.name)
        loc = d.location
        if loc == 'vertices':
            output.GetPointData().AddArray(c)
        else:
            output.GetCellData().AddArray(c)
    return output


def add_textures(output, textures, elname):
    """Add textures to a pyvista data object"""
    if not pyvista.is_pyvista_obj(output):
        output = pyvista.wrap(output)

    for i, tex in enumerate(textures):
        # Now map the coordinates for the texture
        m = vtk.vtkTextureMapToPlane()
        m.SetInputDataObject(output)
        m.SetOrigin(tex.origin)
        m.SetPoint1(tex.origin + tex.axis_u)
        m.SetPoint2(tex.origin + tex.axis_v)
        m.Update()
        # Grab the texture coordinates
        tmp = m.GetOutputDataObject(0)
        tcoord = tmp.GetPointData().GetTCoords()
        name = tex.name
        if name is None or name == '':
            name = '{}-texture-{}'.format(elname, i)
        tcoord.SetName(name)
        # Add these coordinates to the PointData of the output
        # NOTE: Let pyvista handle setting the TCoords because of how VTK cleans
        #       up old TCoords
        output.GetPointData().AddArray(tcoord)
        # Add the vtkTexture to the output
        img = np.array(Image.open(tex.image))
        tex.image.seek(0) # Reset the image bytes in case it is accessed again
        if img.shape[2] > 3:
            img = img[:, :, 0:3]
        vtexture = pyvista.numpy_to_texture(img)
        output.textures[name] = vtexture
        output._activate_texture(name)

    return output
