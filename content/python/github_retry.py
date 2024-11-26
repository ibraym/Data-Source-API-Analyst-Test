# Copyright: 2024 Ibrahem Mouhamad

from typing import Optional, Any
from types import TracebackType
from typing_extensions import Self
import json
from requests import Response
from requests.utils import get_encoding_from_headers
from requests.models import CaseInsensitiveDict
from urllib3.util import Retry
from urllib3.connectionpool import ConnectionPool
from urllib3.exceptions import MaxRetryError
from urllib3.response import HTTPResponse
from datetime import timezone

from consts import Consts

import logging
logger = logging.getLogger('my_logger')

logging.basicConfig()

class GithubRetry(Retry):

    def __init__(self, secondary_rate_wait: float = Consts['DEFAULT_SECONDARY_RATE_WAIT'], **kwargs: Any) -> None:
        """
        :param secondary_rate_wait: seconds to wait before retrying secondary rate limit errors
        :param kwargs: see urllib3.Retry for more arguments
        """
        self.secondary_rate_wait = secondary_rate_wait
        kwargs["status_forcelist"] = kwargs.get("status_forcelist", list(range(500, 600))) + [403]
        kwargs["allowed_methods"] = kwargs.get("allowed_methods", Retry.DEFAULT_ALLOWED_METHODS.union({"GET", "POST"}))
        super().__init__(**kwargs)

    def new(self, **kw: Any) -> Self:
        kw.update(dict(secondary_rate_wait=self.secondary_rate_wait))
        return super().new(**kw)

    def isRateLimitError(self, message: str) -> bool:
        return self.isPrimaryRateLimitError(message) or self.isSecondaryRateLimitError(message)

    def isPrimaryRateLimitError(self, message: str) -> bool:
        if not message:
            return False

        message = message.lower()
        return message.startswith("api rate limit exceeded")

    def isSecondaryRateLimitError(self, message: str) -> bool:
        if not message:
            return False

        message = message.lower()
        return (
            message.startswith("you have exceeded a secondary rate limit")
            or message.endswith("please retry your request again later.")
            or message.endswith("please wait a few minutes before you try again.")
        )

    def increment( 
        self,
        method: Optional[str] = None,
        url: Optional[str] = None,
        response: Optional[HTTPResponse] = None,
        error: Optional[Exception] = None,
        _pool: Optional[ConnectionPool] = None,
        _stacktrace: Optional[TracebackType] = None,
    ) -> Retry:
        if response:
            if response.status == 403:
                if "Retry-After" in response.headers:
                    # Sleeping 'Retry-After' seconds is implemented in urllib3.Retry.sleep() and called by urllib3
                    logger.info(f'Retrying after {response.headers.get("Retry-After")} seconds')
                else:
                    content = response.reason
                    # to identify retry-able methods, we inspect the response body
                    try:
                        content = self.get_content(response, url)  # type: ignore
                        content = json.loads(content)  # type: ignore
                        message = content.get("message")  # type: ignore
                    except Exception as e:
                        raise RuntimeError("Failed to inspect response message") from e

                    try:
                        if self.isRateLimitError(message):

                            # check early that we are retrying at all
                            retry = super().increment(method, url, response, error, _pool, _stacktrace)

                            # we backoff primary rate limit at least until X-RateLimit-Reset,
                            # we backoff secondary rate limit at for secondary_rate_wait seconds
                            backoff = 0.0

                            if self.isPrimaryRateLimitError(message):
                                if Consts['headerRateReset'] in response.headers:
                                    value = response.headers.get(Consts['headerRateReset'])
                                    if value and value.isdigit():
                                        reset = self.__datetime.fromtimestamp(int(value), timezone.utc)
                                        delta = reset - self.__datetime.now(timezone.utc)
                                        resetBackoff = delta.total_seconds()

                                        if resetBackoff > 0:
                                            logger.debug(f"Reset occurs in {str(delta)} ({value} / {reset})")

                                        # plus 1s as it is not clear when in that second the reset occurs
                                        backoff = resetBackoff + 1
                            else:
                                backoff = self.secondary_rate_wait

                            # we backoff at least retry's next backoff
                            retry_backoff = retry.get_backoff_time()
                            if retry_backoff > backoff:
                                if backoff > 0:
                                    logger.debug(
                                        f"Retry backoff of {retry_backoff}s exceeds "
                                        f"required rate limit backoff of {backoff}s".replace(".0s", "s"),
                                    )
                                backoff = retry_backoff

                            def get_backoff_time() -> float:
                                return backoff

                            logger.info(
                                f"Setting next backoff to {backoff}s".replace(".0s", "s"),
                            )
                            retry.get_backoff_time = get_backoff_time  # type: ignore
                            return retry

                        logger.debug(
                            "Response message does not indicate retry-able error",
                        )
                        raise Exception(f'{response.status} {content}')  # type: ignore
                    except MaxRetryError:
                        raise
                    except Exception as e:
                        raise RuntimeError("Failed to determine retry backoff") from e

                    raise Exception(f'{response.status} {content}') 

        # retry the request as usual
        return super().increment(method, url, response, error, _pool, _stacktrace)

    @staticmethod
    def get_content(resp: HTTPResponse, url: str) -> bytes:
        # logic taken from HTTPAdapter.build_response (requests.adapters)
        response = Response()

        # Fallback to None if there's no status_code, for whatever reason.
        response.status_code = getattr(resp, "status", None)  # type: ignore

        # Make headers case-insensitive.
        response.headers = CaseInsensitiveDict(getattr(resp, "headers", {}))

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason  # type: ignore

        response.url = url

        return response.content
