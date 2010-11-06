
import datetime, __builtin__
from django.utils import simplejson
from django.utils.simplejson import decoder

class OurJsonEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if type(o) is datetime.datetime: return str(o)
        elif hasattr(o, "to_json"): return o.to_json()
        elif hasattr(o, "toJson"): return o.toJson()
        # elif type(o) is __builtin__.generator: return [super(OurJsonEncoder, self).default(val) for val in o]
        return super(OurJsonEncoder, self).default(o)

def json_encode(data):
    return OurJsonEncoder().encode(data)

def json_decode(data):
    if data:
        from django.utils.simplejson.decoder import JSONDecoder as jdec
        return jdec().decode(data)
    else:
        return None

"""

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet

def maybe_call(x):
    if callable(x): return x()
    return x


class JSONEncoder(DjangoJSONEncoder):
    '''An extended JSON encoder to handle some additional cases.

    The Django encoder already deals with date/datetime objects.
    Additionally, this encoder uses an 'as_dict' or 'as_list' attribute or
    method of an object, if provided. It also makes lists from QuerySets.
    '''
    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return maybe_call(obj.as_dict)
        elif hasattr(obj, 'as_list'):
            return maybe_call(obj.as_list)
        elif isinstance(obj, QuerySet):
            return list(obj)
        return super(JSONEncoder, self).default(obj)
json_encode = JSONEncoder().encode

"""

