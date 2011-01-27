
"""
An wrapper around openid's fetcher to be used in django.
"""

from openid import fetchers

class UrlfetchFetcher(fetchers.HTTPFetcher):
    def fetch(self, url, body=None, headers=None):
        return fetchers.fetch(body, headers)

