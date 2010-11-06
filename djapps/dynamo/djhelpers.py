
from django.db import models
from django.db.models import Q
from django.db import transaction
import datetime, os, sys, logging

import djmodels as dnmod

# 
# A quick transaction enabled function to 
# save a bunch of db objects.
#
@transaction.commit_on_success
def save_objects(*objects):
    to_save = []
    for obj in objects:
        if type(obj) is list:
            to_save.extend(obj)
        else:
            to_save.extend([obj])

    for obj in to_save:
        obj.save()

# 
# Saves a datastore object
#
def save_object(obj):
    obj.save()

# TODO: memcaching!
def get_object_by_id(obj_class, id):
    """ Get an object by its ID. """
    try: return obj_class.objects.get(pk = id)
    except obj_class.DoesNotExist: return None

def create_object(obj_class, save = True, parent = None, id_val = None, **kwds):
    if id_val:
        return obj_class.objects.create(pk = id_val, **kwds)
    else:
        return obj_class.objects.create(**kwds)

def get_or_create_object(obj_class, save = True, parent = None, id_val = None, **kwds):
    try:
        return obj_class.objects.get(**kwds), False
    except obj_class.DoesNotExist:
        return create_object(obj_class, save, parent, id_val, **kwds), True

# 
# Get a list of all objects of a certain class
#
def get_all_objects(obj_class):
    return obj_class.objects.all()

# 
# Delete a set of objects
#
def delete_objects(objs):
    if objs: objs.delete()

# 
# Delete all objects in a class
#
def delete_all_objects(obj_class):
    print >> sys.stderr, "Deleting all objects of class ", obj_class
    obj_class.objects.all().delete()

# 
# Gets the object with a the given keywords
#
def get_objects(obj_class, **kwds):
    try: return obj_class.objects.filter(**kwds)
    except obj_class.DoesNotExist: return None

# 
# Gets the count of objects with a the given keywords
#
def get_object_count(obj_class, **kwds):
    try: return obj_class.objects.filter(**kwds).count()
    except obj_class.DoesNotExist: return 0

# 
# Returns the ID of a db object
#
def get_object_id(obj):
    return obj.pk

#################################################################################
#                           Counter related helper methods                      #
#################################################################################
def get_counter(name):
    counter, new_created = dnmod.DJCounter.objects.get_or_create(name = name)
    return counter.count;

def delete_counter(name):
    try:
        counter = dnmod.DJCounter.objects.get(name = name)
        counter.delete()
    except dnmod.DJCounter.DoesNotExist, dne:
        pass

def increment_counter(name, incr = 1):
    counter, new_created = dnmod.DJCounter.objects.get_or_create(name = name)
    counter.count += incr
    counter.save()
    return counter.count

#################################################################################
#                   Django specific stuff to create/change bobs                 #
#################################################################################

# 
# gets the data within all the bob fragments of a bob
#
def get_bob_data(bob_name):
    if bob_name:
        frags   = dnmod.DJBOBFragment.objects.filter(bob_name = bob_name).order_by("fragment")
        bobdata = "".join([f.contents for f in frags])
        return bobdata
    else:
        return ""

# 
# Sets the data within all the bob fragments of a bob
# Can only pass in string data here.
# Returns all the fragments so we dont save it here and let the 
# caller save it in one go
#
def set_bob_data(bob_name, data_str):
    # 
    # delete previous fragments
    #
    dnmod.DJBOBFragment.objects.filter(bob_name = bob_name).delete()

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
        fragment = dnmod.DJBOBFragment(bob_name = bob_name, fragment = fragindex, contents = part1)
        output.append(fragment)

        str_val = str_val[dnmod.DJBOBFragment.MAX_BOB_SIZE : ]
        part1 = str_val[ : dnmod.DJBOBFragment.MAX_BOB_SIZE]

        fragindex += 1

    return output

#################################################################################
#                           Creating Dynamic Models                             #
#################################################################################
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model

def register_models(app_name, *model_list):
    from django.db import connection, transaction, models
    from django.core.management.color import no_style

    cursor              = connection.cursor()
    style               = no_style()
    tables              = connection.introspection.table_names()
    seen_models         = connection.introspection.installed_models(tables)
    created_models      = set()
    pending_references  = {}

    for model in model_list:
        print >> sys.stderr, "Processing %s.%s model" % (app_name, model._meta.object_name)
        if connection.introspection.table_name_converter(model._meta.db_table) in tables:
            continue
        sql, references = connection.creation.sql_create_model(model, style, seen_models)
        seen_models.add(model)
        created_models.add(model)
        for refto, refs in references.items():
            pending_references.setdefault(refto, []).extend(refs)
            if refto in seen_models:
                sql.extend(connection.creation.sql_for_pending_references(refto, style, pending_references))
        sql.extend(connection.creation.sql_for_pending_references(model, style, pending_references))

        print >> sys.stderr, "Creating table %s", model._meta.db_table
        for statement in sql:
            cursor.execute(statement)
        tables.append(connection.introspection.table_name_converter(model._meta.db_table))

    # create m2m tables - must be created AFTER the tables (see syncdb.py)
    for model in model_list:
        if model in created_models:
            sql = connection.creation.sql_for_many_to_many(model, style)
            if sql:
                print >> sys.stderr, "Creating m2m tbales for %s.%s model" % (app_name, model._meta.object_name)
                for statement in sql:
                    cursor.execute(statement)

    transaction.commit_unless_managed()

