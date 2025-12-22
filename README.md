# hdf5-indexed-reader (Python)

## Summary

`hdf5-indexed-reader` is a Python package for efficient querying of HDF5 files over the web. It enables loading of individual
datasets from remote files without the need to load the entire file into memory. It works in
conjunction with the companion project [hdf5-indexer](https://github.com/jrobinso/hdf5-indexer), which annotates
HDF5 files with an index mapping object path names to file offsets.

This package is a Python port of the original JavaScript module, built on a vendored and modified version of [pyfive](https://github.com/jjhelmus/pyfive).

## Motivation

The driving use case for this project involves extracting individual datasets for visualization (or analysis)
from large HDF5 files (~200 GB) containing 10s of thousands of individual datasets. Loading such files over
the web with available solutions present 2 problems:

* The file is too large to load into memory in its entirety.
* Finding the file offset for the object desired involves walking a linked list of nodes of containing and sibling
  objects. These nodes can be located anywhere in the file, resulting in an explosion of HTTP range requests which can quickly
  slow down the application.

This project addresses these issues by (1) using range queries to load slices of the file as needed, and (2) supporting
a pre-built index for mapping object (groups and datasets) paths to file offsets, negating the need to walk the
linked list of container objects to build the index at runtime.

## Installation

Clone the repository and install the dependencies:

```bash
git clone <repository-url>
cd hdf5-indexed-reader
pip install -r requirements.txt
```

Dependencies:
* `numpy`
* `requests`

## Usage

The module exports a function `open_h5_file(options)`. The HDF5 file is specified with one of the following options:

* `url`: URL to the HDF5 file (supports HTTP/HTTPS).
* `path`: Local file path.
* `file`: File-like object (must support `read` and `seek`).

URL fetches are cached to avoid separate individual requests for small amounts of data. The following optional properties control the cache:

* `fetchSize`: Minimum size in bytes for each HTTP request. Defaults to 2000 (2 kb).
* `maxSize`: The maximum number of bytes to cache. Default value is 200000 (200 kb).

In cases where it is not possible to modify the HDF5 file, [hdf5-indexer](https://github.com/jrobinso/hdf5-indexer) can create an external index as a JSON file. This file can be used with one of the following properties:

* `indexURL`: URL to index JSON file.
* `indexPath`: Local file path to index JSON file.
* `index`: Dictionary containing the index data.
* `indexOffset`: Byte offset to the index if embedded in the file but not automatically detected.

### Example

Load a `Dataset` from a remote HDF5 file and fetch its shape, data type, and values.

```python
from hdf5_indexed_reader import open_h5_file

# Open remote file
hdf_file = open_h5_file({
    "url": "https://www.dropbox.com/s/53fbs3le4a65noq/spleen_1chr1rep.indexed.cndb?dl=0",
})

# Access dataset
# Note: You can use dictionary-style access or path strings
dataset = hdf_file['/replica10_chr1/spatial_position/1149']

# Get properties
print("Shape:", dataset.shape)
print("Dtype:", dataset.dtype)

# Fetch values (returns a numpy array)
values = dataset[:]
print("Values shape:", values.shape)
print("First value:", values[0])
```

## CLI Usage

A helper script `run_reader.py` is included to easily test and inspect HDF5 files from the command line.

```bash
# Print root keys of a remote file
python run_reader.py --url "https://www.dropbox.com/s/53fbs3le4a65noq/spleen_1chr1rep.indexed.cndb?dl=0"

# Fetch and preview a specific dataset
python run_reader.py \
  --url "https://www.dropbox.com/s/53fbs3le4a65noq/spleen_1chr1rep.indexed.cndb?dl=0" \
  --dataset /replica10_chr1/spatial_position/1
```

## Testing

Unit tests are provided using Python's `unittest` framework.

```bash
# Run all tests
python -m unittest discover . "test_*.py"

# Run specific remote test
python test_remote.py
```

## Limitations

* As this project relies on a modified version of `pyfive`, it inherits `pyfive`'s limitations (e.g., read-only support, limited support for some complex HDF5 features compared to `h5py` which binds to the C library).
* Designed primarily for large HDF5 files with many datasets where index-based access significantly improves performance over network connections.
