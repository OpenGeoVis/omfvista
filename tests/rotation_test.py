"""Tests for grid geometries whose axes are rotated relative to the global frame."""

import unittest

import numpy as np
import omf

import omfvista
from omfvista.volume import get_volume_shape

IDENTITY = ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
# 90 degrees about Z: u -> +Y, v -> -X. What Geosoft voxel exports commonly carry.
QUARTER_TURN = ([0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0])
# 30 degrees about Z, which no rectilinear grid can represent.
OBLIQUE = (
    [np.cos(np.pi / 6), np.sin(np.pi / 6), 0.0],
    [-np.sin(np.pi / 6), np.cos(np.pi / 6), 0.0],
    [0.0, 0.0, 1.0],
)


def make_volume(axes, origin=(1000.0, 2000.0, 0.0), shape=(2, 3, 4), spacing=5.0):
    """A small volume element carrying a distinct value in every cell."""
    axis_u, axis_v, axis_w = axes
    n_u, n_v, n_w = shape
    geometry = omf.VolumeGridGeometry(
        origin=list(origin),
        axis_u=axis_u,
        axis_v=axis_v,
        axis_w=axis_w,
        tensor_u=np.full(n_u, spacing),
        tensor_v=np.full(n_v, spacing),
        tensor_w=np.full(n_w, spacing),
    )
    return omf.VolumeElement(
        name="grid",
        geometry=geometry,
        data=[
            omf.ScalarData(
                name="values", array=np.arange(n_u * n_v * n_w, dtype=float), location="cells"
            )
        ],
    )


def expected_cells(element):
    """Cell centres and their values, computed straight from the OMF definition.

    A node sits at ``origin + u * axis_u + v * axis_v + w * axis_w``, so a cell
    centre uses the mid-point of each tensor interval. Deliberately independent
    of how omfvista builds the mesh.
    """
    geometry = element.geometry
    origin = np.array(geometry.origin, dtype=float)
    axes = np.array([geometry.axis_u, geometry.axis_v, geometry.axis_w], dtype=float)
    tensors = [
        np.asarray(t, dtype=float)
        for t in (geometry.tensor_u, geometry.tensor_v, geometry.tensor_w)
    ]
    mids = [np.cumsum(t) - t / 2 for t in tensors]
    values = np.reshape(element.data[0].array.array, [len(t) for t in tensors])

    points, expected = [], []
    for i, u in enumerate(mids[0]):
        for j, v in enumerate(mids[1]):
            for k, w in enumerate(mids[2]):
                points.append(origin + u * axes[0] + v * axes[1] + w * axes[2])
                expected.append(values[i, j, k])
    return np.array(points), np.array(expected)


def corner_bounds(element):
    """The axis-aligned bounding box of the eight rotated corners of the grid."""
    geometry = element.geometry
    origin = np.array(geometry.origin, dtype=float)
    axes = np.array([geometry.axis_u, geometry.axis_v, geometry.axis_w], dtype=float)
    spans = [np.sum(t) for t in (geometry.tensor_u, geometry.tensor_v, geometry.tensor_w)]
    corners = np.array(
        [
            origin + a * spans[0] * axes[0] + b * spans[1] * axes[1] + c * spans[2] * axes[2]
            for a in (0, 1)
            for b in (0, 1)
            for c in (0, 1)
        ]
    )
    return np.ravel(list(zip(corners.min(axis=0), corners.max(axis=0))))


class TestRotatedVolumeGrid(unittest.TestCase):
    """The geometry origin is a global translation, so it must not be rotated."""

    def test_quarter_turn_is_placed_at_the_origin(self):
        """X = 1000 - v, Y = 2000 + u, Z = w -- not the origin swung about world zero."""
        grid = omfvista.volume_to_vtk(make_volume(QUARTER_TURN))
        self.assertTrue(
            np.allclose(grid.bounds, (985.0, 1000.0, 2000.0, 2010.0, 0.0, 20.0)), grid.bounds
        )

    def test_oblique_rotation_is_placed_at_the_origin(self):
        element = make_volume(OBLIQUE)
        grid = omfvista.volume_to_vtk(element)
        self.assertTrue(np.allclose(grid.bounds, corner_bounds(element)), grid.bounds)

    def test_values_land_in_the_cells_omf_defines(self):
        """Shape and cell order can look right while the mesh sits in the wrong place."""
        for name, axes in (("identity", IDENTITY), ("quarter", QUARTER_TURN), ("oblique", OBLIQUE)):
            with self.subTest(axes=name):
                element = make_volume(axes)
                grid = omfvista.volume_to_vtk(element)
                points, values = expected_cells(element)
                centres = grid.cell_centers().points
                self.assertEqual(len(centres), len(points))
                for centre, value in zip(centres, grid.cell_data["values"]):
                    distances = np.linalg.norm(points - centre, axis=1)
                    nearest = int(np.argmin(distances))
                    self.assertLess(distances[nearest], 1e-6)
                    self.assertEqual(values[nearest], value)


class TestUnrotatedVolumeGrid(unittest.TestCase):
    """Identity frames were always correct and must stay byte-for-byte unchanged."""

    def test_bounds_include_both_origins(self):
        element = make_volume(IDENTITY, origin=(1000.0, 2000.0, 7.0))
        grid = omfvista.volume_to_vtk(element, origin=(10.0, 20.0, 30.0))
        self.assertTrue(
            np.allclose(grid.bounds, (1010.0, 1020.0, 2020.0, 2035.0, 37.0, 57.0)), grid.bounds
        )

    def test_cell_order_is_unchanged(self):
        element = make_volume(IDENTITY)
        grid = omfvista.volume_to_vtk(element)
        shape = get_volume_shape(element.geometry)
        expected = np.reshape(element.data[0].array.array, shape).flatten(order="F")
        self.assertTrue(np.array_equal(grid.cell_data["values"], expected))


class TestRotatedSurfaceGrid(unittest.TestCase):
    """``surface_grid_geom_to_vtk`` always rotates, so it has no identity fast path."""

    @staticmethod
    def make_surface(axes, origin=(1000.0, 2000.0, 0.0), shape=(2, 3), spacing=5.0):
        axis_u, axis_v, _ = axes
        n_u, n_v = shape
        geometry = omf.SurfaceGridGeometry(
            origin=list(origin),
            axis_u=axis_u,
            axis_v=axis_v,
            tensor_u=np.full(n_u, spacing),
            tensor_v=np.full(n_v, spacing),
            offset_w=np.zeros((n_u + 1) * (n_v + 1)),
        )
        return omf.SurfaceElement(name="grid", geometry=geometry)

    def test_quarter_turn_is_placed_at_the_origin(self):
        grid = omfvista.surface_to_vtk(self.make_surface(QUARTER_TURN))
        self.assertTrue(
            np.allclose(grid.bounds, (985.0, 1000.0, 2000.0, 2010.0, 0.0, 0.0)), grid.bounds
        )

    def test_identity_is_placed_at_the_origin(self):
        grid = omfvista.surface_to_vtk(self.make_surface(IDENTITY))
        self.assertTrue(
            np.allclose(grid.bounds, (1000.0, 1010.0, 2000.0, 2015.0, 0.0, 0.0)), grid.bounds
        )


if __name__ == "__main__":
    unittest.main()
