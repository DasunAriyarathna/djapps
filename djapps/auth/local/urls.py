
from django.conf.urls.defaults import *
from djapps.auth.local import views as djacviews

urlpatterns = patterns('',
    url(r'^login', djacviews.decorated_account_login, name="account_login"),
    url(r'^logout', djacviews.account_logout, name="account_logout"),
    url(r'^register', djacviews.account_register, name="account_register"),
    url(r'^confirm/(?P<activation_key>\w+)', djacviews.account_confirm, name="account_confirm"),
)

