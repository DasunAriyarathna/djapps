
import sys
from django.http import HttpResponse, HttpResponseRedirect, Http404
import json as djjson
from . import api_result, codes

JSON_CONTENT_TYPE = "application/json"

def APIResponse(request, result, mimetype=None, status=None,
                content_type=None, template_name = None, redirect_to = None,
                format_param = "format", formatter_params = None):
    if isinstance(result, HttpResponse):
        response = result
    elif redirect_to:   # redirect provided so ignore all else and redirect
        response = HttpResponseRedirect(redirect_to)
    else:
        import request as djrequest
        format = djrequest.get_var(request, format_param, "")
        if format == "json":
            formatter_params = formatter_params or {}
            content_type = content_type or JSON_CONTENT_TYPE
            if type(formatter_params) is list:
                response = HttpResponse(djjson.json_encode(result, *formatter_params),
                                        content_type = content_type)
            else:
                response = HttpResponse(djjson.json_encode(result, **formatter_params),
                                        content_type = content_type)
        else:
            from django.template import RequestContext
            response_data = result[0]
            context = RequestContext(request)
            response = render_to_response(result[1], response_data, context)
    response["Access-Control-Allow-Origin"] = "*"
    if content_type: response["Content-Type"] = content_type
    return response

