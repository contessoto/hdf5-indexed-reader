import unittest
from hdf5_indexed_reader import open_h5_file

class TestCNDBRemote(unittest.TestCase):
    def test_load_cndb_https(self):
        url = "https://www.dropbox.com/s/53fbs3le4a65noq/spleen_1chr1rep.indexed.cndb?dl=0"

        print("Opening HDF5 file...")
        hdf_file = open_h5_file({
            'url': url
        })

        print("Getting dataset...")
        dataset = hdf_file['/replica10_chr1/spatial_position/1']

        self.assertIsNotNone(dataset)

        print("Checking shape...")
        shape = dataset.shape
        print(f"Shape: {shape}")

        values = dataset[:]
        print(f"Values shape: {values.shape}")
        print(f"Values length: {len(values)}")

        self.assertEqual(len(values), 4980)

if __name__ == '__main__':
    unittest.main()
