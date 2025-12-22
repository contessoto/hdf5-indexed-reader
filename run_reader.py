import argparse
import sys
import numpy as np
from hdf5_indexed_reader import open_h5_file

def main():
    parser = argparse.ArgumentParser(description="Read HDF5 files from remote URL or local path using hdf5-indexed-reader.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL of the HDF5 file")
    group.add_argument("--path", help="Local path of the HDF5 file")

    parser.add_argument("--dataset", help="Path to the dataset within the HDF5 file (e.g., /group/dataset)")
    parser.add_argument("--index-url", help="URL of the external index JSON file (optional)")
    parser.add_argument("--index-path", help="Local path of the external index JSON file (optional)")

    args = parser.parse_args()

    options = {}
    if args.url:
        options['url'] = args.url
    if args.path:
        options['path'] = args.path
    if args.index_url:
        options['indexURL'] = args.index_url
    if args.index_path:
        options['indexPath'] = args.index_path

    try:
        print(f"Opening {args.url if args.url else args.path}...")
        f = open_h5_file(options)

        if args.dataset:
            print(f"Fetching dataset: {args.dataset}")
            if args.dataset not in f:
                 # Try with/without leading slash
                 if args.dataset.startswith('/') and args.dataset[1:] in f:
                     dataset_path = args.dataset[1:]
                 elif '/' + args.dataset in f:
                     dataset_path = '/' + args.dataset
                 else:
                     # It might be deep inside
                     dataset_path = args.dataset
            else:
                dataset_path = args.dataset

            try:
                dset = f[dataset_path]
                # Check if it is a dataset or group
                # pyfive Group objects have keys(), Dataset objects have shape/dtype
                if hasattr(dset, 'shape') and not hasattr(dset, 'keys'):
                    print(f"Shape: {dset.shape}")
                    print(f"Dtype: {dset.dtype}")

                    # Be careful with printing values if it is huge
                    size = np.prod(dset.shape)
                    if size < 100:
                        print(f"Values: {dset[:]}")
                    else:
                        print(f"Values (preview): {dset[:min(10, size)]} ...")
                else:
                    print(f"Object is a Group (or unknown). Keys: {list(dset.keys())}")

            except KeyError:
                print(f"Error: Dataset '{args.dataset}' not found.")
                print(f"Available root keys: {list(f.keys())}")
            except Exception as e:
                print(f"Error accessing dataset: {e}")
        else:
            print("No dataset specified. Root keys:")
            print(list(f.keys()))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
