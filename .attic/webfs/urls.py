from django.conf.urls.defaults import *
from djapps.accounts import views as userviews

# 
# Select one of the following prefixes depending on whether 
# we want the "testzone/" in the front
#
URL_PATH_PREFIX = "webfs/"
# URL_PATH_PREFIX = r"^"

urlpatterns = patterns('',
    # Uncomment this for admin:
    # (r'^admin/', include('django.contrib.admin.urls')),
    # 
    # API for dealing with files stored on the sesrver
    #
    (URL_PATH_PREFIX + r'list/', fsviews.list),
    (URL_PATH_PREFIX + r'delete/', fsviews.delete),
    # (URL_PATH_PREFIX + r'rename/', fsviews.rename),
    # (URL_PATH_PREFIX + r'mkdir/', fsviews.mkdir),
    # (URL_PATH_PREFIX + r'getattr/', fsviews.getattr),
    # (URL_PATH_PREFIX + r'setattr/', fsviews.setattr),
    # (URL_PATH_PREFIX + r'lock/', fsviews.lock),
    # (URL_PATH_PREFIX + r'unlock/', fsviews.unlock),
    # (URL_PATH_PREFIX + r'read/', fsviews.read),
    # (URL_PATH_PREFIX + r'write/', fsviews.write),
)

