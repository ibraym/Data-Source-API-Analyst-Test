# Copyright: 2024 Ibrahem Mouhamad

from typing import Optional, Any, Dict, Union, ItemsView
import requests
from urllib3.util import Retry
import io

import logging
logger = logging.getLogger('my_logger')

logging.basicConfig()

class RequestsResponse:
    """
    A wrapper for `requests.Response` to mimic the `httplib` response object.

    Attributes:
        status (int): The HTTP status code of the response.
        headers (requests.structures.CaseInsensitiveDict): The headers of the response.
        text (str): The text content of the response.
    """
    def __init__(self, r: requests.Response):
        """
        Initializes the RequestsResponse object with the provided requests.Response.

        Args:
            r (requests.Response): The response object to wrap.
        """
        self.status = r.status_code
        self.headers = r.headers
        self.text = r.text

    def getheaders(self) -> ItemsView[str, str]:
        """
        Returns the headers of the response as an ItemsView.

        Returns:
            ItemsView[str, str]: The headers of the response.
        """
        return self.headers.items()

    def read(self) -> str:
        """
        Returns the text content of the response.

        Returns:
            str: The response body.
        """
        return self.text

def noopAuth(request: requests.models.PreparedRequest) -> requests.models.PreparedRequest:
    """
    A no-operation authentication handler for requests.

    Args:
        request (requests.models.PreparedRequest): The request object.

    Returns:
        requests.models.PreparedRequest: The unchanged request object.
    """
    return request

class HTTPSRequestsConnectionClass:
    retry: Union[int, Retry]

    """
    Mimics an `httplib` connection object using the `requests` library.

    Attributes:
        host (str): The target host for the connection.
        port (int): The port number for the connection (default is 443 for HTTPS).
        protocol (str): The protocol used, fixed to "https".
        timeout (Optional[int]): The timeout for requests, if any.
        verify (bool): Whether to verify SSL certificates (default is True).
        session (requests.Session): The requests session object used for connections.
        retry (Union[int, Retry]): The retry configuration for the HTTPAdapter.
        pool_size (int): The maximum number of connections for the pool.
    """
    def __init__(
        self,
        host: str,
        port: Optional[int] = None,
        strict: bool = False,
        timeout: Optional[int] = None,
        retry: Optional[Union[int, Retry]] = None,
        pool_size: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the HTTPSRequestsConnectionClass with the given configuration.

        Args:
            host (str): The target host for the connection.
            port (Optional[int]): The port for the connection. Defaults to 443.
            strict (bool): Unused parameter included for API compatibility.
            timeout (Optional[int]): The request timeout in seconds.
            retry (Optional[Union[int, Retry]]): Retry configuration or number of retries.
            pool_size (Optional[int]): The maximum size of the connection pool.
            **kwargs (Any): Additional arguments, such as SSL verification flags.
        """
        self.port = port if port else 443
        self.host = host
        self.protocol = "https"
        self.timeout = timeout
        self.verify = kwargs.get("verify", True)
        self.session = requests.Session()

        self.session.auth = noopAuth

        if retry is None:
            self.retry = requests.adapters.DEFAULT_RETRIES
        else:
            self.retry = retry

        if pool_size is None:
            self.pool_size = requests.adapters.DEFAULT_POOLSIZE
        else:
            self.pool_size = pool_size

        self.adapter = requests.adapters.HTTPAdapter(
            max_retries=self.retry,
            pool_connections=self.pool_size,
            pool_maxsize=self.pool_size,
        )
        self.session.mount("https://", self.adapter)

    def request(
        self,
        verb: str,
        url: str,
        input: Optional[Union[str, io.BufferedReader]],
        headers: Dict[str, str],
    ) -> None:
        """
        Prepares a request to be executed.

        Args:
            verb (str): The HTTP method (e.g., "GET", "POST").
            url (str): The URL path for the request.
            input (Optional[Union[str, io.BufferedReader]]): The request body, if any.
            headers (Dict[str, str]): The headers for the request.
        """
        self.verb = verb
        self.url = url
        self.input = input
        self.headers = headers

    def getresponse(self) -> RequestsResponse:
        """
        Executes the prepared request and returns the response.

        Returns:
            RequestsResponse: The wrapped response object.
        """
        verb = getattr(self.session, self.verb.lower())
        url = f"{self.protocol}://{self.host}:{self.port}{self.url}"
        r = verb(
            url,
            headers=self.headers,
            data=self.input,
            timeout=self.timeout,
            verify=self.verify,
            allow_redirects=False,
        )
        return RequestsResponse(r)

    def close(self) -> None:
        """
        Closes the session and cleans up resources.
        """
        self.session.close()
