
import datetime, __builtin__
import simplejson as json
from django import forms as djangoforms
from django.db import models as djangomodels

import logging
logger = logging.getLogger(__name__)

class OurJsonEncoder(json.JSONEncoder):
    def default(self, o, *args, **kwargs):
        if type(o) is datetime.datetime: return str(o)
        elif hasattr(o, "to_json"): return o.to_json(*args, **kwargs)
        elif hasattr(o, "toJson"): return o.toJson(*args, **kwargs)
        elif isinstance(o, Exception):
            return {'args': o.args, 'message': o.message}
        elif isinstance(o, djangoforms.BaseForm):
            out = {}
            if hasattr(o, "instance"):
                out["instance"] = getattr(o, "instance")
            return out
        elif isinstance(o, djangomodels.query.QuerySet):
            return [self.default(v) for v in o]
        else:
            logger.error("Unknown type: %s", str(type(0)))
        return super(OurJsonEncoder, self).default(o)

def json_encode(data, *args, **kwargs):
    return OurJsonEncoder().encode(data, *args, **kwargs)

def json_decode(data):
    if data:
        return json.JSONDecoder().decode(data)
    else:
        return None

