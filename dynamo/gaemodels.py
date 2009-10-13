
from google.appengine.ext import db
from google.appengine.api.users import User
import datetime, settings
from djapps.gaeutils.sessions import Session

class Unique(db.Model):
    @classmethod
    def check(cls, scope, value):
        def tx(scope, value):
            key_name = "U%s:%s" % (scope, value)
            ue = Unique.get_by_key_name(key_name)
            if ue:
                raise UniqueConstraintViolation(scope, value)
            ue = Unique(key_name = key_name)
            ue.put()
        db.run_in_transaction(tx, scope, value)

    class UniqueConstraintViolation(Exception):
        def __init__(self, scope, value):
            super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope))

# 
# Holds info about a counter shard
#
# TODO - put in things like a load factor so if we are reaching X counters
# per shard then add more shards
#
class DJCounterConfig(db.Model):
    # 
    # name of the countable
    #
    name        = db.StringProperty(required = True)

    # 
    # Number of shards of this type
    #
    num_shards  = db.IntegerProperty(required = True, default = 50)

# 
# A table to hold counters for object classes
#
class DJCounterShard(db.Model):
    # 
    # name of the countable
    #
    name        = db.StringProperty()

    # 
    # Number of items of this type
    #
    count       = db.IntegerProperty(default = 0)

# 
# A generic big object ID.
#
# BOBs are Big OBjects.  Essentially they are used to store large items for
# the attribute of an object.  The bob_id/bob_fragment is a unique primary
# key.
#
# We could use blobs but problem is GAE only gives us 1000 blobs in total
# so we have to manage the fragmentation manually!!  Damn it.
#
class DJBOB(db.Model):
    # 
    # Number of fragments in this bob
    #
    num_fragments   = db.IntegerProperty(default = 0)

# 
# Big OBject fragment.
#
class DJBOBFragment(db.Model):
    MAX_BOB_SIZE            = 512

    # 
    # Which attribute does this fragment belong to?
    #
    bob         = db.ReferenceProperty(DJBOB)

    # 
    # BOB Fragment ID
    #
    fragment    = db.IntegerProperty()

    # 
    # Contents of the BOB fragment
    #
    contents    = db.ByteStringProperty(default = "")

