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

