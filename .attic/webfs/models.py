from django.db import models

# Create your models here.

# 
# A table for holding basic registration info about a user,
# the actual user profile will be in a different class
#
class FSEntry(models.Model):
    virtualpath     =   models.CharField(maxlength=256)
    realpath        =   models.CharField(maxlength=256)
    type            =   models.IntegerField()
    size            =   models.IntegerField()
    created         =   models.DateTimeField()
    modified        =   models.DateTimeField()
    parent          =   models.ForeignKey('FSEntry')
    children        =   models.ManyToManyField('FSEntry')

    class Admin:
        pass

# 
# A table for holding permissions for accessing files and or folders
#
# Essentially, for each entry, we need to define the following permissions:
#  1. Access Type       - Read/Write/Both/None
#  2. Authentication    - Who access it?
#
#  Problem is in Authentication!
#
#  An entry may not have any details about the authentication associated
#  with it, but there may be one to one of its ancestor folders which may
#  apply to it.
#
class Permission(models.Model):
    virtualpath     =    models.CharField(maxlength=256)
    class Admin:
        pass
