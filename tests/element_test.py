import unittest
import os
import shutil
import tempfile

import numpy as np
import omf
import omfvtk
import vtki

PROJECT = omf.Project(name='Test project',
                        description='Just some assorted elements')
POINTSET = omf.PointSetElement(name='Random Points',
                          description='Just random points',
                          geometry=omf.PointSetGeometry(
                                  vertices=np.random.rand(100, 3)
                                  ),
                          data=[
                              omf.ScalarData(
                                      name='rand data',
                                      array=np.random.rand(100),
                                      location='vertices'
                                      ),

                              omf.ScalarData(
                                      name='More rand data',
                                      array=np.random.rand(100),
                                      location='vertices'
                                      )
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
                          color='green'
                          )
LINESET = omf.LineSetElement(
    name='Random Line',
    geometry=omf.LineSetGeometry(
        vertices=np.random.rand(100, 3),
        segments=np.floor(np.random.rand(50, 2)*100).astype(int)
    ),
    data=[
        omf.ScalarData(
            name='rand vert data',
            array=np.random.rand(100),
            location='vertices'
        ),
        omf.ScalarData(
            name='rand segment data',
            array=np.random.rand(50),
            location='segments'
        )
    ],
    color='#0000FF'
)

SURFACE = omf.SurfaceElement(
    name='trisurf',
    geometry=omf.SurfaceGeometry(
        vertices=np.random.rand(100, 3),
        triangles=np.floor(np.random.rand(50, 3)*100).astype(int)
    ),
    data=[
        omf.ScalarData(
            name='rand vert data',
            array=np.random.rand(100),
            location='vertices'
        ),
        omf.ScalarData(
            name='rand face data',
            array=np.random.rand(50),
            location='faces'
        )
    ],
    color=[100, 200, 200]
)
GRID = omf.SurfaceElement(
    name='gridsurf',
    geometry=omf.SurfaceGridGeometry(
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        origin=[50., 50., 50.],
        axis_u=[1., 0, 0],
        axis_v=[0, 0, 1.],
        offset_w=np.random.rand(11, 16).flatten()
    ),
    data=[
        omf.ScalarData(
            name='rand vert data',
            array=np.random.rand(11, 16).flatten(),
            location='vertices'
        ),
        omf.ScalarData(
            name='rand face data',
            array=np.random.rand(10, 15).flatten(order='f'),
            location='faces'
        )
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
    name='vol',
    geometry=omf.VolumeGridGeometry(
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        tensor_w=np.ones(20).astype(float),
        origin=[10., 10., -10]
    ),
    data=[
        omf.ScalarData(
            name='Random Data',
            location='cells',
            array=np.random.rand(10, 15, 20).flatten()
        )
    ]
)

VOLUME_IR = omf.VolumeElement(
    name='vol_ir',
    geometry=omf.VolumeGridGeometry(
        axis_u=[1,1,0],
        axis_v=[0,0,1],
        axis_w=[ 1, -1,  0],
        tensor_u=np.ones(10).astype(float),
        tensor_v=np.ones(15).astype(float),
        tensor_w=np.ones(20).astype(float),
        origin=[10., 10., -10]
    ),
    data=[
        omf.ScalarData(
            name='Random Data',
            location='cells',
            array=np.random.rand(10, 15, 20).flatten()
        )
    ]
)

PROJECT.elements = [POINTSET, LINESET, SURFACE, GRID, VOLUME, VOLUME_IR]
if not PROJECT.validate():
    raise AssertionError('Testing data is not valid.')






class TestElements(unittest.TestCase):
    """
    This creates a dummy OMF project of random data
    """

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.project_filename = os.path.join(self.test_dir, 'project.omf')
        self.vtm_filename = os.path.join(self.test_dir, 'project.vtm')

    def tearDown(self):
        # Remove the test data directory after the test
        shutil.rmtree(self.test_dir)

    def test_file_io(self):
        # Write out the project using omf
        omf.OMFWriter(PROJECT, self.project_filename)
        # Read it back in using OMFVTK
        proj = omfvtk.load_project(self.project_filename)
        self.assertEqual(proj.n_blocks, len(PROJECT.elements))
        self.assertEqual(proj.get_block_name(0), 'Random Points')
        self.assertEqual(proj.get_block_name(1), 'Random Line')
        self.assertEqual(proj.get_block_name(2), 'trisurf')
        self.assertEqual(proj.get_block_name(3), 'gridsurf')
        self.assertEqual(proj.get_block_name(4), 'vol')
        self.assertEqual(proj.get_block_name(5), 'vol_ir')

    def test_wrap_project(self):
        proj = omfvtk.wrap(PROJECT)
        self.assertEqual(proj.n_blocks, len(PROJECT.elements))
        self.assertEqual(proj.get_block_name(0), 'Random Points')
        self.assertEqual(proj.get_block_name(1), 'Random Line')
        self.assertEqual(proj.get_block_name(2), 'trisurf')
        self.assertEqual(proj.get_block_name(3), 'gridsurf')
        self.assertEqual(proj.get_block_name(4), 'vol')
        self.assertEqual(proj.get_block_name(5), 'vol_ir')


    def test_wrap_lineset(self):
        line = omfvtk.wrap(LINESET)
        self.assertTrue(isinstance(line, vtki.PolyData))
        # Note that omfvtk adds a `Line Index` array
        self.assertEqual(line.n_scalars, len(LINESET.data) + 1)
        self.assertEqual(line.n_cells, LINESET.geometry.num_cells)
        self.assertEqual(line.n_points, LINESET.geometry.num_nodes)


    def test_wrap_pointset(self):
        pts = omfvtk.wrap(POINTSET)
        self.assertTrue(isinstance(pts, vtki.PolyData))
        self.assertEqual(pts.n_scalars, len(POINTSET.data))
        self.assertEqual(pts.n_cells, POINTSET.geometry.num_cells)
        self.assertEqual(pts.n_points, POINTSET.geometry.num_nodes)

    def test_wrap_surface(self):
        surf = omfvtk.wrap(SURFACE)
        self.assertTrue(isinstance(surf, vtki.UnstructuredGrid))
        self.assertEqual(surf.n_scalars, len(SURFACE.data))
        self.assertEqual(surf.n_cells, SURFACE.geometry.num_cells)
        self.assertEqual(surf.n_points, SURFACE.geometry.num_nodes)
        grid = omfvtk.wrap(GRID)
        self.assertTrue(isinstance(grid, vtki.StructuredGrid))
        self.assertEqual(grid.n_scalars, len(GRID.data))
        self.assertEqual(grid.n_cells, GRID.geometry.num_cells)
        self.assertEqual(grid.n_points, GRID.geometry.num_nodes)

    def test_wrap_volume(self):
        vol = omfvtk.wrap(VOLUME)
        self.assertEqual(vol.n_scalars, 1)
        self.assertTrue(isinstance(vol, vtki.RectilinearGrid))
        self.assertEqual(vol.n_scalars, len(VOLUME.data))
        self.assertEqual(vol.n_cells, VOLUME.geometry.num_cells)
        self.assertEqual(vol.n_points, VOLUME.geometry.num_nodes)
        vol_ir = omfvtk.wrap(VOLUME_IR)
        self.assertEqual(vol_ir.n_scalars, 1)
        self.assertTrue(isinstance(vol_ir, vtki.StructuredGrid))
        self.assertEqual(vol_ir.n_scalars, len(VOLUME_IR.data))
        self.assertEqual(vol_ir.n_cells, VOLUME_IR.geometry.num_cells)
        self.assertEqual(vol_ir.n_points, VOLUME_IR.geometry.num_nodes)




if __name__ == '__main__':
    import unittest
    unittest.main()
