# Using Pagination in the REST API
Learn to navigate paginated responses from the REST API, including fetching additional pages, customizing page size, and automating pagination in scripts.

## Paginated Responses Navigation
When results are paginated, the response includes a `link` header with URLs for additional pages, which are:
   - `rel="prev"`: Previous page
   - `rel="next"`: Next page
   - `rel="last"`: Last page
   - `rel="first"`: First page

##  Customizing Page Size
We can use `per_page` query parameter to set the number of results per page (if supported by the endpoint).

>The `per_page` parameter appears in the `link` header.

>Tip: Review endpoint documentation to confirm if pagination and per_page parameters are supported.