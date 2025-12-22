import unittest
import os
from hdf5_indexed_reader import open_h5_file

class TestCNDBLocal(unittest.TestCase):
    @unittest.skipUnless(os.path.exists("test/spleen_1chr1rep.indexed.cndb"), "Test file not found")
    def test_cndb_indexed(self):
        config = {'path': "test/spleen_1chr1rep.indexed.cndb"}
        hdf_file = open_h5_file(config)
        # Add basic checks like in test_remote.py
        ds = hdf_file['/replica10_chr1/spatial_position/1']
        self.assertIsNotNone(ds)

    @unittest.skipUnless(os.path.exists("test/spleen_1chr1rep.indexed.cndb"), "Test file not found")
    def test_cndb_indexed_with_offset(self):
        config = {
            'path': "test/spleen_1chr1rep.indexed.cndb",
            'indexOffset': 602012432
        }
        hdf_file = open_h5_file(config)
        ds = hdf_file['/replica10_chr1/spatial_position/1']
        self.assertIsNotNone(ds)

    @unittest.skipUnless(os.path.exists("test/spleen_1chr1rep.cndb"), "Test file not found")
    def test_cndb_no_index_local(self):
        config = {'path': "test/spleen_1chr1rep.cndb"}
        hdf_file = open_h5_file(config)
        ds = hdf_file['/replica10_chr1/spatial_position/1']
        self.assertIsNotNone(ds)

    @unittest.skipUnless(os.path.exists("test/spleen_1chr1rep.indexed.cndb"), "Test file not found")
    def test_string_dataset(self):
        config = {'path': "test/spleen_1chr1rep.indexed.cndb"}
        hdf_file = open_h5_file(config)
        typesDataset = hdf_file['/replica10_chr1/types']
        types = typesDataset[:]
        self.assertEqual(len(types), 4980)

if __name__ == '__main__':
    unittest.main()
