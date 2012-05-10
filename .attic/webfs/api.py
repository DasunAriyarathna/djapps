import datetime, random, sha
import smtplib, os, sys, mimetypes

from django.http import HttpResponse, HttpResponseRedirect
from djapps.accounts.models     import DefaultUserProfile
from djapps.utils.json_encode   import *
from djapps.utils.api_utils     import *

# 
# HACK HACK HACK!!!
#
import testzone.settings

# 
# Create a file or a folder
#
def MkNode(user, path, isfolder, recurse = False):
    if recurse is None:
        recurse = False

    oldpath = path
    path    = _GetRealPath(user.username, path)
    if path is None:
        return api_failure(-1, "Invalid path")

    if os.path.isfile(path):
        return api_failure(-1, "File already exists")

    if os.path.isdir(path):
        return api_failure(-1, "Folder already exists: %s" % oldpath)

    pardir = os.path.dirname(path)

    if not os.path.isdir(pardir) and not recurse:
        return api_failure(-1, "Parent directory does not exist")

    if isfolder:
        os.makedirs(path)
        return api_success(0, "File successfully created")
    else:
        file = open(path, "wb")
        file.close()
        return api_success(0, "Folder successfully created")

# 
# List folder contents
#
def ListFolder(user, folder = "/", levels = 1):
    if folder is None:
        folder = "/"

    try:
        levels = int(levels)
    except:
        levels = 1

    if levels is None or levels <= 0:
        levels = 1

    path    = _GetRealPath(user.username, folder)
    if path is None:
        return api_failure(-1, "Invalid path")

    dirlist = _readdir(path, levels)

    if dirlist is not None:
        return api_success(0, dirlist)
    else:
        return api_failure(-1, "Invalid folder")

# 
# Delete file or a folder
#
def Delete(user, path, children, recurse = False):
    if path is None:
        return api_failure(-1, "No folder specified")

    if (children is None or len(children) == 0) and (path == "/" or path == "" or path is None):
        return api_failure(-1, "Cannot remove root folder")

    if recurse is None:
        recurse = False

    # 
    # Fetch the path
    #
    path2   = path
    path    = _GetRealPath(user.username, path)
    if path is None:
        return api_failure(-1, "Invalid path: " + path2)

    if children is None or len(children) == 0:
        return _delrecursive(path, recurse)
    else:
        retvals = []
        for child in children:
            realpath = _GetRealPath(user.username, path + "/" + child)
            if realpath is None:
                retvals.append(api_failure(-1, "(%s) not found" % child))
            else:
                ret = _delrecursive(path + "/" + child, recurse)
                if 'failure' in ret:
                    retvals.append(ret)

        if len(retvals) == 0:
            return api_success(0, "Deletion successful")

        return api_failures(retvals);

# 
# Get node attributes
#
def GetAttributes(user, item):
    path    = _GetRealPath(user.username, item)
    if path is None:
        return api_failure(-1, "Invalid path")

    try:
        isdir = os.path.isdir(path)
        st = os.stat(path)
        return api_success(0,
                        {'name': item,
                         'size': st.st_size,
                         'isdir': isdir,
                         'created': st.st_ctime,
                         'modified': st.st_mtime
                        })
    except:
        pass

    return api_failure(-1, "Cannot obtain attributes")

# 
# Downloads a specific file
#
def DownloadFile(user, path):
    oldpath = path
    path    = _GetRealPath(user.username, path)

    if path is None:
        return api_failure(-1, "Invalid path")

    if os.path.isdir(path):
        return api_failure(-1, "'%s' is a directory." % oldpath)

    basename = os.path.basename(oldpath)
    mimetype, encoding = mimetypes.guess_type(path)
    resp = HttpResponse(mimetype = mimetype);
    resp['Content-disposition'] = ('Attachment; filename=%s' % basename)
    try:
        fd = open(path, "rb")
        resp.write(fd.read())
        fd.close()
    except:
        return api_failure(-1, "Could not open file, '%s'." % oldpath)

    return api_binary(resp);

# 
# Upload a file to a given location
#
def UploadFile(user, path, file, content):
    path = path + "/" + file
    path = _GetRealPath(user.username, path)

    if path is None:
        return api_failure(-1, "Invalid path")

    try:
        fd = open(path, "wb")
        fd.write(content)
        fd.close()
    except:
        return api_failure(-1, "Could not write to file")

    return api_success(0, "File upload successful")

# 
# Read the contents of a file
#
def Read(user, file, offset, len):
    if file is None:
        return api_failure(-1, "Invalid file");

    path    = _GetRealPath(user.username, file)
    if path is None:
        return api_failure(-1, "Invalid path")

    if not os.path.isfile(path):
        return api_failure(-1, "Invalid file");

    if offset is None:
        offset = 0

    if len is None:
        len = -1

    fin = open(path, "r+")

    if offset > 0:
        fin = fin.seek(offset)

    if len <= 0:
        output = fin.read()
    else:
        output = fin.read(len)

    fin.close()

    return api_success(0, output)
    try:
        pass
    except:
        pass

    return api_failure(-2, "Unknown error");

# 
# Write data to a file at a given position
#
def Write(user, file, offset, len, data):
    path    = _GetRealPath(user.username, file)
    if path is None:
        return api_failure(-1, "Invalid path")

    if offset is None:
        offset = 0

    if len is None:
        len = -1

    fout = None
    if os.path.isfile(path):
        fout = open(path, "rw+")
    else:
        fout = open(path, "w+")

    fout.seek(offset)
    if len <= 0:
        fout.write(data['contents'])
    else:
        fout.write(data['contents'][:len])
    fout.close()

    try:
        pass
    except:
        return api_failure(-1, "Could not open file for writing")

    return api_success(0, "File written successfully");

# 
# Rename an item
#
def Rename(from_name, to_name):
    pass

# 
# set node attributes
#
def SetAttributes(item, attribs):
    pass

# 
# real work in reading the folder contents
#
def _readdir(path, levels = 1):
    entries2 = []

    try:
        entries2 = os.listdir(path)
    except:
        return None

    # 
    # Sort the dir list!
    #
    tmp = [(not os.path.isdir(name), name) for name in entries2]
    tmp.sort()
    entries = [name for isdir, name in tmp]

    out = []

    for d in entries:
        name = path + "/" + d
        isdir = os.path.isdir(name)
        st = os.stat(name)
        stinfo = {'name': d,
                  'size': st.st_size,
                  'isdir': isdir,
                  'created': st.st_ctime,
                  'modified': st.st_mtime
                 }
        if isdir and levels > 1 :
            children = _readdir(name, levels - 1)

            if children is None:
                return None

            stinfo['children'] = children

        out.append(stinfo)

    return out

# 
# TODO:
# At the moment we are using a simple storage scheme
# Everything is stored as <base_dir>/<username>/path/
#
# This will obviously have to be changed so that any file can be anywhere
# to take advantage of distributed fses or mounted shares.
#
def _GetBaseFolder(username):
    return "%s/%s" % (testzone.settings.FS_ROOT, username)

# 
# Get the real path of a user's folder
# Ensures no path above user's root folder is returned
#
def _GetRealPath(username, folder):
    base = _GetBaseFolder(username)

    # 
    # Try creating the user's home directory - this SHOULD exist
    #
    if not os.path.isdir(base):
        os.makedirs(base)

    out = os.path.realpath(base + "/" + folder)
    if out.startswith(base):
        return out

    return None

# 
# Delete folder or a file - recursively if specified
#
def _delrecursive(path, recurse = False):
    try:
        if os.path.isdir(path):
            dirlist = os.listdir(path)

            if len(dirlist) > 0 and not recurse:
                return api_failure(-1, "Folder not empty")
            else:
                for item in dirlist:
                    _delrecursive(path + "/" + item, recurse)

            os.rmdir(path)
        else:
            os.unlink(path)
    except:
        return api_failure(-1, "Deletion failed")

    return api_success(0, "Deletion successful")

