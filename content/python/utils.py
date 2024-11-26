# Copyright: 2024 Ibrahem Mouhamad

from typing import Any, Dict, Union
from datetime import datetime

import urllib


import logging
logger = logging.getLogger('my_logger')

logging.basicConfig()

def add_parameters_to_url(
    url: str,
    parameters: Dict[str, Any],
) -> str:
    """
    Add query parameters to a given URL.

    :param url: The base URL to which parameters will be added.
    :param parameters: A dictionary of parameters to add to the URL.
                       Existing parameters in the URL will be overwritten if they have the same keys.
    :return: The URL with the updated query parameters.
    """
    scheme, netloc, url, params, query, fragment = urllib.parse.urlparse(url)
    url_params = urllib.parse.parse_qs(query)
    # union parameters in url with given parameters, the latter have precedence
    url_params.update(**{k: v if isinstance(v, list) else [v] for k, v in parameters.items()})
    parameter_list = [(key, value) for key, values in url_params.items() for value in values]
    # remove query from url
    url = urllib.parse.urlunparse((scheme, netloc, url, params, "", fragment))

    if len(parameter_list) == 0:
        return url
    else:
        return f"{url}?{urllib.parse.urlencode(parameter_list)}"

def parseLinkHeader(headers: Dict[str, Union[str, int]]) -> Dict[str, str]:
    """
    Parse the `Link` header from HTTP response headers.

    :param headers: A dictionary containing HTTP response headers.
    :return: A dictionary mapping relation types (e.g., "next", "prev") to URLs.
    """
    links = {}
    if "link" in headers and isinstance(headers["link"], str):
        linkHeaders = headers["link"].split(", ")
        for linkHeader in linkHeaders:
            url, rel, *rest = linkHeader.split("; ")
            url = url[1:-1]
            rel = rel[5:-1]
            links[rel] = url
    return links

def is_iso_format(date_string):
    # Attempt to parse the string using the ISO 8601 format
    try:
        datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False