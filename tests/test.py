import unittest
import shutil
import tempfile
import os

try:
    import urllib.request as download
except ImportError:
    import urllib2.urlopen as download


import omf
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
        reader = omf.OMFReader(self.fname)
        project = reader.get_project()
        # Iterate over the elements and add converted VTK object to dictionary:
        data = dict()
        for e in project.elements:
            print('wrapping {} ...'.format(e.__class__.__name__))
            d = omfvtk.wrap(e)
            data[e.name] = d
            self.assertIsNotNone(d)



if __name__ == '__main__':
    import unittest
    unittest.main()
