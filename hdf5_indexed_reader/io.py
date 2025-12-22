import urllib.request
import io
import requests

class RemoteFile:
    def __init__(self, url, size=None):
        self.url = url
        self._size = size
        self.name = url # For pyfive
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.closed = False

        # Get size if not provided
        if self._size is None:
            # Handle dropbox for size check too
            url_to_check = url
            if "dropbox.com" in url and "dl=0" in url:
                url_to_check = url.replace("dl=0", "dl=1")

            try:
                response = self.session.head(url_to_check, allow_redirects=True)
                if 'Content-Length' in response.headers:
                    self._size = int(response.headers['Content-Length'])
                else:
                    # Try GET with stream=True if HEAD fails to give size
                    response = self.session.get(url_to_check, stream=True, allow_redirects=True)
                    if 'Content-Length' in response.headers:
                         self._size = int(response.headers['Content-Length'])
                    response.close()
            except Exception as e:
                pass

    def read(self, offset, length):
        headers = {"Range": f"bytes={offset}-{offset + length - 1}"}

        if not hasattr(self, 'resolved_url'):
            # Special handling for Dropbox
            url_to_fetch = self.url
            if "dropbox.com" in self.url and "dl=0" in self.url:
                 # Dropbox dl=0 returns an HTML page, we want the binary which dl=1 gives (via redirect)
                 url_to_fetch = self.url.replace("dl=0", "dl=1")

            try:
                # We follow redirects to get the final URL
                # Using session to preserve cookies
                resp = self.session.get(url_to_fetch, stream=True, allow_redirects=True)
                self.resolved_url = resp.url
                resp.close()
            except Exception as e:
                self.resolved_url = self.url # Fallback

        response = self.session.get(self.resolved_url, headers=headers)

        if response.status_code not in [200, 206]:
             # If cached URL expired? Retry once
             try:
                 url_to_fetch = self.url
                 if "dropbox.com" in self.url and "dl=0" in self.url:
                     url_to_fetch = self.url.replace("dl=0", "dl=1")

                 resp = self.session.get(url_to_fetch, stream=True, allow_redirects=True)
                 self.resolved_url = resp.url
                 resp.close()

                 response = self.session.get(self.resolved_url, headers=headers)
             except Exception as e:
                  pass

             if response.status_code not in [200, 206]:
                 raise Exception(f"Error fetching data: {response.status_code}")

        return response.content

    def seek(self, offset):
        self._pos = offset

    def tell(self):
        return self._pos

    def close(self):
        self.closed = True
        self.session.close()

class BufferedFile:
    def __init__(self, file_reader, fetch_size=2000, max_size=200000):
        self.file_reader = file_reader
        self.fetch_size = fetch_size
        self.max_size = max_size
        self._pos = 0
        self.cache = {}
        self.chunks = []
        self.closed = False

    @property
    def name(self):
        return self.file_reader.name

    def seek(self, offset, whence=0):
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            if hasattr(self.file_reader, '_size') and self.file_reader._size is not None:
                self._pos = self.file_reader._size + offset
            else:
                 raise NotImplementedError("Seek from end not supported without size")
        return self._pos

    def tell(self):
        return self._pos

    def read(self, size=-1):
        if size == -1:
            raise NotImplementedError("Read all not supported")

        start = self._pos
        end = start + size

        # Check if we have data in cache
        data = self._read_from_cache(start, size)

        if data is None:
            # Fetch
            fetch_start = start
            fetch_end = end

            # Align fetch_start? Or just fetch at least fetch_size?
            if size < self.fetch_size:
                 fetch_end = start + self.fetch_size

            fetched_data = self.file_reader.read(fetch_start, fetch_end - fetch_start)

            self._add_to_cache(fetch_start, fetched_data)

            # Now read from cache again (it should be there)
            data = self._read_from_cache(start, size)

        self._pos += size
        return data

    def _read_from_cache(self, start, size):
        end = start + size
        for chunk in self.chunks:
            if chunk['start'] <= start and chunk['end'] >= end:
                offset = start - chunk['start']
                return chunk['data'][offset:offset+size]
        return None

    def _add_to_cache(self, start, data):
        end = start + len(data)

        # Remove oldest if total size > max_size
        total_size = sum(len(c['data']) for c in self.chunks)
        while total_size + len(data) > self.max_size and self.chunks:
            removed = self.chunks.pop(0) # FIFO
            total_size -= len(removed['data'])

        self.chunks.append({'start': start, 'end': end, 'data': data})

    def close(self):
        self.closed = True
        if hasattr(self.file_reader, 'close'):
            self.file_reader.close()
