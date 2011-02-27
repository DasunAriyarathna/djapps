
from django.db import models
from django.db import transaction
from django.conf import settings
import datetime
from djapps.dynamo.djhelpers import get_or_create_object, get_object_id

class Association(models.Model):
    """
    An association with another OpenID server, either a consumer or a
    provider.
    """
    url         = models.URLField()
    handle      = models.CharField(max_length = 64)
    association = models.CharField(max_length = 512)
    created     = models.DateTimeField(auto_now_add = True)

class UsedNonce(models.Model):
    """
    An OpenID nonce that has been used.
    """
    server_url  = models.URLField()
    timestamp   = models.DateTimeField(auto_now_add = True)
    salt        = models.CharField(max_length = 64)

