
import datetime
from django.db.models       import Q
from djapps.rdf.models      import *
from djapps.utils           import *
from djapps.utils.api_utils import *

##################################################################################
##                  API for Entity additions and removals                       ##
##################################################################################

# 
# Gets a node with the given type and data.  If it already exists it is
# returned otherwise it is optionally created (if the user is specified).
#
# What is unique in a node is its data/type combination.  A uriref node can
# have the same data as a literal node, but they are not the same.
#
def GetNode(nodetype, nodedata = "", user = None, prefix = "node_"):
    try:
        return RDFNode.objects.get(Q(nodeData = nodedata) & Q(nodeType = nodetype))
    except RDFNode.DoesNotExist:
        if user is not None:
            creation = None
            try:
                creation = CreationDetail(creator = user, created = datetime.datetime.today(), status = RDFDefaults.STATUS_ACTIVE)
                creation.save()
            except:
                return "Could not create creation details"

            try:
                node = RDFNode(nodeData = nodedata, nodeType = nodetype, creation = creation)
                node.save()

                # 
                # Auto allocate name if necessary or requested
                #
                if nodetype == RDFDefaults.RDF_URIREF_NODE and (nodedata is None or nodedata == ""):
                    node.nodeData = prefix + str(node.id)
                    node.save()

                return node
            except:
                creation.delete()
                return "Could not create node"

    return None

# 
# Add a new property to the system
#
def GetProperty(uri, user = None):
    try:
        return RDFProperty.objects.get(uri = uri)
    except RDFProperty.DoesNotExist:
        if user is not None:
            try:
                creation = CreationDetail(creator = user, created = datetime.datetime.today(), status = RDFDefaults.STATUS_ACTIVE)
                creation.save()
                try:
                    prop = RDFProperty(uri = uri, creation = creation)
                    prop.save()
                    return prop
                except:
                    creation.delete()
            except:
                pass

    return None

# 
# Adds a new relationship tuple, if it doesnt already exist.
#
# Note that this call would fail if the subject is a literal.  
# Literals can only appear in object nodes.
#
# Should we care about duplicates? Yes.  We do not have duplicate links in
# here.  Each link is unique.  Duplicate links should actually have
# explicit mentions either in the form of different property names or in a
# collections node.
#
def GetTuple(subject, property, object, user = None):
    try:
        return RDFTuple.objects.get(subject = subject, property = property, object = object)
    except RDFTuple.DoesNotExist:
        if user is not None:
            try:
                creation = CreationDetail(creator = user, created = datetime.datetime.today(), status = RDFDefaults.STATUS_ACTIVE)
                creation.save()
                try:
                    tuple = RDFTuple(subject = subject, property = property, object = object, creation = creation)
                    tuple.save()
                    return tuple
                except:
                    creation.delete()
            except:
                pass

    return None

# 
# Adds a new graph
#
def AddGraph(user, name):
    try:
        creation = CreationDetail(creator = user, created = datetime.datetime.today(), status = RDFDefaults.STATUS_ACTIVE)
        creation.save()
        try:
            graph = RDFGraph(name = name, creation = creation)
            graph.save()
            return graph
        except:
            creation.delete()
    except:
        pass

    return None

# 
# Removes a generic item based on its class
#
def RemoveItem(ItemClass, item):
    if item is None:
        return false

    try:
        item.delete()
        return True
    except ItemClass.DoesNotExist:
        return False

# 
# Remove a node from the system
#
def RemoveNode(node):
    return RemoveItem(RDFNode, node)

# 
# Remove a property from the system
#
def RemoveProperty(property):
    return RemoveItem(RDFProperty, property)

# 
# Removes a graph
#
def RemoveGraph(graph):
    return RemoveItem(RDFGraph, graph)

# 
# Removes a relationship tuple, if it exists.
#
def RemoveTuple(tuple):
    return RemoveItem(RFDTuple, tuple)

