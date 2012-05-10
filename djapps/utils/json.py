
import datetime, __builtin__
from django import forms as djangoforms
from django.db import models as djangomodels
from django.utils import simplejson
from django.utils.simplejson import decoder

class OurJsonEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if type(o) is datetime.datetime: return str(o)
        elif hasattr(o, "to_json"): return o.to_json()
        elif hasattr(o, "toJson"): return o.toJson()
        elif isinstance(o, djangoforms.BaseForm):
            out = {}
            if hasattr(o, "instance"):
                out["instance"] = json_encode(getattr(o, "instance"))
            return out
        elif isinstance(o, djangomodels.query.QuerySet):
            return [self.default(v) for v in o]
        else:
            print "Unknown type: ", type(o)
        return super(OurJsonEncoder, self).default(o)

def json_encode(data):
    return OurJsonEncoder().encode(data)

def json_decode(data):
    if data:
        from django.utils import simplejson
        return simplejson.JSONDecoder().decode(data)
    else:
        return None

