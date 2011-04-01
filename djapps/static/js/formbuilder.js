//
// We want a way to build forms easily.
//
// How?  It is pretty painful to do appendChilds and CreateElements and so
// on.  Simple configs would be good.
//
// Eg the following:
//
//  {
//   type: 'div',   // defaults to "div" if not specified
//   nameid: 'xxx',
//   attr: {attrib1: val1, attr2: val2},
//   style: {width: xx, height: yy},
//   kids: [ node1, node2, node3...] 
//   handlers: {ev1: handler1, ev2: handler2... } // list of all handlers to add
//  }
//
// "nameid" is for specifying both the name AND the id to the same value -
// a shortcut for "attr: {name: xxx, id: xxx}", do not specify both, the
// attr will be ignored.
//
// Should create a div under a specific parent element.
//
// Finding divs should be based on starting from a given parent and finding
// child items recursively.
//
// What will be the return type?
//
// Basic return types required are:
//
// 1. The root of the dom tree.
// 2. A table that holds a reference to a given node in the dom tree by
// ites name.  This is optional, as a search can reveal this.  If an app is
// interested it can keep track of this info anyway.
//
// Issues:
//
// Should we verify duplicate node names?
// How to have templating in it so we can have variable names in as well?
// So any attribute/variable can be enclosed in %% and we can substitute
// based on the variable value found in the context object
//
function Build(cfg, context)
{
    var doc = document;
    if (context.doc)
        doc = context.doc;

    if (typeof(cfg) == "function")
    {
        cfg = cfg(context);

        if (typeof(cfg) ==  "string")
            return doc.createTextNode(cfg);

        return cfg;
    }

    if (typeof(cfg) == "string")
    {
        return doc.createTextNode(cfg);
    }

    // by default we will creating a "div"
    if (!cfg.type)
    {
        cfg.type = "div";
    }

    // remove leading and trailing spaces
    cfg.type = cfg.type.trim();

    /******************************************************************
    var root    = null;
    var out     = null;

    var els = cfg.type.split(" ");

    for (var i = 0; i < els.length;i++)
    {
        if (els[i] != "")
        {
            var node = CreateEl(els[i]);
            if (root == null)
            {
                root = out = node;
            }
            else
            {
                AddChild(out, els[i], node);
                out = node;
            }
        }
    }
    *******************************************************************/

    // another shortcut - we can have multiple entries in the type field
    // This is to indicate that we ahve a series of nodes with no
    // attributes so that we dont have to call "kid" multiple times
    //
    // eg "tr td input" indicates we need something like:
    //
    // <tr><td><input> and that all attrs and styles apply to the input
    // element rather than the tr element
    var out = CreateEl(cfg.type, {attribs: cfg.attr, style: cfg.style}, context);

    if (cfg.nameid)
    {
        if (typeof(cfg.nameid) == "function")
            cfg.nameid = cfg.nameid(context);
        out.name = out.id = cfg.nameid;
    }

    for (var kid in cfg.kids)
    {
        var kidNode = Build(cfg.kids[kid], context);

        if (kidNode != null && typeof(kidNode) != "undefined")
            AddChild(out, cfg.type, kidNode);
    }

    for (var handler in cfg.handlers)
    {
        var handlerObj = cfg.handlers[handler];
        AddEventListener(out, handler, handlerObj.handlerFunc, handlerObj.capture);
    }

    if (cfg.notify && context && context.nodeCreated)
        context.nodeCreated(out);

    return out;
}

// 
// Finds a root node given the fullname
// Fullnames are specified by 
//
//  a.b.c.d.e
//
//  if any of the items is * then all child nodes are searched till the
//  first one with a match is found - Use this sparingly
//
function Find(root, fullname)
{
    var notempty = function(elem, index, array) { return elem != ""; }
    var names = fullname.split(".").filter(notempty);
    return _myFind(root, names);
}

// 
// Find all elements from the root with the given name (a DFS), upto a
// certain level
//
function FindAll(root, name, level)
{
    if (!level)
        level = -1;

    var child   = null;
    var nodes   = [];
    var stack   = [{item: root, depth: 0}];

    while (stack.length > 0)
    {
        var popped  = stack.pop();
        var curr    = popped.item;

        if (curr.id == name)
            nodes.push(curr);

        if (level < 0 || popped.depth < level)
        {
            for (var i = 0;i < curr.childNodes.length;i++)
            {
                stack.push({item: curr.childNodes[i], depth: popped.depth + 1});
            }
        }
    }

    return nodes;
}

// 
// Actual worker function for Find
//
function _myFind(root, names)
{
    var stack = [];
    var curr  = root;

    for (var i = 0;i < names.length;i++)
    {
        var name = names[i].trim();
        if (name == "*")
        {
            // TODO
            alert('Wild Cards not yet implemented');
        }
        else
        {
            var child = null;
            for (var j = 0;j < curr.childNodes.length;j++)
            {
                if (curr.childNodes[j].id == name)
                {
                    child = curr.childNodes[j];
                    break ;
                }
            }
            curr = child;
            if (curr == null)
                return null;
        }
    }

    return curr;
}

// 
// A single point for adding a node to a parent.  Adding to a parent isnt
// straight forward - for most dom elements, adding is a matter of doing an
// appendChild, however for say "tr" elements appendChild must be done on
// the tr.cells[x] instead, while keeping the parent as the tr element
// itself!
//
function AddChild(parent, type, node)
{
    parent.appendChild(node);
}

// 
// Shortcut for creating links
//
function CreateLink(label, link, config, context)
{
    if ( ! link)
    {
        link = 'javascript:void(0)';
    }

    if ( ! config )
    {
        config = {attribs: {href: link}};
    }
    else if ( ! config.attribs )
    {
        config.attribs = {href: link};
    }
    else
    {
        config.attribs.href = link;
    }

    var out = CreateEl("a", config, context);

    if (label == null)
    {
        label = "";
    }

    if (typeof(label) == "string")
    {
        out.appendChild(document.createTextNode(label));
    }
    else
    {
        out.appendChild(label);
    }
    return out;
}

// 
// Shortcut for CreateEl("td"...)
//
function CreateCol(config, context)
{
    return CreateEl("td", config, context);
}

// 
// Shortcut for CreateEl("tr"...)
//
function CreateRow(config, context)
{
    return CreateEl("tr", config, context);
}

// 
// Short cut for CreateEl("div")
//
function CreateDiv(config, context)
{
    return CreateEl("div", config, context);
}

// 
// Creates an element while also setting its attributes
//
// Config can have the following attributes:
//
// elname   -   Element name
// attribs  -   Optional Structure containting element's 
//              attributes and their values
// styles   -   Optional Structure containting elements style 
//              attributes and their values
// parent   -   Optional parent under which this item is added to
// index    -   Optional index where this item is inserted.
// doc      -   Optional document used to create the element
//
function CreateEl(elname, config, context)
{
    var el      = (config && config.doc ? config.doc : document).createElement(elname);
    var attribs = config ? config.attribs : null;
    var styles  = config ? config.style : null;
    var parent  = config ? config.parent : null;
    var index   = config ? config.index : null;

    if (attribs)
    {
        for (attr in attribs)
        {
            var at = attribs[attr];
            if (typeof(at) == "function")
                at = at(context);

            el[attr] = at;
        }
    }

    if (styles)
    {
        for (style in styles)
        {
            var st = styles[style];
            if (typeof(st) == "function")
                st = st(context);
            el.style[style] = st;
        }
    }

    if (parent)
    {
        if (index >= 0)
        {
            parent.insertChild(el, index);
        }
        else
        {
            parent.appendChild(el);
        }
    }

    return el;
}

// 
// Prevent default action to be taken on an event
//
function PreventEventDefault(ev)
{
    if (ev.preventDefault) 
        ev.preventDefault();
    ev.returnValue = false;
}

// 
// Add an event listener to an element in a browser independent way
//
function AddEventListener(el, type, func, capture)
{
    if (el.addEventListener)
    {
        el.addEventListener(type, func, !!capture);
    }
    else if (el.attachEvent)
    {
        el.attachEvent("on" + type, func);
    }
    else
    {
        alert('Unknown platform');
    }
}

