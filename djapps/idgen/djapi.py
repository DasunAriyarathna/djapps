
import random, sys, models, constants, math, utils, gen_classes

def create_id_generator(name,
                        gen_type = "gen_classes.IDGeneratorRandom",
                        allowed_keys = constants.UPPER_ALNUM,
                        key_length = 8,
                        **kwargs):
    """
    Creates a new id generator with key length and allowed characters in the keys.
    """
    assert name.strip() != "", "Name cannot be empty."
    assert key_length > 0, "Key length must be greater than 0"
    assert len(allowed_keys) > 0, "Allowed keys must have at least one character."
    assert len(allowed_keys) <= 100, "Allowed keys cannot have more than 100 characters."

    generator   = models.IDGenerator(name = name,
                                     allowed_keys = allowed_keys,
                                     key_length = key_length,
                                     gen_type = gen_type)
    generator.save()     # will fail if name exists

    num_bits    = utils.get_num_bits(len(allowed_chars), key_length)
    tap_bits    = ",".join(map(str, utils.calculate_tap_bits(num_bits)))
    eval(gen_type).create_generate_state(generator, tap_bits = tap_bits seed = seed)

    # create the state object
    return generator

def get_next_id(generator_name):
    """
    Gets the next ID using the generator.
    """
    generator   = models.IDGenerator.objects.get(pk = generator_name)
    return eval(generator.gen_type).get_next_id(generator)

