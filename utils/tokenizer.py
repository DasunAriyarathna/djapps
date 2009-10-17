
import re

# 
# Simple tokenizer - punctuations are ignored, and quoted strings are
# returned as is
#
def tokenize(string, iterator = True):
    # 
    # A simple tokenizer.  Gets contigious letters/alphabets or a quoted
    # string.
    #
    exp = re.compile('([\'a-zA-Z0-9]+)|(\"[^\"]*\")|(\'[^\']*\')')

    tokens = exp.finditer(string)

    if iterator:
        return tokens
    else:
        outlist = []

        # 
        # Append each token in the iterator to an output list
        # We could have returned the output of findall, however,
        # this returns a tuple of 3 items (to indicate which of the sub
        # rules it matched)
        #
        for token in tokens:
            outlist.append(token.group())

        return outlist
