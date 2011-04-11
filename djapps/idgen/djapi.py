
import random, sys, models, constants, math, utils, gen_classes

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
    generator.save()     # will fail if name exists

    eval(gen_type).create_generator_state(generator, **kwargs)

    # create the state object
    return generator

def get_next_id(generator_or_name, hint = None):
    """
    Gets the next ID using the generator.
    """
    generator = generator_or_name
    if type(generator) in (str, unicode):
        generator = models.IDGenerator.objects.get(pk = generator)
    return eval(generator.gen_type).get_next_id(generator, hint)

