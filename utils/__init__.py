
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

