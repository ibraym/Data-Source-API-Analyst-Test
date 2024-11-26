# Commits

To get a list of commits of a specific `repo` owned by a specific user `owner` from [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28), we should use `/repos/{owner}/{repo}/commits` endpoint.


## Rate Limit
This endpoint does not have a custom rate limits, so the default rate limits explained [here](./rate-limits.md) are applied.

## Headers
   - `Accept` header: can take one of the following values:
      - `application/vnd.github+json` recommended.
   - `Authorization` header.
   - `X-GitHub-Api-Version` header.

## Path parameters
Both parameters are not case sensitive.
   - `owner`: the repository's owner.
   - `repo`: The name of the repository without the .git extension.

## Query parameters
All query parameters are optional.
   - `sha`: SHA or branch to start listing commits from. Default: the repository’s default branch (usually `main`).
   - `path`: Only commits containing this file path will be returned.
   - `author`: GitHub username or email address to use to filter by commit author.
   - `committer`: GitHub username or email address to use to filter by commit committer.
   - `since`: Only show results that were last updated after the given time. This is a timestamp in ISO 8601 format.
   - `until`: Only commits before this date will be returned. This is a timestamp in ISO 8601 format.
   - `per_page`: The number of results per page (max 100), default is `30`.
   - `page`: The page number of the results to fetch, default is '1'

## Response Codes
   - `200`: OK
   - `400`: Bad request
   - `404`: Resource not found
   - `409`: Conflict
   - `503`: Internal Error

## Results
It returns JSON objects with `type` and `items` keys. `items` value is a list of commits. `type` is `array` string.
