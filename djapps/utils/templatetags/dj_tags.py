from django import template
from django.template import Template, Node, NodeList, resolve_variable, Context
from django.template import TemplateSyntaxError, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END

from django.conf import settings

import sys, os, logging

register = template.Library()

@register.filter
def djloginlink(value, arg):
    from djapps.utils import urls   as djurls
    return djurls.get_login_url(arg)

@register.filter
def djlogoutlink(value, arg):
    from djapps.utils import urls   as djurls
    return djurls.get_logout_url(arg)

@register.filter
def djregisterlink(value, arg):
    from djapps.utils import urls   as djurls
    return djurls.get_register_url(arg)

#
# The tag for objid.  Simpler way to get the id of an object regardless
# of GAE or django.
#
@register.tag(name = "objid")
def do_objid(parser, token):
    """
    outputs the id of an object.

    So eg:
        {% objid object %}
    """
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    return DJObjIdNode(format_string)

#
# The node processor for "objid" nodes
#
class DJObjIdNode(template.Node):
    def __init__(self, format_string):
        # remove initial / or ./ or ../ so that we dont endup going
        # somewhere where we shouldnt be
        self.theObject = format_string

    def render(self, context):
        theObject = context[self.theObject]
        from djapps.dynamo import helpers
        return helpers.get_object_id(theObject)

#
# The tag for djflash.  ie for including flash content on a page.  Instead
# of having to muck about with all that browser dependencies.
#
# @register.inclusion_tag('djapps/flashplayer.html')
@register.tag(name = "djflash")
def do_djflash(parser, token):
    """
    A simple tag for including flash contents in a page.
    So eg:
        {% djflash URI:location requiredMajorVersion:9 requiredMinorVersion:0 requiredRevision:124 width:100% height:100% name:objname align:center bgcolor:#ffffff %}
    """
    contents    = token.split_contents()
    tagname     = contents[0]
    args        = contents[1:]
    arg_match   = {
        'djsrc': 'fpFlashObjectSrc',
        'src': 'fpFlashObjectSrc',
        'name': 'fpFlashObjectName',
        'width': 'fpWidth',
        'height': 'fpHeight',
        'align': 'fpAlign',
        'minorVersion': 'fpMinorVersion',
        'majorVersion': 'fpMajorVersion',
        'revision': 'fpRevision',
        'bgcolor': 'fpBGColor'
    }
    arguments   = {
        'fpWidth': "100%",
        'fpHeight': "100%",
        'fpBGColor': "#ffffff",
        'fpAlign': "center",
        'fpMajorVersion': 10,
        'fpMinorVersion': 0,
        'fpRevision': 0,
    }

    flashSrc    = None

    for arg in args:
        parts = arg.split(":")
        param, value = parts[0], parts[1]

        if len(parts) != 2:
            raise template.TemplateSyntaxError("Invalid argument: %s.  " +
                                               "Arguments must be of the type 'name':'value'" % arg)
        if param not in arg_match:
            raise template.TemplateSyntaxError("Invalid parameter: %s.  Valid parameters are %s." % (param, ", ".join(arg_match.keys())))

        #
        # strip any quotes off
        #
        if value.endswith('"'):
            value = value[:-1]
        if value[0] == '"':
            value = value[1:]

        if param == "src":
            """
            if value[0] == "/":
                value = value[1:]
            if not value.lower().startswith("http://"):
                value = settings.PROJ_STATIC_HOST + "/" + value
            """

            flashSrc = value
        else:
            arguments[arg_match[param]] = value

    if not flashSrc not in arguments:
        raise template.TemplateSyntaxError("djflash MUST have a 'djsrc' or 'src'parameter")

    if 'fpFlashObjectName' not in arguments:
        raise template.TemplateSyntaxError("djflash MUST have a 'name' parameter")

    return DJFlashNode(flashSrc, arguments)

#
# The node processor for "djflash" nodes, which add
# flash objects to the page.
#
class DJFlashNode(template.Node):
    def __init__(self, src, arguments):
        self.flashSrc       = src
        self.arguments      = arguments

    def render(self, context):
        self.arguments['fpFlashObjectSrc'] = self.flashSrc

        # TODO: provide a better way to find this template
        filepath    = "djapps/flashplayer.html"

        try:
            from django.template.loader import get_template
            t = get_template(filepath)
            return t.render(Context(self.arguments))
        except TemplateSyntaxError, e:
            if settings.DEBUG:
                return "[Included template had syntax error: %s]" % e
            else:
                return '' # Fail silently for invalid included templates.

def do_ifin(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) < 3:
        raise TemplateSyntaxError, "%r takes atleast two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfInNode(bits[1], bits[2:], nodelist_true, nodelist_false, negate)

@register.tag
def ifin(parser, token):
    """
    Outputs the contents of the block if the value of the first argument is
    in the argument list formed from second argument onwards.

    Examples::

        {% ifin user.id comment.user_id comment2.user_id %}
            ...
        {% endifequal %}

        {% ifnotin user.id "asdf" 3 comment.user_id %}
            ...
        {% else %}
            ...
        {% endifnotequal %}
    """
    return do_ifin(parser, token, False)

@register.tag
def ifnotin(parser, token):
    """
    Outputs the contents of the block if the value of the first argument is
    not in the argument list formed from second argument onwards.
    See ifin.
    """
    return do_ifin(parser, token, True)

class IfInNode(Node):
    def __init__(self, var1, var_list, nodelist_true, nodelist_false, negate):
        from django.template import Variable, VariableDoesNotExist
        self.var1, self.var_list = Variable(var1), [ Variable(var) for var in var_list ]
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfEqualNode>"

    def render(self, context):
        from django.template import Variable, VariableDoesNotExist
        try:
            val1 = self.var1.resolve(context)
        except VariableDoesNotExist:
            val1 = None
        try:
            val_list = [ var.resolve(context) for var in self.var_list ]
        except VariableDoesNotExist:
            val_list = None
        if (self.negate and val1 not in val_list) or (not self.negate and val1 in val_list):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

