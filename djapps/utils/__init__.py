
API_SUCCESS     = "success"
API_FAILURE     = "failure"
API_BINARY      = "binary"
API_FAILURES    = "failures"

# 
# Generates an api output structure indicating success
#
def api_result(code, value, **kwparams):
    out = {'code': code, 'value': value}
    out.update(kwparams)
    return out

def to_str_keys(indict):
    """
    Problem with python 2.6.5 and below is you cannot pass dicts with
    unicode key.  So this method returns a copy of the dict with the
    unicode keys converted to ascii strings.
    """
    return dict([[str(x), indict[x]] for x in indict.keys()])

