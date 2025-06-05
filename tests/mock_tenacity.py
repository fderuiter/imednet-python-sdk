class RetryError(Exception):
    """Exception raised when all retry attempts fail."""


class RetryCallState:
    def __init__(self, outcome=None):
        self.outcome = outcome


class Retrying:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class AsyncRetrying:
    def __init__(self, *args, **kwargs):
        pass

    async def __call__(self, func, *args, **kwargs):
        return await func(*args, **kwargs)


def stop_after_attempt(attempts):
    return attempts


def wait_exponential(multiplier=1.0):
    return multiplier
