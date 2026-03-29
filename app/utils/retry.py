import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


def http_retry():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.HTTPError, TimeoutError)),
        reraise=True,
    )
