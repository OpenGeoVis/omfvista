"""Tests for representing 90-degree rotations as a RectilinearGrid."""

import unittest

import numpy as np
import omf
import pyvista

import omfvista
from omfvista.utilities import axis_permutation
from omfvista.volume import rectilinear_axes

IDENTITY = ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
# 90 degrees about Z: u -> +Y, v -> -X.
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


class TestAxisPermutation(unittest.TestCase):
    """Only a signed permutation matrix stays rectilinear in the global frame."""

    def test_identity(self):
        self.assertEqual(axis_permutation(*IDENTITY), ((0, 1, 2), (1.0, 1.0, 1.0)))

    def test_quarter_turn(self):
        self.assertEqual(axis_permutation(*QUARTER_TURN), ((1, 0, 2), (1.0, -1.0, 1.0)))

    def test_oblique_rotation_is_rejected(self):
        self.assertIsNone(axis_permutation(*OBLIQUE))

    def test_floating_point_noise_is_tolerated(self):
        """A 90-degree turn built from cos/sin leaves 6.1e-17 in place of zero."""
        angle = np.pi / 2
        axes = (
            [np.cos(angle), np.sin(angle), 0.0],
            [-np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        )
        self.assertEqual(axis_permutation(*axes), ((1, 0, 2), (1.0, -1.0, 1.0)))

    def test_duplicated_axis_is_rejected(self):
        """Integer entries are not enough; each axis must be used exactly once."""
        self.assertIsNone(axis_permutation([1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))


class TestRectilinearAxes(unittest.TestCase):
    """Node coordinates come back ascending, with the flip recorded separately."""

    def test_quarter_turn_axes_ascend(self):
        coords, perm, flip = rectilinear_axes(make_volume(QUARTER_TURN).geometry)
        x, y, z = coords
        self.assertEqual(perm, (1, 0, 2))
        self.assertEqual(flip, (True, False, False))
        self.assertTrue(np.array_equal(x, [985.0, 990.0, 995.0, 1000.0]))
        self.assertTrue(np.array_equal(y, [2000.0, 2005.0, 2010.0]))
        self.assertTrue(np.array_equal(z, [0.0, 5.0, 10.0, 15.0, 20.0]))

    def test_oblique_rotation_has_no_rectilinear_form(self):
        self.assertIsNone(rectilinear_axes(make_volume(OBLIQUE).geometry))


class TestGridType(unittest.TestCase):
    """A RectilinearGrid stores three coordinate vectors instead of every node."""

    def test_quarter_turn_is_rectilinear(self):
        grid = omfvista.volume_to_vtk(make_volume(QUARTER_TURN))
        self.assertIsInstance(grid, pyvista.RectilinearGrid)

    def test_identity_is_rectilinear(self):
        grid = omfvista.volume_to_vtk(make_volume(IDENTITY))
        self.assertIsInstance(grid, pyvista.RectilinearGrid)

    def test_oblique_rotation_falls_back_to_structured(self):
        grid = omfvista.volume_to_vtk(make_volume(OBLIQUE))
        self.assertIsInstance(grid, pyvista.StructuredGrid)


class TestCellDataFollowsTheAxes(unittest.TestCase):
    """Re-expressing the grid on global axes must re-order the cube to match."""

    def test_identity_cell_order_is_unchanged(self):
        """The transpose is a no-op here, so this must match the pre-existing output."""
        element = make_volume(IDENTITY)
        grid = omfvista.volume_to_vtk(element)
        expected = np.reshape(element.data[0].array.array, (2, 3, 4)).flatten(order="F")
        self.assertTrue(np.array_equal(grid.cell_data["values"], expected))

    def test_quarter_turn_cube_is_transposed_and_flipped(self):
        element = make_volume(QUARTER_TURN)
        grid = omfvista.volume_to_vtk(element)
        cube = np.reshape(element.data[0].array.array, (2, 3, 4))
        # u feeds global Y, v feeds global X reversed, w feeds global Z.
        expected = np.transpose(cube, (1, 0, 2))[::-1, :, :]
        self.assertTrue(np.array_equal(grid.cell_data["values"], expected.flatten(order="F")))

    def test_lowest_corner_cell_holds_the_value_omf_puts_there(self):
        """Cell (u=0, v=2, w=0) is the one at minimum X and minimum Y."""
        element = make_volume(QUARTER_TURN)
        grid = omfvista.volume_to_vtk(element)
        cube = np.reshape(element.data[0].array.array, (2, 3, 4))
        self.assertEqual(grid.cell_data["values"][0], cube[0, 2, 0])


if __name__ == "__main__":
    unittest.main()
