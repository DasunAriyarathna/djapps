
import datetime, settings, logging
from google.appengine.ext import db
from google.appengine.api.users import User
from djapps.gaeutils.sessions import Session
from google.appengine.api.datastore_errors import Timeout
import gaemodels as dnmod

# 
# A quick transaction enabled function to 
# save a bunch of db objects.
#
# TODO : transactions
#
def save_objects(*objects):
    to_save = []
    for obj in objects:
        if type(obj) is list:
            to_save.extend(obj)
        else:
            to_save.extend([obj])
    count = 0
    while count < 3:
        try:
            return db.put(to_save)
        except db.Timeout:
            count += 1
    else:
        raise db.Timeout()

# 
# Saves a datastore object
#
def save_object(obj):
    count = 0
    while count < 3:
        try:
            return db.put(obj)
        except db.Timeout:
            count += 1
    else:
        raise db.Timeout()

# TODO: memcaching!
def get_object_by_id(obj_class, key):
    """ Get an object by its ID. """
    try:
        return obj_class.get_by_id(long(key))
    except ValueError, v:
        return obj_class.get_by_key_name(key)

def create_object(obj_class, save = True, parent = None, id_val = None, **kwds):
    obj = obj_class(parent, id_val, **kwds)
    if save: db.put(obj)
    return obj

def get_or_create_object(obj_class, save = True, parent = None, id_val = None, **kwds):
    query = obj_class.all()
    for kwd in kwds:
        if query.count() > 0:
            query = query.filter("%s = " % kwd, kwds[kwd])

    if query.count() > 0:
        return query.fetch(1)[0], False
    else:
        obj = obj_class(parent, id_val, **kwds)
        if save:
            obj.put()
        return obj, True

# 
# Get all objects of a given class
#
def get_all_objects(obj_class):
    return obj_class.all()

# 
# Delete a set of objects
#
def delete_objects(objs):
    if objs:
        db.delete(objs)

def delete_all_objects(obj_class, num_del = 300, **filters):
    while True:
        querystr = "SELECT __key__ FROM %s " % obj_class.__name__
        count = 1
        values = []
        for filter in filters:
            if count == 1: querystr += " where "
            else: querystr += " and "

            querystr += " %s = :%s " % (filter, filter)
        objs = db.GqlQuery(querystr, **filters).fetch(num_del)
        objs = [item for item in objs]

        num_objs = len(objs)
        if num_objs == 0:
            # no objects left so return
            return
        else:
            if num_del > num_objs: num_del = num_objs
            print "Deleting %d/%d objects of class %s" % (num_del, num_objs, str(obj_class))
            count = 0
            while count < 5:
                try:
                    db.delete(objs)
                    count = 5
                except db.Timeout:
                    print "Timeout error - continuing %d..." % count
                    count += 1

# 
# Returns objects with given attribs
#
def get_objects(obj_class, **kwds):
    query = obj_class.all()
    for kwd in kwds:
        query.filter("%s = " % kwd, kwds[kwd])
    return query.fetch(query.count())

# 
# Gets the count of objects with a the given keywords
#
def get_object_count(obj_class, **kwds):
    query = obj_class.all()
    for kwd in kwds:
        count = query.count()
        query.filter("%s = " % kwd, kwds[kwd])

    return query.count()

# 
# Returns the ID of a db object
#
def get_object_id(obj):
    return obj.key().id_or_name()

#################################################################################
#                           Counter related helper methods                      #
#################################################################################
def get_counter(name):
    from google.appengine.api import memcache
    # total = memcache.get(name)
    if total is None:
        total = 0
        for counter in dnmod.DJCounterShard.gql('WHERE name = :1', name):
            total += counter.count
        # memcache.add(name, str(total), 60)
    return total

def delete_counter(name):
    """ Deletes the counters of a given type. """
    from google.appengine.api import memcache
    # memcache.delete(name)
    shards = dnmod.DJCounterShard.gql('WHERE name = :1', name)
    count = 0
    while count < 3:
        try:
            return db.put(shards)
        except db.Timeout:
            count += 1
    else:
        raise db.Timeout()

def increment_counter(name, incr = 1):
    config = dnmod.DJCounterConfig.get_or_insert(name, name = name)
    # TODO:
    # call increase_shards if counters/shard 
    # has reached a certain threshold
    def txn():
        import random
        index = random.randint(0, config.num_shards - 1)
        shard_name = "%s/%d" % (name, index)
        counter = dnmod.DJCounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = dnmod.DJCounterShard(key_name = shard_name, name = name)
        counter.count += incr
        counter.put()
        return counter.count
    new_count = db.run_in_transaction(txn)
    from google.appengine.api import memcache
    #
    # if memcache.get(name) is None: memcache.set(name, incr)
    # else: memcache.incr(name, incr)
    #
    return new_count

def increase_shards(name, num):
    config = dnmod.DJCounterConfig.get_or_insert(name, name = name)
    def txn():
        if config.num_shards < num:
            config.num_shards = num
            config.put()
    db.run_in_transaction(txn)

#################################################################################
#                           All bob-related helper methods                      #
#################################################################################

# 
# Set template's data
#
def set_object_bob_data(obj, data):
    # do not use Blobs as we have a limit of 1000 blobs and files!!!
    # so use custom bob's - reads are cheap anyway and doing partial reads
    # are cheap anyway
    # obj.bob = db.Blob(data)
    if not obj.bob:
        obj.bob = _new_bob()
    saved_objects = _set_bob_data(obj.bob, data)
    save_objects(obj, obj.bob, *saved_objects)

# 
# Gets the value of a "bob" property of any object
#
def get_object_bob_data(obj):
    # again not using blobs thanks to the 1000 blob limit
    # return obj.bob
    return _get_bob_data(obj.bob)

#################################################################################
#               All extendible attribute-related helper methods                 #
#################################################################################

# 
# Set the value of an object's attribute
#
def set_attr(obj, attrib_name, value):
    class_name = "%s.%s" % (obj.__module__, obj.__class__.__name__)
    attrib = _get_or_create_attribute(class_name, get_object_id(obj), attrib_name)

    if type(value) == bool or type(value) == int or type(value) == float:
        attrib.value = str(value)
        if type(value) == bool:
            attrib.attrib_type = dnmod.DJAttribute.ATTRIB_TYPE_BOOL
        elif type(value) == int:
            attrib.attrib_type = dnmod.DJAttribute.ATTRIB_TYPE_INT
        else:
            attrib.attrib_type = dnmod.DJAttribute.ATTRIB_TYPE_FLOAT
    else:
        # attrib.bob          = Blob(value)
        attrib.attrib_type   = dnmod.DJAttribute.ATTRIB_TYPE_BOB
        set_object_bob_data(attrib, value)
    db.put(attrib)

# 
# Gets the object attributes
#
def get_attr(obj, attrib_name, default_val = None):
    class_name = "%s.%s" % (obj.__module__, obj.__class__.__name__)
    attrib = dnmod.DJAttribute.objects.get(obj_class = class_name, obj_id = obj.id, attrib_name = attrib_name)
    if attrib:
        if attrib.attrib_type == dnmod.DJAttribute.ATTRIB_TYPE_BOOL:
            return bool(attrib.value)
        elif attrib.attrib_type == dnmod.DJAttribute.ATTRIB_TYPE_INT:
            return int(attrib.value)
        elif attrib.attrib_type == dnmod.DJAttribute.ATTRIB_TYPE_FLOAT:
            return float(attrib.value)
        else:
            return _get_bob_data(attrib.bob)
    else:
        logging.debug("========== Attribute %s does not exist" % attrib_name)

    return default_val

# 
# Create a new "dynamic" object instance
#
def _get_or_create_attribute(obj_class, obj_id, attrib_name):
    return dnmod.DJAttribute.get_or_insert(obj_class = obj_class,
                                          obj_id = obj_id,
                                          attrib_name = attrib_name)

#################################################################################
#               Private GAE specific stuff to create/change bobs                #
#################################################################################

# 
# Creates a new BOB
#
def _new_bob():
    return dnmod.DJBOB(num_fragments = 0)

# 
# gets the data within all the bob fragments of a bob
#
def _get_bob_data(bob):
    if bob:
        query = GqlQuery("SELECT * from DJBOBFragment where bob = :bob", bob = bob)
        query.order("fragment")
        frags  = query.fetch(query.count())
        return "".join([f.contents for f in frags])
    else:
        return ""

# 
# Sets the data within all the bob fragments of a bob
# Can only pass in string data here.
# Returns all the fragments so we dont save it here and let the 
# parent save it in one go
#
def _set_bob_data(bob, data_str):
    # 
    # delete previous fragments.
    # This is unnecessary really since we can "override" fragments instead
    # of deleting and recreating
    #
    delete_all_objects(dnmod.DJBOBFragment, bob = bob)

    # 
    # recreate fragments
    #
    # TODO: be smart about it and only delete fragments 
    # that are over the size.
    #
    str_val     = data_str
    part1       = str_val[ : dnmod.DJBOBFragment.MAX_BOB_SIZE]
    fragindex   = 0
    output      = []

    while part1 != "":
        fragment = dnmod.DJBOBFragment(bob = bob, fragment = fragindex, contents = part1)
        output.append(fragment)

        str_val = str_val[dnmod.DJBOBFragment.MAX_BOB_SIZE : ]
        part1 = str_val[ : dnmod.DJBOBFragment.MAX_BOB_SIZE]

        fragindex += 1

    bob.num_fragments = fragindex
    return output

