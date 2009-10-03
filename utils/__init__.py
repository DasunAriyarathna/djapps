
import types
from decimal import *
from django.utils import simplejson as json
from django.http import HttpResponse, HttpResponseRedirect

import json as djjson

API_SUCCESS     = "success"
API_FAILURE     = "failure"
API_BINARY      = "binary"
API_FAILURES    = "failures"

# 
# Generates an api output structure indicating success
#
def api_result(code, value):
    return {'code': code, 'value': value}

def json_encode(data):
    """
    The main issues with django's default json serializer is that
    properties that had been added to a object dynamically are being
    ignored (and it also has problems with some models).
    """
    from django.db import models

    def _any(data):
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret
    
    ret = _any(data)
    
    # from django.core.serializers.json import DateTimeAwareJSONEncoder
    # return json.dumps(ret, cls=DateTimeAwareJSONEncoder)
    return djjson.json_encode(ret)

# 
# Formats an object to the appropriate output - determined by the
# output_fmt value.
#
# Following choices for output_fmt are available:
#   json        -   Output as json 
#   xml         -   Output as xml (not yet implemented)
#
#   XXX         -   Otherwise use the template specified by XXX
#
# By default output_fmt points to a generic default template.
#
# SO if you dont have any templates, do not specify them.
#
def FormatHttpResponse(response, output_fmt = "json"):
    # 
    # Send out json for now
    #
    if output_fmt is None or output_fmt == '':
        output_fmt = "json"

    lower = output_fmt.lower()

    if lower == "json":
        return HttpResponse(json_encode(response))

    if lower == "xml":
        return HttpResponse("XML Output Not Yet Implemented")

    return render_to_response(output_fmt, response)

