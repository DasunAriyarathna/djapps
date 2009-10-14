
import datetime, random, sha, sys, logging, urlparse
from django.conf import settings
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse

import  djapps.utils.decorators     as djdecos
import  djapps.utils.request        as djrequest
import  djapps.utils.json           as djjson
from    djapps.utils                import api_result
from    djapps.utils                import urls as djurls
from    djapps.auth                 import REDIRECT_FIELD_NAME
from    djapps.auth.openid          import PROVIDERS_KEY

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

consumer_instance   = False

def get_consumer(request):
    assert hasattr(request, 'session'), "The openid module requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'gaeutils.middle.middleware.SessionMiddleware' in GAE or 'django.contrib.sessions.middleware.SessionMiddleware' in django."

    consumer_instance = None
    if not consumer_instance:
        fetchers.setDefaultFetcher(fetcher.UrlfetchFetcher())
        consumer_instance = Consumer(request.openid_session, store.DatastoreStore())

    return consumer_instance

# 
# The initiate url is called when the user selects to "sign in with XXX"
#
# Ok the openid provider after authenticating the user will redirect the
# user back to us.  Which page should the user be redirected to?  Should
# the user go to the page he/she was originally intending to visit or
# should the user be sent to an intermediate page, which completes auth
# process and THEN redirects to the page the user had originally in mind?
#
# With the intermediate stage, all the logic happens before any other page
# is visited which is clean.  But it has the side effect of an extra http
# request.
#
# However if the user is redirected directly (from the openid provider),
# then we need an authentication layer (perhaps as part of the
# MultiSiteAuthenticator middleware.  While this saves the extra http
# request, every authenticator will have to look for the openid.XXX
# parameters in each request essentially duplicating the work.
#
# SO with this in mind a way to alleviate this would be to add an OpenID
# middleware which will keep track of all users from all openid providers
# and do the login initiation and completion in this module.
#
# This way specific authenticators could look at the openid
# middleware and session data to see which providers (or users on the
# providers) are logged in instead of performing a login completion
# themselves.
#
def openid_login_initiate(request,
                          redirect_field_name   = REDIRECT_FIELD_NAME,
                          login_complete_url    = "/openid/login/complete"):
    if request.method == "GET":
        # redirect back to the login page
        return HttpResponseRedirect(djurls.get_login_url())
    elif request.method == "POST":
        # paramount!  without this no XRDS can be fetched 
        openid_url = request.POST.get('openid_url')
        if not openid_url:
            return api_result(-1, "OpenID Provider URL Not Specified")

        the_consumer = get_consumer(request)
        if not the_consumer:
            return api_result(-1, "Could not create consumer object")

        try:
            auth_request = the_consumer.begin(openid_url)
        except discover.DiscoveryFailure, e:
            logging.error("Error during OpenID provider discovery: " + str(e))
            return api_result(-1, e)
        except discover.XRDSError, e:
            logging.error("Error parsing XRDS from provider: " + str(e))
            return api_result(-1, e)

        # request.openid_session.claimed_id = auth_request.endpoint.claimed_id
        # request.openid_session.server_url = auth_request.endpoint.server_url
        # request.openid_session.save()

        sreg_request = sreg.SRegRequest(optional=['nickname', 'fullname', 'email'])
        auth_request.addExtension(sreg_request)

        pape_request = pape.Request([pape.AUTH_MULTI_FACTOR,
                                     pape.AUTH_MULTI_FACTOR_PHYSICAL,
                                     pape.AUTH_PHISHING_RESISTANT,
                                     ])
        auth_request.addExtension(pape_request)

        redirect_to = request.REQUEST.get(redirect_field_name, '')
        full_url    = djurls.get_site_url() + "/" + request.get_full_path()

        parts       = list(urlparse.urlparse(full_url))
        parts[2]    = login_complete_url

        parts[4]    = 'session_id=%s' % request.openid_session.sid
        if redirect_to: parts[4] += '&%s=%s' % (redirect_field_name, redirect_to)

        parts[5]    = ''
        return_to   = urlparse.urlunparse(parts)
        realm       = urlparse.urlunparse(parts[0:2] + [''] * 4)

        redirect_url = auth_request.redirectURL(realm, return_to)
        logging.debug('Redirecting to %s' % redirect_url)
        return HttpResponseRedirect(redirect_url)

# 
# Called by the openid provider after an authentication request has been
# processed (ie when we have directed the user to them in the first place
# from the above handler).
#
def openid_login_complete(request, redirect_field_name = REDIRECT_FIELD_NAME):
    the_consumer = get_consumer(request)
    if not the_consumer:
        return api_result(-1, "Could not create consumer object")


    full_url    = djurls.get_site_url() + request.get_full_path()
    response    = the_consumer.complete(request.GET, full_url)
    if not hasattr(request.openid_session, PROVIDERS_KEY):
        request.openid_session[PROVIDERS_KEY] = {}
    providers   = request.openid_session[PROVIDERS_KEY]
    if response.status == 'success':
        sreg_data = sreg.SRegResponse.fromSuccessResponse(response)
        pape_data = pape.Response.fromSuccessResponse(response)

        print >> sys.stderr, "================================================================"
        print >> sys.stderr, "Response Sucess: sreg, pape: ", sreg_data, pape_data
        if sreg_data:
            print >> sys.stderr, "SReg_Data.items(): ", sreg_data.items()
        print >> sys.stderr, "ServerUrl, Claimed_id: ", response.endpoint.server_url, response.endpoint.claimed_id
        print >> sys.stderr, "================================================================"

        providers[response.endpoint.server_url] = response.endpoint.claimed_id
        request.openid_session[PROVIDERS_KEY]   = providers
        # request.openid_session.save()

        redirect_to = request.REQUEST.get(redirect_field_name, '')
        return HttpResponseRedirect(redirect_to)
    else:
        logging.exception("============================================================")
        logging.exception("Response Failure: " + str(response))
