
import random, utils, models

def save_id(generator, id):
    newgenid = models.GeneratedID(generator = generator, gen_id = id)
    newgenid.save()
    return newgenid

def is_id_used(generator, val):
    if val and generator:
        return models.GeneratedID.objects.filter(generator = generator, gen_id = val).count() > 0
    return False

def mark_id_as_used(generator, val):
    if val and generator:
        from django.db import IntegrityError, DatabaseError, transaction
        try:
            save_id(generator, val)
            return True
        except IntegrityError, e:
            print "Error: Rand ID Value (%s) already exists. Trying again..." % val
            try: transaction.rollback()
            except Exception, e: print "Rollback Error: ", e.message
        except DatabaseError, e:
            print "Error: Rand ID Value (%s) already exists. Trying again..." % val
            try: transaction.rollback()
            except Exception, e: print "Rollback Error: ", e.message
    return False

class IDGenerator(object):
    """
    Base class of all generator state objects.
    """
    @classmethod
    def create_generator_state(cls, generator, *args, **kwargs):
        """
        This method creates (or fetches) the generator state object if it
        already exists.
        This method does not have to return anything, which most likely
        would imply that a generator specific state is not required (though
        not recommended).
        """
        return None

    @classmethod
    def get_next_id(cls, generator):
        """
        Calculates the next ID for a particular generator.
        """
        return None

    @classmethod
    def release_id(cls, generator, id):
        """
        Releases an ID back to the pool.
        """
        return None
        models.GeneratedID.objects.filter(id = id, generator = generator).delete()

class IDGeneratorSerial(IDGenerator):
    @classmethod
    def get_next_id(cls, generator):
        """
        Calculates the next ID for a particular generator.
        This creates IDs serially.
        """
        num_bits    = utils.get_num_bits(len(generator.allowed_chars), generator.key_length)
        delta       = 0
        while True:
            delta += 1
            val = 1 + models.GeneratedID.objects.filter(generator = generator).count()
            val = utils.value_to_string(val, generator.allowed_chars)
            if mark_id_as_used(generator, val): return val

class IDGeneratorRandom(IDGenerator):
    @classmethod
    def get_next_id(cls, generator):
        """
        Calculates the next ID for a particular generator.
        This creates IDs at random and waits till there are no collissions.
        """
        num_bits    = utils.get_num_bits(len(generator.allowed_chars), generator.key_length)
        while True:
            val = utils.value_to_string(random.randint(0, 2 ** num_bits), generator.allowed_chars)
            if mark_id_as_used(generator, val): return val

class IDGeneratorLFSR(IDGenerator):
    @classmethod
    def create_generator_state(cls, generator, *args, **kwargs):
        """
        This method creates (or fetches) the generator state object if it
        already exists.
        """
        seed        = kwargs.get("seed", 0),
        assert len(str(seed)) <= 256, "Seed cannot be greater than 256 characters long"
        # cannot have 0 seed!
        while not seed:
            seed = random.randint(0, len(allowed_keys) ** key_length)

        if tap_bits not in kwargs:
            num_bits    = utils.get_num_bits(len(allowed_chars), key_length)
            tap_bits    = ",".join(map(str, utils.calculate_tap_bits(num_bits)))
        else:
            tap_bits = kwargs["tap_bits"]

        id_gen_lfsr = models.IDGeneratorLFSR(generator = generator, seed = seed, tap_bits = tap_bits)
        id_gen_lfsr.save()
        return id_gen_lfsr

    @classmethod
    def get_next_id(cls, generator):
        """
        Calculates the next ID for a particular generator.
        This creates IDs at random and waits till there are no collissions.
        """
        num_bits    = utils.get_num_bits(len(generator.allowed_chars), generator.key_length)

        from django.db import transaction
        @transaction.commit_manually()
        def saver_method():
            # update the seed and save the generator within the transaction
            while True:
                try:
                    state       = models.IDGeneratorLFSR.objects.filter(generator = generator).all()[0]
                    tap_bits    = map(int, state.tap_bits.split(","))

                    # update the seed - shift and apply the func
                    curr_seed = int(state.seed)
                    state.seed = utils.update_bits(curr_seed, tap_bits, num_bits)
                    state.save()

                    # now get the generated ID and save it to ensure there
                    # are no collissions - once we "prove" that our LFSR is
                    # maximal we can get rid of this step
                    val = value_to_string(int(state.seed), generator.allowed_chars)
                    save_id(generator, state.seed)

                    # if this succeeds then all good!
                    transaction.commit()
                    return val
                except:
                    # reload generator state
                    print >> sys.stderr, "Generator state update failed, Trying again..."
                    state   = models.IDGeneratorLFSR.objects.filter(generator = generator).all()[0]
                    assert state, "Generator state may have been deleted"

        return saver_method()

