# Copyright: 2024 Ibrahem Mouhamad

# Defining required constants

Consts = {
    'DEFAULT_BASE_URL': 'https://api.github.com',
    'DEFAULT_TIMEOUT': 15,
    'DEFAULT_USER_AGENT': 'Github API client by Github:@ibraym',
    'DEFAULT_PER_PAGE': 30,
    'DEFAULT_SECONDS_BETWEEN_REQUESTS': 1,
    'DEFAULT_SECONDARY_RATE_WAIT': 60,
    'headerRateRemaining': 'x-ratelimit-remaining',
    'headerRateLimit': 'x-ratelimit-limit',
    'headerRateReset': "X-RateLimit-Reset",
    'headerRawJSON': 'application/vnd.github.raw+json',
    'headerHtmlJSON': 'application/vnd.github.html+json',
    'headerObjectJSON': 'application/vnd.github.object+json',
}