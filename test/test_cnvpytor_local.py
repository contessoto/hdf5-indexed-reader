import unittest
import os
from hdf5_indexed_reader import open_h5_file

class TestCnvpytorLocal(unittest.TestCase):
    @unittest.skipUnless(os.path.exists("test/vcf_cnv.pytor"), "Test file not found")
    def test_chromosome_names(self):
        config = {'path': "test/vcf_cnv.pytor"}

        hdf_file = open_h5_file(config)

        chr_ds = hdf_file['rd_chromosomes']
        rd_chromosomes = chr_ds[:]

        self.assertEqual(len(rd_chromosomes), 25)
        names = set(x.decode('utf-8') if isinstance(x, bytes) else x for x in rd_chromosomes)

        for i in range(1, 23):
            n = f"chr{i}"
            self.assertIn(n, names)

        self.assertIn("chrX", names)
        self.assertIn("chrY", names)
        self.assertIn("chrM", names)

if __name__ == '__main__':
    unittest.main()
