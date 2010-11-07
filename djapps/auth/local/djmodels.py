from django import db
from django.db import models
from django.contrib.auth.models import User

# 
# A table for holding basic registration info about a user,
# the actual user profile will be in a different class
#
class LocalUserRegistration(models.Model):
    user            = models.ForeignKey(User)
    activation_key  = models.CharField(max_length=128)
    salt            = models.CharField(max_length=128)
    key_expires     = models.DateTimeField()
    active          = models.BooleanField(default = False)
    class Admin: pass

