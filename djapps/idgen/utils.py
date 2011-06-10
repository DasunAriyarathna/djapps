
import math

def value_to_string(unsigned_value, allowed_chars, max_length = -1):
    """
    Converts an arbitrary integer value into string with the given
    characters.
    """
    if unsigned_value == 0:
        return allowed_chars[0]
    else:
        out = ""
        length = 0
        num_chars = len(allowed_chars)
        while unsigned_value > 0 and (max_length < 0 or length < max_length):
            length += 1
            out = allowed_chars[unsigned_value % num_chars] + out
            unsigned_value = int(unsigned_value / num_chars)
        return out

def isprime(n):
    n = abs(int(n))
    if n == 2:
        return True
    elif n < 2 or n % 2 == 0:
        return False
    else:
        for x in xrange(3, int(n ** 0.5) + 1, 2):
            if n % x == 0:
                return False;
    return True

def get_num_bits(alpha_length, key_length):
    """
    Gets the number of bits required to store a key with the alphabet being
    a certain size.
    """
    # why is num_bits doing an "int" instead of a "ceil"?
    # This is because with a floor we will have duplicates! why?  consider
    # this:
    #
    #   allowed_chars = alpha numeric (36 chars)
    #   key_length = 6
    #   Num keys = 36 ^ 6 = 2176782336
    #   Num bits = 31.019550008653876
    #
    #   However if we use 32 bits then we actually 4 billion keys this
    #   means we will need more than 6 alpha numeric characters to store
    #   these!  But with only 6 alpha numeric chars we will have to re
    #   generate the values we already did previously.  So instead we use
    #   31 bits, which comes to about 2 billion values and are infact short
    #   by about 29 million IDs.  This is not an issue however as our
    #   original problem was to have unique keys!
    return int(math.log(alpha_length ** key_length, 2))

def calculate_tap_bits(num_bits):
    """
    Calculate the tap bits for a LFSR given num_bits.
    The number of entries will be even and the values will be relative
    primes of each other (to ensure a Maximal LFSR).
    """
    # TODO: this is bogus - clearly just two bits wont do
    return [num_bits, num_bits - 1]

def update_bits(curr_seed, tap_bits, num_bits):
    """
    Updates the seed by shifting seed and inserting the new bit that is a
    function of the tap bits.
    TODO: Have an easier way to do custom tap functions.
    """
    xored = 0
    for bit in tap_bits:
        xored ^= ((curr_seed >> bit) & 0x01)
    return (curr_seed >> 1) | (xored << (num_bits - 1))

primes_table = map(isprime, xrange(0, 10000))

