
import datetime, random, sha, sys, logging
from django.conf import settings
from django.template import RequestContext, loader

import  djapps.utils.decorators     as djdecos
import  djapps.utils.request        as djrequest
import  djapps.utils.json           as djjson
from    djapps.utils                import api_result

from openid import fetchers
from openid.consumer.consumer import Consumer
from openid.consumer import discover
from openid.extensions import pape, sreg

if settings.USING_APPENGINE:
    import gaefetcher as fetcher
    import gaestore as store
else:
    # TODO: Implement the fetcher and store for django
    import djfetcher as fetcher
    import djstore as store


REDIRECT_FIELD_NAME = "next"

_consumer = None

def get_consumer(request):
    assert hasattr(request, 'session'), "The openid module requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'gaeutils.middle.middleware.SessionMiddleware' in GAE or 'django.contrib.sessions.middleware.SessionMiddleware' in django.",

    if not _consumer:
        fetchers.setDefaultFetcher(fetcher.UrlfetchFetcher())
        _consumer = Consumer(request.session, store.DatastoreStore())

    return _consumer

def openid_login_initiate(request,
                 redirect_field_name = REDIRECT_FIELD_NAME,
                 request_context = None):
    # paramount!
    # without this no XRDS can be fetched 
    openid_url = request.POST.get('openid_url')
    if not openid_url:
        return api_result(-1, "OpenID Provider URL Not Specified")

    consumer = get_consumer()
    if not consumer:
        return api_result(-1, "Could not create consumer")

    try:
        auth_request = consumer.begin(openid_url)
    except discover.DiscoveryFailure, e:
        logging.error("Error during OpenID provider discovery: " + str(e))
        return api_result(-1, e)
    except discover.XRDSError, e:
        logging.error("Error parsing XRDS from provider: " + str(e))
        return api_result(-1, e)

    self.session.claimed_id = auth_request.endpoint.claimed_id
    self.session.server_url = auth_request.endpoint.server_url
    self.session.store_and_display = self.request.get('display', 'no') != 'no'
    self.session.put()

    sreg_request = sreg.SRegRequest(optional=['nickname', 'fullname', 'email'])
    auth_request.addExtension(sreg_request)
    pape_request = pape.Request([pape.AUTH_MULTI_FACTOR,
                                 pape.AUTH_MULTI_FACTOR_PHYSICAL,
                                 pape.AUTH_PHISHING_RESISTANT,
                                 ])
    auth_request.addExtension(pape_request)

    parts = list(urlparse.urlparse(self.request.uri))
    parts[2] = 'finish'
    parts[4] = 'session_id=%d' % self.session.key().id()
    parts[5] = ''
    return_to = urlparse.urlunparse(parts)
    realm = urlparse.urlunparse(parts[0:2] + [''] * 4)

    redirect_url = auth_request.redirectURL(realm, return_to)
    logging.debug('Redirecting to %s' % redirect_url)
    self.response.set_status(302)
    self.response.headers['Location'] = redirect_url


def openid_login_complete(request):
    pass
