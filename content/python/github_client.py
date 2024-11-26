default_retry = GithubRetry()

class Github:
    """
    The main class to access the GitHub API v3.
    Provides methods for performing authenticated API requests and managing paginated responses.
    """

    def __init__(
        self,
        auth: Auth,
        base_url: str = Consts['DEFAULT_BASE_URL'],
        timeout: int = Consts['DEFAULT_TIMEOUT'],
        user_agent: str = Consts['DEFAULT_USER_AGENT'],
        per_page: int = Consts['DEFAULT_PER_PAGE'],
        verify: bool | str = True,
        retry: int | Retry | None = default_retry,
        seconds_between_requests: float | None = Consts['DEFAULT_SECONDS_BETWEEN_REQUESTS'],
    )-> None:
        """
        Initialize the GitHub API client.

        :param auth: An instance of the `Auth` class for authentication.
        :param base_url: Base URL for GitHub API (defaults to `Consts['DEFAULT_BASE_URL']`).
        :param timeout: Timeout for API requests in seconds.
        :param user_agent: User agent string for the client.
        :param per_page: Number of items per page for paginated responses.
        :param verify: SSL verification (can be `True`, `False`, or a path to a CA_BUNDLE file).
        :param retry: Retry configuration, either an integer or a `Retry` object.
        :param seconds_between_requests: Minimum delay between requests to avoid rate-limiting.
        """
        assert isinstance(auth, Auth), auth
        assert isinstance(timeout, int), timeout
        assert user_agent is None or isinstance(user_agent, str), user_agent
        assert isinstance(per_page, int), per_page
        assert isinstance(verify, (bool, str)), verify
        assert retry is None or isinstance(retry, int) or isinstance(retry, urllib3.util.Retry), retry
        assert seconds_between_requests is None or seconds_between_requests >= 0

        self.__auth = auth
        self.__base_url = base_url

        o = urllib.parse.urlparse(base_url)
        assert o.scheme == 'https'
        self.__hostname = o.hostname
        self.__port = o.port
        self.__prefix = o.path

        self.__timeout = timeout
        self.__retry = retry
        self.__seconds_between_requests = seconds_between_requests
        self.__connection = None

        self.rate_limiting = (-1, -1)
        self.rate_limiting_resettime = 0
        self.per_page = per_page

        assert user_agent is not None # github now requires a user-agent.
        self.__userAgent = user_agent
        self.__verify = verify
        self.__last_requests: Dict[str, float] = dict()

    def __getConnection(self):
        """
        Create and configure the HTTP connection object if it does not already exist.

        :return: Configured HTTPS connection object.
        """
        if self.__connection is not None:
            return self.__connection

        return HTTPSRequestsConnectionClass(
            self.__hostname,
            self.__port,
            retry=self.__retry,
            timeout=self.__timeout,
            verify=self.__verify,
        )

    def __deferRequest(self) -> None:
        """
        Enforce a delay between consecutive requests to respect the API's rate limits.
        """
        requests = self.__last_requests.values()

        last_request = max(requests) if requests else 0

        next_request = (last_request + self.__seconds_between_requests) if self.__seconds_between_requests else 0

        defer = max(next_request - datetime.now(timezone.utc).timestamp(), 0)
        time.sleep(defer)

    def __send_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        input: Optional[Any] = None,
    ):
        """
        Send an HTTP request using the configured connection.

        :param method: HTTP method (e.g., "GET", "POST").
        :param url: The target URL for the request.
        :param headers: Dictionary of HTTP headers for the request.
        :param input: Optional payload or body for the request.
        :return: Tuple containing status, response headers, and response content.
        """
        self.__deferRequest()

        try:
            self.__connection = self.__getConnection()

            self.__connection.request(method, url, input, headers)
            response = self.__connection.getresponse()

            status = response.status
            responseHeaders = {k.lower(): v for k, v in response.getheaders()}
            output = response.read()

            return status, responseHeaders, output
        finally:
            self.__last_requests[method] = datetime.now(timezone.utc).timestamp()

    def __makeAbsoluteUrl(self, url: str) -> str:
        """
        Convert a relative URL to an absolute URL based on the base URL.

        :param url: Relative or absolute URL.
        :return: Fully qualified absolute URL.
        """
        if url.startswith("/"):
            url = f"{self.__prefix}{url}"
        else:
            o = urllib.parse.urlparse(url)
            assert o.hostname in [
                self.__hostname,
                "uploads.github.com",
                "status.github.com",
                "github.com",
            ], o.hostname
            assert o.path.startswith((self.__prefix, "/api/", "/login/oauth")), o.path
            assert o.port == self.__port, o.port
            url = o.path
            if o.query != "":
                url += f"?{o.query}"
        return url

    def __check_response(
        self,
        status: int,
        responseHeaders: Dict[str, Any],
        output: str,
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Check the API response for errors and decode the response content.

        :param status: HTTP status code.
        :param responseHeaders: Dictionary of HTTP response headers.
        :param output: Raw response content.
        :return: Decoded response data (JSON if applicable).
        """
        data = output
        is_JSON = False
        if isinstance(output, bytes):
            data = output.decode('utf-8')
        if status >= 400:
            raise Exception(f'{status} {data}')
        if 'content-type' in responseHeaders:
            if Consts['headerRawJSON'] in responseHeaders['content-type'] or \
               Consts['headerHtmlJSON'] in responseHeaders['content-type']:
                return responseHeaders, data
        if len(data) == 0:
            return None
        else:
            try:
                data = json.loads(data)
            except ValueError:
                raise
        return responseHeaders, data


    def __get(self,
        url: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Perform a GET request to the GitHub API.

        :param url: Target URL for the request.
        :param parameters: Optional query parameters for the request.
        :param headers: Optional HTTP headers for the request.
        :return: Tuple containing response headers and data.
        """
        if parameters is None:
            parameters = {}
        if headers is None:
            headers = {}
        if self.__auth is not None:
            self.__auth.authentication(headers)
        headers['User-Agent'] = self.__userAgent

        url = self.__makeAbsoluteUrl(url)
        url = add_parameters_to_url(url, parameters)

        status, responseHeaders, output = self.__send_request('get', url, headers)

        if Consts['headerRateRemaining'] in responseHeaders and Consts['headerRateLimit'] in responseHeaders:
            self.rate_limiting = (
                int(float(responseHeaders[Consts['headerRateRemaining']])),
                int(float(responseHeaders[Consts['headerRateLimit']])),
            )
        if Consts['headerRateReset'] in responseHeaders:
            self.rate_limiting_resettime = int(float(responseHeaders[Consts['headerRateReset']]))

        return self.__check_response(status, responseHeaders, output)

    def paginator(self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Union[str, int]]] = None) -> Iterator[Dict] | str:
        """
        Create a generator to iterate over paginated results.

        :param url: API endpoint URL.
        :param params: Query parameters for the request.
        :param headers: HTTP headers for the request.
        :return: Iterator yielding items from all pages.
        """
        nextParams: Dict[str, Any] = params or {}
        nextUrl = url
        if self.per_page != 30:
            nextParams['per_page'] = self.per_page
        while nextUrl is not None:
            headers, data = self.__get(nextUrl, nextParams, headers)
            data = data if data else []
            nextUrl = None
            if len(data) > 0:
                links = parseLinkHeader(headers)
                if "next" in links:
                    nextUrl = links["next"]
            nextParams = {}
            if 'items' in data:
                totalCount = data.get('total_count')
                data = data['items']
            if 'content-type' in headers:
                if Consts['headerRawJSON'] in headers['content-type'] or \
                    Consts['headerHtmlJSON'] in headers['content-type']:
                    content = data
                    yield content
            else:
                content = [
                    element
                    for element in data
                    if element is not None
                ]
                yield from content


    def close(self) -> None:
        """
        Close the API client's connection to the server.
        """
        self.__connection.close()

    def search_repositories(
        self,
        query: str,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        qualifiers: Optional[Dict] = None,
    ) -> Iterator[Dict]:
        """
        :calls: `GET /search/repositories <https://docs.github.com/en/rest/reference/search>`
        :param query: string
        :param sort: string ('stars', 'forks', 'updated')
        :param order: string ('asc', 'desc')
        :param qualifiers: dict query qualifiers
        """
        assert isinstance(query, str), query
        url_parameters = dict()
        if sort is not None:
            assert sort in ("stars", "forks", "updated"), sort
            url_parameters["sort"] = sort
        if order is not None:
            assert order in ("asc", "desc"), order
            url_parameters["order"] = order

        query_chunks = []
        if query:
            query_chunks.append(query)

        for qualifier, value in qualifiers.items():
            query_chunks.append(f"{qualifier}:{value}")

        url_parameters["q"] = " ".join(query_chunks)
        assert url_parameters["q"], "need at least one qualifier"

        return self.paginator(
            "/search/repositories",
            url_parameters,
        )

    def commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        committer: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Iterator[Dict]:
        """
        Retrieve a list of commits for a repository.

        :param owner: The GitHub username or organization that owns the repository.
        :param repo: The name of the repository.
        :param sha: Optional. The SHA or branch to start listing commits from.
        :param path: Optional. Restrict results to commits that affect the specified file or directory path.
        :param author: Optional. Filter commits by a specific author, using their GitHub username or email address.
        :param committer: Optional. Filter commits by a specific committer, using their GitHub username or email address.
        :param since: Optional. ISO 8601 date string to filter commits after the specified date.
        :param until: Optional. ISO 8601 date string to filter commits before the specified date.
        :return: An iterator over dictionaries, where each dictionary represents a commit object.

        **Example Usage:**

        ```python
        commits = github.commits(
            owner="octocat",
            repo="Hello-World",
            sha="main",
            since="2023-01-01T00:00:00Z",
            until="2023-12-31T23:59:59Z",
        )
        for commit in commits:
            print(commit["sha"])
        ```

        **Filters:**
        - `sha`: Retrieves commits starting from a specific branch or commit.
        - `path`: Limits the results to a specific file or directory.
        - `author` / `committer`: Filters results based on the author's or committer's identity.
        - `since` / `until`: Limits the results to a specific time range using ISO 8601 date strings (e.g., `"2023-01-01T00:00:00Z"`).

        **Notes:**
        - Ensure `since` and `until` are valid ISO 8601 date strings.
        - The method returns an iterator, so it efficiently handles paginated responses from the GitHub API.
        """
        assert isinstance(owner, str), owner
        assert isinstance(repo, str), repo
        url_parameters = dict()
        if sha is not None:
            assert isinstance(sha, str), sha
            url_parameters["sha"] = sha
        if path is not None:
            assert isinstance(path, str), path
            url_parameters["path"] = path
        if author is not None:
            assert isinstance(author, str), author
            url_parameters["author"] = author
        if committer is not None:
            assert isinstance(committer, str), committer
            url_parameters["committer"] = committer
        if since is not None:
            assert isinstance(since, str) and is_iso_format(since), since
            url_parameters["since"] = since
        if until is not None:
            assert isinstance(until, str) and is_iso_format(until), until
            url_parameters["until"] = until
        return self.paginator(
            f"/repos/{owner}/{repo}/commits",
            url_parameters,
        )
      
    def contents(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Iterator[Dict] | str:
        """
        Retrieve the content of a file or directory in a repository.

        :param owner: The GitHub username or organization that owns the repository.
        :param repo: The name of the repository.
        :param path: The path to the file or directory within the repository.
        :param ref: Optional. The name of the commit/branch/tag. Defaults to the repository's default branch (usually `main`).
        :param content_type: Optional. Specifies the format of the returned content. 
                            Must be one of `'raw'`, `'html'`, or `'object'`. 
                            - `'raw'`: Returns raw content.
                            - `'html'`: Returns content rendered as HTML.
                            - `'object'`: Returns a JSON representation of the object.
        :return: An iterator over dictionaries, where each dictionary represents the content of the specified path.

        **Notes:**
        - The `path` parameter can refer to either a file or a directory.
        - If `ref` is not provided, the method retrieves content from the repository's default branch.
        - Use `content_type` to control how the content is returned (raw bytes, HTML, or JSON object).
        - This method supports paginated responses for directories containing multiple items.

        **Headers:**
        - If `content_type` is specified, custom `Accept` headers are added to define the desired response format.
        - For `'raw'`, the header `application/vnd.github.raw` is used.
        - For `'html'`, the header `application/vnd.github.html` is used.
        - For `'object'`, the header `application/vnd.github.object` is used.
        """
        assert isinstance(owner, str), owner
        assert isinstance(repo, str), repo
        assert isinstance(path, str), path
        url_parameters = dict()
        if ref is not None:
            assert isinstance(ref, str), ref
            url_parameters["ref"] = ref
        headers: Optional[Dict[str, str]] = None
        if content_type is not None:
            assert content_type in ['raw', 'html', 'object'], content_type
            if content_type == 'raw':
                headers = {'Accept': Consts['headerRawJSON']}
            if content_type == 'html':
                headers = {'Accept': Consts['headerHtmlJSON']}
            if content_type == 'object':
                headers = {'Accept': Consts['headerObjectJSON']}

        return self.paginator(
            f"/repos/{owner}/{repo}/contents/{path}",
            url_parameters,
            headers=headers,
        )
