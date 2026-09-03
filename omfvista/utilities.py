__all__ = [
    "check_orientation",
    "axis_permutation",
    "check_orthogonal",
    "add_data",
    "add_texture_coordinates",
]


from PIL import Image
import numpy as np
import pyvista

try:
    from pyvista import is_pyvista_obj as is_pyvista_dataset
except ImportError:
    from pyvista import is_pyvista_dataset


def check_orientation(axis_u, axis_v, axis_w):
    """This will check if the given ``axis_*`` vectors are the typical
    cartesian refernece frame (i.e. rectilinear).
    """
    if (
        np.allclose(axis_u, (1, 0, 0))
        and np.allclose(axis_v, (0, 1, 0))
        and np.allclose(axis_w, (0, 0, 1))
    ):
        return True
    return False


def axis_permutation(axis_u, axis_v, axis_w, atol=1e-9):
    """Detect an axis frame that is a rotation by multiples of 90 degrees.

    Such a frame is a signed permutation matrix, which means the grid is still
    rectilinear in the global frame and can be represented exactly by a
    ``vtkRectilinearGrid`` -- no need for a ``vtkStructuredGrid``.

    Returns ``(perm, signs)``, where ``perm[i]`` is the global axis that local
    axis ``i`` (0=u, 1=v, 2=w) maps onto and ``signs[i]`` is +1/-1, or ``None``
    if the frame is obliquely rotated.
    """
    mtx = np.array([axis_u, axis_v, axis_w], dtype=float)
    rounded = np.round(mtx)
    if not np.allclose(mtx, rounded, atol=atol):
        return None
    if not (
        np.array_equal(np.abs(rounded).sum(axis=0), np.ones(3))
        and np.array_equal(np.abs(rounded).sum(axis=1), np.ones(3))
    ):
        return None
    perm = tuple(int(np.flatnonzero(rounded[i])[0]) for i in range(3))
    signs = tuple(float(rounded[i, perm[i]]) for i in range(3))
    return perm, signs


def check_orthogonal(axis_u, axis_v, axis_w):
    """Makes sure that the three input vectors are orthogonal"""
    if not (
        np.abs(axis_u.dot(axis_v) < 1e-6)
        and np.abs(axis_v.dot(axis_w) < 1e-6)
        and np.abs(axis_w.dot(axis_u) < 1e-6)
    ):
        # raise ValueError('axis_u, axis_v, and axis_w must be orthogonal')
        return False
    return True


def add_data(output, data):
    """Adds data arrays to an output VTK data object"""
    for d in data:
        output[d.name] = np.array(d.array.array)
    return output


def add_texture_coordinates(output, textures, elname):
    """Add texture coordinates to a pyvista data object."""
    if not is_pyvista_dataset(output):
        output = pyvista.wrap(output)
    for i, tex in enumerate(textures):
        # Now map the coordinates for the texture
        tmp = output.texture_map_to_plane(
            origin=tex.origin,
            point_u=tex.origin + tex.axis_u,
            point_v=tex.origin + tex.axis_v,
        )
        # Grab the texture coordinates
        tcoord = tmp.GetPointData().GetTCoords()
        name = tex.name
        if name is None or name == "":
            name = "{}-texture-{}".format(elname, i)
        tcoord.SetName(name)
        # Add these coordinates to the PointData of the output
        # NOTE: Let pyvista handle setting the TCoords because of how VTK cleans
        #       up old TCoords
        output.GetPointData().AddArray(tcoord)
    return output


def texture_to_vtk(texture):
    """Convert an OMF texture to a VTK texture."""
    img = np.array(Image.open(texture.image))
    texture.image.seek(0)  # Reset the image bytes in case it is accessed again
    if img.shape[2] > 3:
        img = img[:, :, 0:3]
    vtexture = pyvista.numpy_to_texture(img)
    return vtexture


def get_textures(element):
    """Get a dictionary of textures for a given element."""
    return [texture_to_vtk(tex) for tex in element.textures]
