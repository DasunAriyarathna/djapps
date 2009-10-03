# Create your views here.

import datetime

# from django.core import serializers
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader

# 
# Load our custom django libraries and utilities
#
from djapps.accounts.models     import DefaultUserProfile
from djapps.utils.json_encode   import *
from djapps.utils.api_utils     import *
from djapps.utils               import misc as djmisc

import api

#######################
# Utility functions
#######################

# 
# The main view
#
def list(request):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    result = djmisc.CheckAuthAndReqMethod(request, 'GET')

    # 
    # we have an error so return immediately
    #
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    numlevels = 1
    if request.GET and 'levels' in request.GET:
        numlevels = request.GET['levels']

    return djmisc.FormatHttpResponse(api.ListFolder(user, path, numlevels), output_fmt)

# 
# Delete one or more files or folders
#
# All entries (if more than one) are reported as "child" entries relative
# to the current path.  These are specified as the content of the request.
#
# Return will be a success or a list of return values if there are
# successes and failures for some items.
#
def delete(request):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    result = djmisc.CheckAuthAndReqMethod(request, 'DELETE')

    # 
    # we have an error so return immediately
    #
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    recurse = False
    if request.GET:
        if 'recurse' in request.GET:
            recurse = request.GET['recurse']

    data = request.POST
    children = []

    if 'fileList' in request.POST:
        # we have multiple items to delete
        data        = request.POST['fileList']
        children    = eval(data)

    return djmisc.FormatHttpResponse(api.Delete(user, path, children, recurse), output_fmt)

#
# Get node attributes
#
def getattr(request, path):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    result = djmisc.CheckAuthAndReqMethod(request, 'GET')

    # 
    # we have an error so return immediately
    #
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

# 
# Create a new node (either a file or a directory)
#
def mknode(request, is_folder):
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    result = djmisc.CheckAuthAndReqMethod(request, 'PUT')

    # 
    # we have an error so return immediately
    #
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    recurse = False
    if request.GET and 'recurse' in request.GET:
        recurse = request.GET['recurse']

    return djmisc.FormatHttpResponse(api.MkNode(request.user, path, is_folder, recurse), output_fmt)

# 
# Get node attributes
#
def getattr(request):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    # 
    # Check if we have the right http method
    #
    result = djmisc.CheckAuthAndReqMethod(request, 'GET')
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    return djmisc.FormatHttpResponse(api.GetAttributes(user, path), output_fmt)

# 
# Reads from a file
#
def read(request):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    # 
    # Check if we have the right http method
    #
    result = djmisc.CheckAuthAndReqMethod(request, 'GET')
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    offset  = 0
    len     = -1
    if 'offset' in request.GET:
        offset = request.GET['offset']

    if 'len' in request.GET:
        len = request.GET['len']

    return djmisc.FormatHttpResponse(api.Read(user, path, offset, len), output_fmt)

# 
# Writes to a file
#
def write(request):
    user        = request.user
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    # 
    # Check if we have the right http method
    #
    result = djmisc.CheckAuthAndReqMethod(request, 'POST')
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    offset  = 0
    len     = -1

    if 'offset' in request.POST:
        offset = request.POST['offset']

    if 'len' in request.POST:
        len = request.POST['len']

    data = request.POST

    return djmisc.FormatHttpResponse(api.Write(user, path, offset, len, data), output_fmt)

# 
# Downloads a file
#
def downloadfile(request):
    user        = request.user
    reqm        = request.method
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    # 
    # Check if we have the right http method
    #
    result = djmisc.CheckAuthAndReqMethod(request, 'GET')
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    result = api.DownloadFile(user, path)

    if API_BINARY in result:
        return result[API_BINARY]

    return djmisc.FormatHttpResponse(result, output_fmt)

# 
# Called to upload a file
#
def uploadfile(request):
    user        = request.user
    reqm        = request.method
    path        = request.META['PATH_INFO']
    output_fmt  = djmisc.GetOutputFormat(request)

    # 
    # Check if we have the right http method
    #
    result = djmisc.CheckAuthAndReqMethod(request, 'POST')
    if result is not None:
        return djmisc.FormatHttpResponse(result, output_fmt)

    uploadFileField = 'uploadedFile'
    if request.GET and 'fieldName' in request.GET:
        uploadFileField = request.GET['fieldName'];

    post        = request.POST
    files       = request.FILES

    # if not uploadFileField in files:
        # return djmisc.FormatHttpResponse(api_failure(-1, "Invalid file"), output_fmt);

    uploadFile  = files[uploadFileField]
    uploadPath  = path
    filename    = uploadFile['filename']

    result = api.UploadFile(user, uploadPath, filename, uploadFile['content'])

    return djmisc.FormatHttpResponse(result, output_fmt)

