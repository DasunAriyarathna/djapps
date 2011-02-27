from django.db import models

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
# Big OBject fragment.
# Idea is objects can have "extension" data over one or more of these
# fragments.  The objects will be responsible for giving the names of these
# objects.  Kind of act as poor man's inodes.
#
class DJBOBFragment(models.Model):
    MAX_BOB_SIZE            = 512

    # 
    # Name of the bob this fragment belongs to
    #
    bob_name    = models.CharField(max_length = 128)

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
    class Meta:
        unique_together = ("bob", "fragment")

    # 
    # Admin Interface
    #
    class Admin: save_on_top = True

