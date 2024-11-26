# Commits

To get the contents of a file or a directory, referenced by `path` query parameter, of a specific `repo` owned by a specific user `owner` from [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28), we should use `/repos/{owner}/{repo}/contents/{path}` endpoint.


## Rate Limit
This endpoint does not have a custom rate limits, so the default rate limits explained [here](./rate-limits.md) are applied.

## Headers
   - `Accept` header: can take one of the following values:
      - `application/vnd.github+json` recommended.
      - `application/vnd.github.raw+json` to return the raw file contents.
      - `application/vnd.github.html+json` to return the file contents in HTML.
      - `application/vnd.github.object+json` to return the contents in one object. If the contents contain an array of files, the object will contains an entries attribute for them.
   - `Authorization` header.
   - `X-GitHub-Api-Version` header.

## Path parameters
`owner` and `repo` parameters are not case sensitive.
   - `owner`: the repository's owner.
   - `repo`: The name of the repository without the .git extension.
   - `path`: path to the file or directory.

## Query parameters
All query parameters are optional.
   - `ref`: The name of the commit/branch/tag. Default: the repository’s default branch (usually `main`).

## Response Codes
   - `200`: OK
   - `302`: Found
   - `304`: Not modified
   - `403`: Forbidden
   - `404`: Resource not found

## Results
It returns a list of JSON objects if no custom header is specified.
