import unittest
import os
import shutil
import tempfile

import numpy as np
import omf
import omfvtk
import vtki


DATA_FILE = os.path.join(os.path.dirname(__file__), '../assets/test_file.omf')


class TestProjectWrapper(unittest.TestCase):
    """
    Test the wrapper for a project file which will iterate over all data types
    """
    def setUp(self):
        self.fname = DATA_FILE

    def test_wrap(self):
        """Test the whole suite"""
        data = omfvtk.load_project(self.fname)
        self.assertIsNotNone(data)
        self.assertEqual(data.n_blocks, 9)



class TestElements(unittest.TestCase):
    """
    This creates a dummy OMF project of random data
    """

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.project_filename = os.path.join(self.test_dir, 'project.omf')

        self.proj = omf.Project(name='Test project',
                                description='Just some assorted elements')
        self.pts = omf.PointSetElement(name='Random Points',
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
        self.line = omf.LineSetElement(
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

        self.surf = omf.SurfaceElement(
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
        self.grid = omf.SurfaceElement(
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

        self.vol = omf.VolumeElement(
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

        self.vol_ir = omf.VolumeElement(
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

        self.proj.elements = [self.pts, self.line, self.surf, self.grid, self.vol]
        self.assertTrue(self.proj.validate())


    def tearDown(self):
        # Remove the test data directory after the test
        shutil.rmtree(self.test_dir)

    def test_file_io(self):
        # Write out the project using omf
        omf.OMFWriter(self.proj, self.project_filename)
        # Read it back in using OMFVTK
        proj = omfvtk.load_project(self.project_filename)
        self.assertEqual(proj.n_blocks, 5)
        self.assertEqual(proj.get_block_name(0), 'Random Points')
        self.assertEqual(proj.get_block_name(1), 'Random Line')
        self.assertEqual(proj.get_block_name(2), 'trisurf')
        self.assertEqual(proj.get_block_name(3), 'gridsurf')
        self.assertEqual(proj.get_block_name(4), 'vol')

    def test_wrap_project(self):
        proj = omfvtk.wrap(self.proj)
        self.assertEqual(proj.n_blocks, 5)
        self.assertEqual(proj.get_block_name(0), 'Random Points')
        self.assertEqual(proj.get_block_name(1), 'Random Line')
        self.assertEqual(proj.get_block_name(2), 'trisurf')
        self.assertEqual(proj.get_block_name(3), 'gridsurf')
        self.assertEqual(proj.get_block_name(4), 'vol')
        # proj.save(os.path.join(self.test_dir, 'projectvtk.vtm'))


    def test_wrap_lineset(self):
        line = omfvtk.wrap(self.line)
        self.assertTrue(isinstance(line, vtki.PolyData))
        # Note that omfvtk adds a `Line Index` array
        self.assertEqual(line.n_scalars, len(self.line.data) + 1)
        self.assertEqual(line.n_cells, self.line.geometry.num_cells)
        self.assertEqual(line.n_points, self.line.geometry.num_nodes)


    def test_wrap_pointset(self):
        pts = omfvtk.wrap(self.pts)
        self.assertTrue(isinstance(pts, vtki.PolyData))
        self.assertEqual(pts.n_scalars, len(self.pts.data))
        self.assertEqual(pts.n_cells, self.pts.geometry.num_cells)
        self.assertEqual(pts.n_points, self.pts.geometry.num_nodes)

    def test_wrap_surface(self):
        surf = omfvtk.wrap(self.surf)
        self.assertTrue(isinstance(surf, vtki.UnstructuredGrid))
        self.assertEqual(surf.n_scalars, len(self.surf.data))
        self.assertEqual(surf.n_cells, self.surf.geometry.num_cells)
        self.assertEqual(surf.n_points, self.surf.geometry.num_nodes)
        grid = omfvtk.wrap(self.grid)
        self.assertTrue(isinstance(grid, vtki.StructuredGrid))
        self.assertEqual(grid.n_scalars, len(self.grid.data))
        self.assertEqual(grid.n_cells, self.grid.geometry.num_cells)
        self.assertEqual(grid.n_points, self.grid.geometry.num_nodes)

    def test_wrap_volume(self):
        vol = omfvtk.wrap(self.vol)
        self.assertEqual(vol.n_scalars, 1)
        self.assertTrue(isinstance(vol, vtki.RectilinearGrid))
        self.assertEqual(vol.n_scalars, len(self.vol.data))
        self.assertEqual(vol.n_cells, self.vol.geometry.num_cells)
        self.assertEqual(vol.n_points, self.vol.geometry.num_nodes)
        vol_ir = omfvtk.wrap(self.vol_ir)
        self.assertEqual(vol_ir.n_scalars, 1)
        self.assertTrue(isinstance(vol_ir, vtki.StructuredGrid))
        self.assertEqual(vol_ir.n_scalars, len(self.vol_ir.data))
        self.assertEqual(vol_ir.n_cells, self.vol_ir.geometry.num_cells)
        self.assertEqual(vol_ir.n_points, self.vol_ir.geometry.num_nodes)




if __name__ == '__main__':
    import unittest
    unittest.main()
