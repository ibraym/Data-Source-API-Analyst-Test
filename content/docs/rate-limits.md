# Detailed Summary: Rate Limits for the REST API


## **1. About Primary Rate Limits**
Primary rate limits restrict the number of API requests we can make within a specific time frame. These limits vary depending on the authentication method and are intended to prevent abuse and ensure equitable access.

### **Key Features of Primary Rate Limits**
- Unauthenticated requests are highly restricted.
- Authenticated requests allow significantly higher usage.
- Specific endpoints, such as search, may have stricter limits.

---

### **Rate Limits by Authentication Method**

| **Authentication Method**              | **Rate Limit** (Requests/Hour)           | **Notes**                                                                                              |
|-----------------------------------------|------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Unauthenticated                         | 60                                       | Rate shared across IP address. Limited to public data.                                                |
| Authenticated (Personal Access Token)   | 5,000                                    | Includes personal tokens, GitHub Apps, and OAuth apps.                                                |
| GitHub Enterprise Cloud (App/OAuth)     | 15,000                                   | Higher limits apply to requests made via apps owned by GitHub Enterprise Cloud organizations.         |
| GitHub App Installations                | 5,000 (minimum) / scales with usage      | Scales with users and repositories. Maximum: 12,500 requests/hour.                                    |
| OAuth Apps (Client ID & Secret)         | 5,000 (per app)                          | For public data access only. Enterprise Cloud apps: 15,000 requests/hour.                             |
| GITHUB_TOKEN in Actions                 | 1,000 (per repository)                   | 15,000/hour for repositories under GitHub Enterprise Cloud.                                           |

---

## **2. About Secondary Rate Limits**
Secondary rate limits aim to prevent excessive strain on the API infrastructure. These are based on factors such as concurrent requests, endpoint-specific limits, and computational resource usage.

### **Triggers for Secondary Rate Limits**
1. **Concurrent Requests**: Maximum of 100 concurrent requests across REST and GraphQL APIs.
2. **Single-Endpoint Usage**: No more than 900 points/minute for REST API endpoints and 2,000 points/minute for GraphQL.
3. **Request Rate**: Excessive requests in a short time or high compute-cost operations can trigger limits.
4. **Content Creation**: Limits include actions like creating issues, comments, or repositories (up to 80/minute or 500/hour).
5. **Other Undisclosed Reasons**: Secondary limits may change without notice.


## **3. Monitoring Rate Limit**
Rate limit information is provided in API response headers or through a specific endpoint.

### **Rate Limit Response Headers**
- `x-ratelimit-limit`: Maximum allowed requests per hour.
- `x-ratelimit-remaining`: Remaining requests in the current window.
- `x-ratelimit-used`: Requests made in the current window.
- `x-ratelimit-reset`: Time (UTC epoch seconds) when the limit resets.
- `x-ratelimit-resource`: The resource against which the request counted.

### **Rate Limit Status**
- We can use the `/rate_limit` endpoint to retrieve the current rate limit status. This endpoint **does not consume primary rate limits**, but it may count towards secondary limits.

---

## **4. Exceeding the Rate Limit**
Exceeding rate limits triggers specific error responses.

### **Primary Rate Limit Exceeded**
- Response: HTTP `403` or `429`.
- `x-ratelimit-remaining`: `0`.
- Retry after time specified in `x-ratelimit-reset`.

### **Secondary Rate Limit Exceeded**
- Response: HTTP `403` or `429`, often with `retry-after` header.
- Retry Strategy:
  1. Wait the specified number of seconds from `retry-after` header.
  2. For ambiguous responses, wait at least one minute before retrying.
  3. Use exponential backoff for persistent failures.
  4. Throw an error after a reasonable number of retries.

⚠️ **Warning**: Continuing requests while rate-limited can result in the banning of the integration.

---

### **5. Staying Under the Rate Limit**
To optimize API usage:
1. **Authenticate All Requests**:
   - Always use tokens for higher rate limits.
2. **Monitor Requests**:
   - Track usage via response headers or `/rate_limit`.
3. **Optimize API Calls**:
   - Cache frequent data.
   - Combine requests where possible.
   - Avoid redundant or excessive requests.
4. **Use GraphQL for Bulk Data**:
   - Fetch related data in a single query to minimize requests.
5. **Spread Out Requests**:
   - Distribute requests over time to avoid spikes.
6. **Minimize Content Creation**:
   - Avoid exceeding limits on creating issues, comments, or other content.

---

## **6. Increasing Rate Limit**
To access higher rate limits:
1. **Authenticate Requests**:
   - Move from unauthenticated to authenticated requests using tokens.
2. **Switch to GitHub Apps**:
   - Apps scale rate limits with users and repositories.
3. **Upgrade to GitHub Enterprise Cloud**:
   - Grants higher limits for apps and workflows.
