"""Tests for the axis-frame helpers in ``omfvista.utilities``."""

import unittest

import numpy as np

from omfvista.utilities import check_orientation, check_orthogonal

ORTHOGONAL = (
    np.array([1.0, 0.0, 0.0]),
    np.array([0.0, 1.0, 0.0]),
    np.array([0.0, 0.0, 1.0]),
)


def frame(angle):
    """A frame whose u and v axes are ``angle`` radians apart, so u . v = cos(angle)."""
    axis_u = np.array([1.0, 0.0, 0.0])
    axis_v = np.array([np.cos(angle), np.sin(angle), 0.0])
    return axis_u, axis_v, np.cross(axis_u, axis_v)


class TestCheckOrthogonal(unittest.TestCase):
    """``np.abs`` belongs on the dot product, not on the comparison."""

    def test_orthogonal_frame_passes(self):
        self.assertTrue(check_orthogonal(*ORTHOGONAL))

    def test_rotated_orthogonal_frame_passes(self):
        self.assertTrue(check_orthogonal(*frame(np.pi / 2)))

    def test_acute_frame_is_rejected(self):
        """u . v = +0.5. Rejected either way -- the baseline for the case below."""
        self.assertFalse(check_orthogonal(*frame(np.pi / 3)))

    def test_obtuse_frame_is_rejected(self):
        """u . v = -0.5, which ``np.abs(dot < 1e-6)`` wrongly reports as orthogonal."""
        self.assertFalse(check_orthogonal(*frame(2 * np.pi / 3)))

    def test_nearly_orthogonal_frame_passes(self):
        """The 1e-6 tolerance is there to absorb floating point noise."""
        axis_u = np.array([1.0, 0.0, 0.0])
        axis_v = np.array([1e-9, 1.0, 0.0])
        self.assertTrue(check_orthogonal(axis_u, axis_v, np.cross(axis_u, axis_v)))


class TestCheckOrientation(unittest.TestCase):
    """Only the exact cartesian frame counts as the standard orientation."""

    def test_standard_frame(self):
        self.assertTrue(check_orientation(*ORTHOGONAL))

    def test_rotated_frame(self):
        self.assertFalse(check_orientation([0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]))


if __name__ == "__main__":
    unittest.main()
