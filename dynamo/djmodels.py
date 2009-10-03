from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin as djangoadmin
import datetime

# 
# A table to hold counters for object classes
# Note that these things arent necessarily unique since 
#
class DJCounter(models.Model):
    # 
    # name of the countable
    #
    name        = models.CharField(max_length = 128, unique = True)

    # 
    # Number of items of this type
    #
    count       = models.IntegerField(default = 0)

    # 
    # Admin Interface
    #
    class Admin: save_on_top = True

# 
# A generic big object ID.
# BOBs are Big OBjects.  Essentially they are used to store large items for
# the attribute of an object.  The bob_id/bob_fragment is a unique primary
# key.
#
class DJBOB(models.Model):
    # 
    # Number of fragments in this bob
    #
    num_fragments   = models.IntegerField(default = 0)

# 
# Big OBject fragment.
#
class DJBOBFragment(models.Model):
    MAX_BOB_SIZE            = 512

    # 
    # Which attribute does this fragment belong to?
    #
    parent      = models.ForeignKey(DJBOB)

    # 
    # BOB Fragment ID
    #
    fragment    = models.IntegerField()

    # 
    # Contents of the BOB fragment
    #
    contents    = models.CharField(max_length = MAX_BOB_SIZE, default = "")

    # 
    # bob_id/bob_fragment are a unique primary key
    #
    unique_together = ("parent", "fragment")

    # 
    # Admin Interface
    #
    class Admin: save_on_top = True


# 
# Base class of models that are extendible
#
class DJExpando(models.Model):
    # 
    # Lumped/unstructure extension data
    #
    bob     = models.ForeignKey("DJBOB", null = True)

# 
# The value of an attribute of an object
#
# obj/attrib is the primary key
#
class DJAttribute(models.Model):
    """
        This holds the actual attribute value
        The obj_class/obj_id/attrib_name tuple must be unique.
    """
    ATTRIB_TYPE_BOOL    = 0
    ATTRIB_TYPE_INT     = 1
    ATTRIB_TYPE_FLOAT   = 2
    ATTRIB_TYPE_BOB     = 3
         
    #
    # Class of the object to which this object belongs
    #
    obj_class   = models.CharField(max_length = 128)

    # 
    # ID of the object to which this attribute belongs
    #
    obj_id      = models.IntegerField()

    # 
    # Name of the attribute
    #
    attrib_name = models.CharField(max_length = 64)

    # 
    # Attribute type
    #
    attrib_type = models.IntegerField(default = 0)

    # 
    # The value of the field (if a simple field)
    #
    value   = models.CharField(max_length = 16, default = "")

    # 
    # Value of the object if greater than 16 chars
    #
    bob     = models.ForeignKey("DJBOB", null = True)

    # 
    # game/user are a unique primary key
    #
    unique_together = ("obj_id", "attrib_name")

    # 
    # String representation
    #
    def __str__(self):
        return "%s - %d - %s - %d - %s" % (self.obj_class, self.id, self.attrib_name, self.attrib_type, self.value)

    # 
    # Unicode representation
    #
    def __unicode__(self):
        return self.__str__()

    # 
    # Admin Interface
    #
    class Admin:
        save_on_top = True

djangoadmin.site.register(DJCounter)
djangoadmin.site.register(DJAttribute)
djangoadmin.site.register(DJBOBFragment)
djangoadmin.site.register(DJBOB)
