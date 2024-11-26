# Data-Source-API-Analyst-Test

The goal of this repository is to provide an analysis of [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28) including authentication methods, requests logic, pagination, rate limits and error handling.

## Scope
Based on the client needs, we are interested in the following endpoints:

1. [Search Repositories (public)](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories): \
[GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28) provides the `/search` endpoint that can be used search for specific item. We can search for `commits`, `issues`, `labels`, ...etc. To search for repositories, we should use `/search/repositories`.

2. [Commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28): To get a list of commits of a specific `repo` owned by a specific user `owner` from [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28), we should use `/repos/{owner}/{repo}/commits` endpoint.

3. [Contents](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28): To get the contents of a file or a directory, referenced by `path` query parameter, of a specific `repo` owned by a specific user `owner` from [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28), we should use `/repos/{owner}/{repo}/contents/{path}` endpoint.

## Reports
We researched the documentation to gather information about the required endpoints and how call and get data from the API.

1. API documentation:
    1. [Authentication](./content/docs/auth.md)
    2. [Rate Limits](./content/docs/rate-limits.md)
    3. [Pagination](./content/docs/pagination.md)
    4. [Search Repositories (public)](./content/docs/search_repos.md)
    5. [Commits](./content/docs/commits.md)
    6. [Contents](./content/docs/contents.md)
    7. [Troubleshooting Guide](./content/docs/troubleshooting.md)

2. Code:
we prepared a [Jupyter notebook](./content/jupyter_notebook/) that contains the step by step documentation of each function/class we have developed to handle authentication, pagination, rate limits and error handling. It also include some example of how requesting and extracting data from the API.


### Key features of our implementation:
   - Authentication: Integrates with the Auth class to handle token-based authentication.
   - Rate Limit Management: Tracks and enforces API rate limits to avoid throttling.
   - Retry Strategy: Handles retries for network errors and rate-limit responses.
   - Pagination: Simplifies handling of paginated API responses.
   - Extensibility: Designed for integration with additional API endpoints and functionalities.

### Types of Errors Handled
   - Automatic Retry on Rate Limit Exceeded: The `GithubRetry` class manages retries for both primary and secondary rate limit errors, with intelligent backoff strategies.
   - Response Validation: The `__check_response` method in `Github` class raises exceptions for HTTP errors (status codes >= 400) and handles both JSON decoding errors and invalid API responses.
   - Timeouts and Connection Errors: The connection logic includes built-in retries and timeouts.
   - Customizable Retry and Timeout Logic: The `Github` class allows configuration of retry behavior and request timeouts to customize error handling according to needs.
   - Detailed Error Messages: The `Github` class provides detailed error messages that include HTTP status codes and response content to help diagnose issues.
