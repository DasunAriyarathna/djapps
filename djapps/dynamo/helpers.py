from django.conf import settings

if settings.USING_APPENGINE:
    from gaehelpers import *
else:
    from djhelpers  import *

# 
# Get the first object matching a given set of keywords.
#
def get_first_object(obj_class, **kwds):
    objs = get_objects(obj_class, **kwds)
    if objs: return objs[0]
    return None

