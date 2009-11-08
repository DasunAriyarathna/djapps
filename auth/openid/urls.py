
from django.conf.urls.defaults import *
from djapps.auth.openid import views as djoicviews

urlpatterns = patterns('',
    url(r'^login/initiate', djoiviews.openid_login_initiate, name="openid_login_initiate"),
    url(r'^login/complete', djoiviews.openid_login_complete, name="openid_login_complete"),
)

