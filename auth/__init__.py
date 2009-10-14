
from django.conf import settings

REDIRECT_FIELD_NAME     = "next"

if settings.USING_APPENGINE:
    from djapps.gaeutils.sessions import Session
    def get_session(cookie_name, cookies = None):
        return Session(cookie_name = cookie_name)
else:
    def get_session(cookie_name, cookies):
        session_key     = cookies.get(cookie_name, None)
        engine          = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        return engine.SessionStore(session_key)

