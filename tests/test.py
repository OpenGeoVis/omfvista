import unittest
import shutil
import tempfile
import os

from six.moves import urllib

import omfvtk


DATA_URL = "https://raw.githubusercontent.com/gmggroup/omf/master/assets/test_file.omf"



class TestWrapper(unittest.TestCase):
    """
    Test the wrapper
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.fname = os.path.join(self.test_dir, 'test_file.omf')
        urllib.request.urlretrieve(DATA_URL, self.fname)

    def tearDown(self):
        # Remove the test data directory after the test
        shutil.rmtree(self.test_dir)

    def test_wrap(self):
        data = omfvtk.load_project(self.fname)
        self.assertIsNotNone(data)
        self.assertEqual(data.n_blocks, 9)



if __name__ == '__main__':
    import unittest
    unittest.main()
