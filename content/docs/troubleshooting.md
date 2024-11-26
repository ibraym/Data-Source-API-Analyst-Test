# Troubleshooting Guide

## Common Issues
1. **401 Unauthorized**
   - Ensure the personal access token is active and correctly set in the `Authorization` header.

2. **404 Not Found**
   Verify the endpoint requirements:
      - If the endpoint requires authentication, then make sure to authenticate before making requests.
      - If you send request to [commits](./commits.md) or [contents](./contents.md) endpoints, make sure that the query parameters are valid. Verify the repository owner, name, and path.

2. **403 Rate Limit Exceeded**
   - Use the `/rate_limit` endpoint to monitor remaining requests.
   - Implement backoff logic to wait until the reset time. We already provided an implementation for that in [GithubRetry class](../python/github_retry.py).

4. **Pagination Issues**
   - Always include `page` and `per_page` parameters.
   - Fetch additional pages in a loop until the response is empty. See [paginator function](../python/github_client.py) in `Github` class.

5. **400 Bad request**
Verify the query parameters.