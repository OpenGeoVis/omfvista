"""Methods for converting volumetric data objects"""

__all__ = [
    "get_volume_shape",
    "rectilinear_axes",
    "volume_grid_geom_to_vtk",
    "volume_to_vtk",
]

__displayname__ = "Volume"

import numpy as np
import pyvista

from omfvista.utilities import axis_permutation


def get_volume_shape(vol):
    """Returns the shape of a gridded volume"""
    return (len(vol.tensor_u), len(vol.tensor_v), len(vol.tensor_w))


def rectilinear_axes(volgridgeom):
    """Global-axis node coordinates for a grid rotated by multiples of 90 degrees.

    Returns ``(coords, perm, flip)`` -- ascending node coordinates along global
    X/Y/Z, the local axis feeding each global axis, and whether it is reversed --
    or ``None`` when the grid is obliquely rotated and needs a StructuredGrid.
    """
    found = axis_permutation(volgridgeom.axis_u, volgridgeom.axis_v, volgridgeom.axis_w)
    if found is None:
        return None
    local2global, signs = found
    grid_origin = np.asarray(volgridgeom.origin, dtype=float)
    local = [
        np.insert(np.cumsum(np.asarray(getattr(volgridgeom, "tensor_" + a), dtype=float)), 0, 0.0)
        for a in "uvw"
    ]
    coords, perm, flip = [None] * 3, [None] * 3, [None] * 3
    for local_axis in range(3):
        global_axis, sign = local2global[local_axis], signs[local_axis]
        coord = grid_origin[global_axis] + sign * local[local_axis]
        perm[global_axis], flip[global_axis] = local_axis, bool(sign < 0)
        coords[global_axis] = coord[::-1].copy() if sign < 0 else coord
    return coords, tuple(perm), tuple(flip)


def volume_grid_geom_to_vtk(volgridgeom, origin=(0.0, 0.0, 0.0)):
    """Convert the 3D gridded volume to a :class:`pyvista.StructuredGrid`
    (or a :class:`pyvista.RectilinearGrid` when apprropriate) object contatining
    the 2D surface.

    Args:
        volgridgeom (:class:`omf.volume.VolumeGridGeometry`): the grid geometry
            to convert
    """
    volgridgeom._validate_mesh()

    # Node coordinates in the *local* (u, v, w) frame, i.e. not yet offset by
    # the geometry origin -- the origin is a global-frame translation and must
    # only be applied after the axes have been rotated.
    u = np.insert(np.cumsum(volgridgeom.tensor_u), 0, 0.0)
    v = np.insert(np.cumsum(volgridgeom.tensor_v), 0, 0.0)
    w = np.insert(np.cumsum(volgridgeom.tensor_w), 0, 0.0)

    # A frame rotated by multiples of 90 deg is still rectilinear in the global
    # frame, so a vtkRectilinearGrid represents it exactly (and far more cheaply
    # than storing every node of a vtkStructuredGrid).
    rect = rectilinear_axes(volgridgeom)
    if rect is not None:
        (xx, yy, zz), _, _ = rect
        return pyvista.RectilinearGrid(xx + origin[0], yy + origin[1], zz + origin[2])

    # Otherwise use a vtkStructuredGrid
    # Build out all nodes in the mesh
    uu, vv, ww = np.meshgrid(u, v, w, indexing="ij")
    points = np.c_[uu.ravel("F"), vv.ravel("F"), ww.ravel("F")]

    # Rotate the points based on the axis orientations, then translate
    rotation_mtx = np.array([volgridgeom.axis_u, volgridgeom.axis_v, volgridgeom.axis_w])
    points = points.dot(rotation_mtx)
    points += np.array(volgridgeom.origin)

    output = pyvista.StructuredGrid()
    output.points = points
    output.dimensions = len(u), len(v), len(w)
    output.points += np.array(origin)
    return output


def volume_to_vtk(volelement, origin=(0.0, 0.0, 0.0)):
    """Convert the volume element to a VTK data object.

    Args:
        volelement (:class:`omf.volume.VolumeElement`): The volume element to
            convert

    """
    output = volume_grid_geom_to_vtk(volelement.geometry, origin=origin)
    shp = get_volume_shape(volelement.geometry)
    rect = rectilinear_axes(volelement.geometry)
    # Add data to output
    for data in volelement.data:
        arr = np.reshape(data.array.array, shp)
        if rect is not None:
            # The grid was re-expressed on global axes, so the cube must follow.
            # For an identity frame this is a no-op, matching previous behaviour.
            _, perm, flip = rect
            arr = np.transpose(arr, perm)
            arr = arr[tuple(slice(None, None, -1) if f else slice(None) for f in flip)]
        output[data.name] = arr.flatten(order="F")
    return output


# Now set up the display names for the docs
volume_to_vtk.__displayname__ = "Volume to VTK"
volume_grid_geom_to_vtk.__displayname__ = "Volume Grid Geometry to VTK"
get_volume_shape.__displayname__ = "Volume Shape"
