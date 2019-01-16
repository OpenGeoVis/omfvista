import unittest
import os

import omfvtk


DATA_FILE = os.path.join(os.path.dirname(__file__), '../assets/test_file.omf')


class TestWrapper(unittest.TestCase):
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



if __name__ == '__main__':
    import unittest
    unittest.main()
