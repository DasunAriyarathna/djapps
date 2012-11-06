import random, sys, models, constants, math, utils, gen_classes
from django.conf import settings
from django import db as djangodb
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

def get_id_generator(name):
    """
    Gets the ID Gen by name if it exists.
    """
    try:
        return models.IDGenerator.objects.get(name = name)
    except models.IDGenerator.DoesNotExist:
        return None

def create_id_generator(name,
                        gen_type = "gen_classes.IDGeneratorRandom",
                        allowed_chars = constants.UPPER_ALNUM,
                        key_length = 6,
                        **kwargs):
    """
    Creates a new id generator with key length and allowed characters in the keys.
    """
    assert name.strip() != "", "Name cannot be empty."
    assert key_length > 0, "Key length must be greater than 0"
    assert len(allowed_chars) > 0, "Allowed chars must have at least one character."
    assert len(allowed_chars) <= 100, "Allowed chars cannot have more than 100 characters."

    generator   = models.IDGenerator(name = name,
                                     allowed_chars = allowed_chars,
                                     key_length = key_length,
                                     gen_type = gen_type)
    generator.save()     # will fail if name exists so catch the DB Error

    eval(gen_type).create_generator_state(generator, **kwargs)

    # create the state object
    return generator

def get_or_create_id_generator(name, *args, **kwargs):
    """
    Creates an id generator with a given name and arguments.  If it already
    exists, then returns the existing one.
    """
    try:
        return create_id_generator(name, *args, **kwargs)
    except djangodb.DatabaseError, ie:
        logger.debug("ID Generator (%s) already exists." % name)
        return get_id_generator(name)

def release_id(generator_or_name, id):
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    return gen_classes.release_id(generator, id)

def mark_id_as_used(generator_or_name, id):
    """
    Marks a particular ID as having been used.
    """
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    return gen_classes.mark_id_as_used(generator, id)

def get_next_id(generator_or_name):
    """
    Gets the next ID using the generator.
    """
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    return eval(generator.gen_type).get_next_id(generator)

def is_id_used(generator_or_name, id):
    """
    Tells if a particular ID has already been used for a given generator.
    """
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    return gen_classes.is_id_used(generator, id)

def validate_id(generator_or_name, id):
    """
    Tells if an id is valid for a particular class.
    """
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    if len(id) > generator.key_length or any(map(lambda x:x not in generator.allowed_chars, id)):
        raise ValidationError("Characters in '%s' must be less then %d characters in length and only made of '%s'" % (id, generator.key_length, generator.allowed_chars))

