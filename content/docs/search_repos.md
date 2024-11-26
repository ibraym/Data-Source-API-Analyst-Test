# Search repositories (public)

As we only need public repos, this endpoint can be used without authentication. It returns up to `100` results per page.

## Rate Limit
   - For authenticated requests, up to `30` requests per minute.
   - For unauthenticated requests, up to `10` requests per minute.

## Headers
   - `Accept` header: can take one of the following values:
      - `application/vnd.github+json` recommended.
      - `application/vnd.github.text-match+json` to return additional metadata that allows us to highlight the matching search terms when displaying search results. See [Text match metadata](https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#text-match-metadata) for more details.
   - `Authorization` header (not required) for public search, but we will have lower rate limit.
   - `X-GitHub-Api-Version` header.

## Query parameters
`q` query parameters is required, the other parameters are optional.
   - `q`: The query contains one or more search keywords and qualifiers. a query can contain any combination of search qualifiers supported on GitHub. The format of the search query is:
   ```
   SEARCH_KEYWORD_1 SEARCH_KEYWORD_N QUALIFIER_1 QUALIFIER_N
   ```
   See [Searching on GitHub](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories) for a complete list of available qualifiers for search repositories, their format, and an example of how to use them.
   > query length should be longer than 256 characters (not including operators or qualifiers). \
   > query length should not have more than five AND, OR, or NOT operators.
   - `sort`: Can be one of: `stars`, `forks`, `help-wanted-issues`, `updated`. By default results are sorted by best match in descending order.
   - order: Can be one of: `desc`, `asc`, default to `desc`. This parameter is ignored unless `sort` provided.
   - `per_page`: The number of results per page (max 100), default is `30`.
   - `page`: The page number of the results to fetch, default is '1'

## Response Codes
   - `200`: OK
   - `304`: Not modified
   - `422`: Validation failed, or the endpoint has been spammed.
   - `503`: Service unavailable

## Results
It returns JSON objects with `total_count`, `incomplete_results`, and `items` keys. `items` value is a list of repositories. `incomplete_results=true` means that the query exceed the time limit to run a query.
