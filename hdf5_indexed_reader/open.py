import json
import requests
import os
from .io import RemoteFile, BufferedFile
from .pyfive.high_level import File

def open_h5_file(options):
    """
    options: dict with keys:
      - url: str
      - path: str (local)
      - file: file-like object
      - fetchSize: int
      - maxSize: int
      - index: dict (optional)
      - indexURL: str (optional)
      - indexPath: str (optional)
      - indexFile: file-like (optional)
      - indexOffset: int (optional)
    """

    url = options.get('url')
    path = options.get('path')
    file_obj = options.get('file')

    fetch_size = options.get('fetchSize', 2000)
    max_size = options.get('maxSize', 200000)

    file_reader = None

    if url:
        file_reader = RemoteFile(url)
        # Wrap in BufferedFile
        file_reader = BufferedFile(file_reader, fetch_size=fetch_size, max_size=max_size)
    elif path:
        file_reader = open(path, 'rb')
        # Local file usually doesn't need buffering as OS handles it, but consistency?
        # Pyfive expects a file-like object.
    elif file_obj:
        file_reader = file_obj
    else:
        raise ValueError("One of 'url', 'path', or 'file' must be specified")

    # Load index
    index = read_external_index(options)
    index_offset = options.get('indexOffset')

    # Create HDF5 file
    # file_reader needs to look like a file to pyfive
    # RemoteFile/BufferedFile implement read(size) and seek.
    # But pyfive might expect different signature for read?
    # Pyfive expects read(n) and seek(offset).
    # My BufferedFile implements read(size) and seek(offset, whence).
    # This should be compatible.

    # Note: File constructor in modified pyfive accepts index and index_offset
    return File(file_reader, index=index, index_offset=index_offset)

def read_external_index(options):
    if options.get('index'):
        return options['index']

    index_url = options.get('indexURL')
    index_path = options.get('indexPath')
    # indexFile support omitted for now as it's browser specific usually

    index_content = None

    if index_url:
        response = requests.get(index_url)
        if response.status_code == 200:
             return response.json()
        else:
             raise Exception(f"Failed to load index from {index_url}")
    elif index_path:
        with open(index_path, 'r') as f:
            return json.load(f)

    return None
