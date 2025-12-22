import unittest
from hdf5_indexed_reader import open_h5_file

class TestLDMATRemote(unittest.TestCase):
    def test_ldmat_remote(self):
        url = "https://www.dropbox.com/s/7243c3327329244/LDMAT_22_22.h5?dl=0"

        print("Opening HDF5 file...")
        hdf_file = open_h5_file({
            'url': url
        })

        print("Getting dataset...")
        dataset = hdf_file['LDMAT_22_22']

        self.assertIsNotNone(dataset)

        print("Checking shape...")
        shape = dataset.shape
        print(f"Shape: {shape}")

        dtype = dataset.dtype
        print(f"Dtype: {dtype}")

        values = dataset[:]
        print(f"Values length: {len(values)}")

        # JS test expects 10000.
        # Let's see what we get.

if __name__ == '__main__':
    unittest.main()
