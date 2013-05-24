
import sys
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
import json as djjson
from . import api_result, codes

JSON_CONTENT_TYPE = "application/json"

def APIResponse(request, code, result, template_name = None, redirect_to = None,
                mimetype=None, status=None, content_type=None, 
                format_param = "format", formatter_params = None):
    if isinstance(result, HttpResponse):
        response = result
    elif redirect_to:   # redirect provided so ignore all else and redirect
        response = HttpResponseRedirect(redirect_to)
    else:
        import request as djrequest
        format = djrequest.get_var(request, format_param, "")
        if code is not None: result = {'code': code, 'value': result}
        if format == "raw":
            return result
        elif format == "json" or not template_name:
            formatter_params = formatter_params or {}
            content_type = content_type or JSON_CONTENT_TYPE
            if type(formatter_params) is list:
                json_str = djjson.json_encode(result, *formatter_params)
            else:
                json_str = djjson.json_encode(result, **formatter_params)
            response = HttpResponse(json_str, content_type = content_type, mimetype = mimetype, status = status)
        else:
            from django.template import RequestContext
            context = RequestContext(request)
            if hasattr(template_name, "__call__"):
                template_name = template_name(request)
            response = render_to_response(template_name, result, context, mimetype = mimetype)
    if content_type: response["Content-Type"] = content_type
    response["Access-Control-Allow-Origin"] = "*"
    return response

