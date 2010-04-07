
import datetime, random, sha, sys, logging, urlparse
from django.conf import settings
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse

import  djapps.utils.decorators     as djdecos
import  djapps.utils.request        as djrequest
import  djapps.utils.json           as djjson
from    djapps.utils                import api_result
from    djapps.utils                import urls as djurls
from    djapps.dynamo               import helpers as dynhelpers
from    djapps.auth.openid          import PROVIDERS_KEY, default_user_maker

from openid import fetchers
from openid.consumer.consumer import Consumer
from openid.consumer import discover
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import pape, sreg, ax
from openid.yadis.manager import Discovery

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

def make_openid_redirect_url(the_consumer, openid_session, openid_url, full_request_url,
                             login_complete_url = "/openid/login/complete",
                             redirect_field_name = "next",
                             redirect_to = "/"):
    try:
        disco = Discovery(openid_session, openid_url, the_consumer.session_key_prefix)
        try:
            service = disco.getNextService(discover.discover)
        except fetchers.HTTPFetchingError, why:
            raise DiscoveryFailure(
                'Error fetching XRDS document: %s' % (why[0],), None)

        auth_request = the_consumer.beginWithoutDiscovery(service)
        # auth_request = the_consumer.begin(openid_url)
    except discover.DiscoveryFailure, e:
        logging.error("Error during OpenID provider discovery: " + str(e))
        return api_result(-1, e)
    except discover.XRDSError, e:
        logging.error("Error parsing XRDS from provider: " + str(e))
        return api_result(-1, e)

    # request.openid_session.claimed_id = auth_request.endpoint.claimed_id
    # request.openid_session.server_url = auth_request.endpoint.server_url
    # request.openid_session.save()

    # this is messy - we need the extension type to be specified
    # elsewhere instead of having to hardcode it all here
    fetch_request = ax.FetchRequest()
    fetch_request.add(ax.AttrInfo("http://schema.openid.net/contact/email", 1, True, "email"))
    fetch_request.add(ax.AttrInfo("http://axschema.org/namePerson/first", 1, True, "firstname"))
    fetch_request.add(ax.AttrInfo("http://axschema.org/namePerson/last", 1, True, "lastname"))
    auth_request.addExtension(fetch_request)


    sreg_request = sreg.SRegRequest(optional=['nickname', 'fullname', 'email'])
    auth_request.addExtension(sreg_request)

    pape_request = pape.Request([pape.AUTH_MULTI_FACTOR,
                                 pape.AUTH_MULTI_FACTOR_PHYSICAL,
                                 pape.AUTH_PHISHING_RESISTANT,
                                 ])
    auth_request.addExtension(pape_request)

    parts               = list(urlparse.urlparse(full_request_url))
    parts[2]            = login_complete_url
    parts[4]            = 'session_id=%s' % openid_session.sid
    if redirect_to: parts[4] += '&%s=%s' % (redirect_field_name, redirect_to)

    parts[5]    = ''
    return_to   = urlparse.urlunparse(parts)
    realm       = urlparse.urlunparse(parts[0:2] + [''] * 4)

    redirect_url = auth_request.redirectURL(realm, return_to)
    return redirect_url

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
                          redirect_field_name   = "next",
                          login_complete_url    = "/openid/login/complete"):
    if request.method == "GET":
        # redirect back to the login page
        return HttpResponseRedirect(djurls.get_login_url())
    elif request.method == "POST":
        # paramount!  without this no XRDS can be fetched 
        openid_url  = request.POST.get('openid_url')
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if not openid_url:
            return api_result(-1, "OpenID Provider URL Not Specified")

        the_consumer = get_consumer(request)
        if not the_consumer:
            return api_result(-1, "Could not create consumer object")
    
        full_request_url    = djurls.get_site_url() + "/" + request.get_full_path()
        redirect_url = make_openid_redirect_url(the_consumer, request.openid_session, openid_url, 
                                                full_request_url,
                                                login_complete_url,
                                                redirect_field_name,
                                                redirect_to)

        logging.debug('Redirecting to %s' % redirect_url)
        return HttpResponseRedirect(redirect_url)

# 
# Called by the openid provider after an authentication request has been
# processed (ie when we have directed the user to them in the first place
# from the above handler).
#
# Note that this will do the redirection to the "original" uri that the
# user had requested (if response was a success) otherwise we redirect back
# to the login page again!
#
# Another thing to note is that we also create a user object here (on
# success).  But we do not want to tie it down to one kind of user.  So the
# user will be created with the function user_maker which by default will
# create a "Default" user, but other types like UserAliases can also be
# created in this method.
#
def openid_login_complete(request,
                          redirect_field_name = "next",
                          user_maker = default_user_maker):
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
        fetch_data = ax.FetchResponse.fromSuccessResponse(response)

        new_user, new_created = user_maker(response.endpoint.claimed_id, response.endpoint.server_url)
        if new_user:
            providers[response.endpoint.server_url] = response.endpoint.claimed_id
            request.openid_session[PROVIDERS_KEY]   = providers

            # update user info if not already done
            first_name = fetch_data.data.get("http://axschema.org/namePerson/first", None)
            last_name = fetch_data.data.get("http://axschema.org/namePerson/last", None)
            email = fetch_data.data.get("http://schema.openid.net/contact/email", None)
            if first_name:
                new_user.first_name = first_name[0]
            if last_name:
                new_user.last_name  = last_name[0]
            if email:
                new_user.email      = email[0]
            dynhelpers.save_objects(new_user)

            redirect_to = request.REQUEST.get(redirect_field_name, '/')
            return HttpResponseRedirect(redirect_to)

    logging.exception("============================================================")
    logging.exception("Response Failure: " + str(response))
    return HttpResponseRedirect(djurls.get_login_url())

