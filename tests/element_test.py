import os
import shutil
import tempfile
import unittest

import numpy as np
import omf
import pyvista

import omfvista

PROJECT = omf.Project(name="Test project", description="Just some assorted elements")
POINTSET = omf.PointSetElement(
    name="Random Points",
    description="Just random points",
    geometry=omf.PointSetGeometry(vertices=np.random.rand(100, 3)),
    data=[
        omf.ScalarData(name="rand data", array=np.random.rand(100), location="vertices"),
        omf.ScalarData(name="More rand data", array=np.random.rand(100), location="vertices"),
    ],
    #                           textures=[
    #                                   omf.ImageTexture(
    #                                           name='test image',
    #                                           image='test_image.png',
    #                                           origin=[0, 0, 0],
    #                                           axis_u=[1, 0, 0],
    #                                           axis_v=[0, 1, 0]
    #                                           ),
    #                                   omf.ImageTexture(
    #                                           name='test image',
    #                                           image='test_image.png',
    #                                           origin=[0, 0, 0],
    #                                           axis_u=[1, 0, 0],
    #                                           axis_v=[0, 0, 1]
    #                                           )
    #                                   ],
    color="green",
)
LINESET = omf.LineSetElement(
    name="Random Line",
    geometry=omf.LineSetGeometry(
        vertices=np.random.rand(100, 3),
        segments=np.floor(np.random.rand(50, 2) * 100).astype(int),
    ),
    data=[
        omf.ScalarData(name="rand vert data", array=np.random.rand(100), location="vertices"),
        omf.ScalarData(name="rand segment data", array=np.random.rand(50), location="segments"),
    ],
    color="#0000FF",
)

SURFACE = omf.SurfaceElement(
    name="trisurf",
    geometry=omf.SurfaceGeometry(
        vertices=np.random.rand(100, 3),
        triangles=np.floor(np.random.rand(50, 3) * 100).astype(int),
    ),
    data=[
        omf.ScalarData(name="rand vert data", array=np.random.rand(100), location="vertices"),
        omf.ScalarData(name="rand face data", array=np.random.rand(50), location="faces"),
    ],
    color=[100, 200, 200],
)
GRID = omf.SurfaceElement(
    name="gridsurf",
    geometry=omf.SurfaceGridGeometry(
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        origin=[50.0, 50.0, 50.0],
        axis_u=[1.0, 0, 0],
        axis_v=[0, 0, 1.0],
        offset_w=np.random.rand(11, 16).flatten(),
    ),
    data=[
        omf.ScalarData(
            name="rand vert data",
            array=np.random.rand(11, 16).flatten(),
            location="vertices",
        ),
        omf.ScalarData(
            name="rand face data",
            array=np.random.rand(10, 15).flatten(order="f"),
            location="faces",
        ),
    ],
    # textures=[
    #     omf.ImageTexture(
    #         name='test image',
    #         image='test_image.png',
    #         origin=[2., 2., 2.],
    #         axis_u=[5., 0, 0],
    #         axis_v=[0, 2., 5.]
    #     )
    # ]
)

VOLUME = omf.VolumeElement(
    name="vol",
    geometry=omf.VolumeGridGeometry(
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        tensor_w=np.ones(20).astype(float),
        origin=[10.0, 10.0, -10],
    ),
    data=[
        omf.ScalarData(
            name="Random Data",
            location="cells",
            array=np.random.rand(10, 15, 20).flatten(),
        )
    ],
)

VOLUME_IR = omf.VolumeElement(
    name="vol_ir",
    geometry=omf.VolumeGridGeometry(
        axis_u=[1, 1, 0],
        axis_v=[0, 0, 1],
        axis_w=[1, -1, 0],
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        tensor_w=np.ones(20).astype(float),
        origin=[10.0, 10.0, -10],
    ),
    data=[
        omf.ScalarData(
            name="Random Data",
            location="cells",
            array=np.random.rand(10, 15, 20).flatten(),
        )
    ],
)

PROJECT.elements = [POINTSET, LINESET, SURFACE, GRID, VOLUME, VOLUME_IR]
if not PROJECT.validate():
    raise AssertionError("Testing data is not valid.")


class TestElements(unittest.TestCase):
    """
    This creates a dummy OMF project of random data
    """

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.project_filename = os.path.join(self.test_dir, "project.omf")
        self.vtm_filename = os.path.join(self.test_dir, "project.vtm")

    def tearDown(self):
        # Remove the test data directory after the test
        shutil.rmtree(self.test_dir)

    def _check_multi_block(self, proj):
        self.assertEqual(proj.n_blocks, len(PROJECT.elements))
        self.assertEqual(proj.get_block_name(0), "Random Points")
        self.assertEqual(proj.get_block_name(1), "Random Line")
        self.assertEqual(proj.get_block_name(2), "trisurf")
        self.assertEqual(proj.get_block_name(3), "gridsurf")
        self.assertEqual(proj.get_block_name(4), "vol")
        self.assertEqual(proj.get_block_name(5), "vol_ir")

    def test_file_io(self):
        # Write out the project using omf
        omf.OMFWriter(PROJECT, self.project_filename)
        # Read it back in using omfvista
        proj = omfvista.load_project(self.project_filename)
        self._check_multi_block(proj)

    def test_wrap_project(self):
        proj = omfvista.wrap(PROJECT)
        self._check_multi_block(proj)

    def test_wrap_list_of_elements(self):
        proj = omfvista.wrap(PROJECT.elements)
        self._check_multi_block(proj)

    def test_wrap_lineset(self):
        line = omfvista.wrap(LINESET)
        self.assertTrue(isinstance(line, pyvista.PolyData))
        # Note that omfvista adds a `Line Index` array
        self.assertEqual(line.n_arrays, len(LINESET.data) + 1)
        self.assertEqual(line.n_cells, LINESET.geometry.num_cells)
        self.assertEqual(line.n_points, LINESET.geometry.num_nodes)

    def test_wrap_pointset(self):
        pts = omfvista.wrap(POINTSET)
        self.assertTrue(isinstance(pts, pyvista.PolyData))
        self.assertEqual(pts.n_arrays, len(POINTSET.data))
        self.assertEqual(pts.n_cells, POINTSET.geometry.num_cells)
        self.assertEqual(pts.n_points, POINTSET.geometry.num_nodes)

    def test_wrap_surface(self):
        surf = omfvista.wrap(SURFACE)
        self.assertTrue(isinstance(surf, pyvista.PolyData))
        self.assertEqual(surf.n_arrays, len(SURFACE.data))
        self.assertEqual(surf.n_cells, SURFACE.geometry.num_cells)
        self.assertEqual(surf.n_points, SURFACE.geometry.num_nodes)
        grid = omfvista.wrap(GRID)
        self.assertTrue(isinstance(grid, pyvista.StructuredGrid))
        self.assertEqual(grid.n_arrays, len(GRID.data))
        self.assertEqual(grid.n_cells, GRID.geometry.num_cells)
        self.assertEqual(grid.n_points, GRID.geometry.num_nodes)

    def test_wrap_volume(self):
        vol = omfvista.wrap(VOLUME)
        self.assertEqual(vol.n_arrays, 1)
        self.assertTrue(isinstance(vol, pyvista.RectilinearGrid))
        self.assertEqual(vol.n_arrays, len(VOLUME.data))
        self.assertEqual(vol.n_cells, VOLUME.geometry.num_cells)
        self.assertEqual(vol.n_points, VOLUME.geometry.num_nodes)
        vol_ir = omfvista.wrap(VOLUME_IR)
        self.assertEqual(vol_ir.n_arrays, 1)
        self.assertTrue(isinstance(vol_ir, pyvista.StructuredGrid))
        self.assertEqual(vol_ir.n_arrays, len(VOLUME_IR.data))
        self.assertEqual(vol_ir.n_cells, VOLUME_IR.geometry.num_cells)
        self.assertEqual(vol_ir.n_points, VOLUME_IR.geometry.num_nodes)


if __name__ == "__main__":
    import unittest

    unittest.main()
