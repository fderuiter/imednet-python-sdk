class RequestError(Exception):
    """Exception raised for network errors."""


class Response:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.is_error = status_code >= 400

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON data")
        return self._json_data


class Timeout:
    def __init__(self, timeout=None, *, connect=None, read=None, write=None, pool=None):
        if timeout is not None:
            self.connect = self.read = self.write = self.pool = timeout
        else:
            self.connect = connect
            self.read = read
            self.write = write
            self.pool = pool


class Client:
    def __init__(self, base_url=None, headers=None, timeout=None):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout

    def request(self, method, url, **kwargs):
        return Response()

    def close(self):
        pass


class AsyncClient:
    def __init__(self, base_url=None, headers=None, timeout=None):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout

    async def request(self, method, url, **kwargs):
        return Response()

    async def aclose(self):
        pass
