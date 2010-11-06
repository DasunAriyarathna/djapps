
from django.utils.functional import lazy

def ugettext(message):
    # return real_ugettext(message)
    return message

ugettext_lazy = lazy(ugettext, unicode)

