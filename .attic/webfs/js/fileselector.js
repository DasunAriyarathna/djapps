
var FSDlgTemplate = {
    style: {position: "absolute", backgroundColor: "#AAA", // MozOpacity: 0.8,
    'text-align': "center", 'z-index': 10000, visibility: "hidden",
    left: 0, top: 0, width: "100%", height: "100%"},
    kids: [
    {
        nameid: "FSDlgContentDiv",
        notify: true,
        style: { width: "400px", top: "50%", MozOpacity: 10,
                 margin: "30px auto", border: "1px solid #000", paddding: "15px"}
    },{
        style: {width: "100%", textAlign: 'center'},
        kids: [
        {
            nameid: "dlgOkButton", type: "input", notify: true,
            attr: {type: 'button', value: "Ok"},
        },
        {
            nameid: "dlgCancelButton", type: "input", notify: true,
            attr: {type: 'button', value: "Cancel"},
        }]
    }]
};

// 
// Content template for the "New Directory" dialog
//
var FSNewDirDlgTemplate = 
{
    style: { width: "100%", display: "none", visibility: 'hidden', float: 'left'},
    kids:[
    "Enter directory name: ",
    { type: "br" },
    {
        nameid: "newDirNameField", type: "input", notify: true, 
        attr: {type: 'text'}, style: {width: "100%"}
    }]
};

// 
// Content template for the "Rename" dialog
//
var FSRenameDlgTemplate = 
{
    style: { width: "100%", display: "none", visibility: 'hidden', float: 'left'},
    kids:[
    "Rename/Move To: ",
    { type: "br" },
    {
        nameid: "newLocField", type: "input", notify: true, 
        attr: {type: 'text'}, style: {width: "100%"}
    }]
};

// 
// Content template for the "upload file" dialog
//
var FSUploadDlgTemplate = 
{
    style: { width: "100%", display: "none", visibility: 'hidden', float: 'left'},
    kids:[
    "Enter file to upload: ",
    { type: "br" },
    { type: "iframe", style: {display: "none"},
        nameid: function(ctx) { return ctx.fs_id + 'uploadResultsIFrame'; } },
    {
        type: "form", nameid: "fileUploadForm", notify: true,
        attr:
        {
            target: function(ctx) { return ctx.fs_id + 'uploadResultsIFrame'; },
            method: "POST", enctype: "multipart/form-data"
        },
        kids: [{
            type: "input", nameid: "uploadFileField", notify: true, 
            attr: {type: 'file'}, style: {width: "100%"}
        }]
    }]
};

//
// The main template for the file selector control
//
var FSTemplate = {
    nameid: 'contentHolder',
    style: {width: '100%', height: '100%', 'text-align': 'center'},
    kids: [
    { 
        nameid: 'buttonPanelDiv',
        style: {textAlign: "center"},
        notify: true, 
        kids: [
        { nameid: "fsUpButton", type: "input", notify: true, attr: {type: 'button', value: "Up"}},
        { nameid: "fsHomeButton", type: "input", notify: true, attr: {type: 'button', value: "Home"}},
        { nameid: "fsNewButton", type: "input", notify: true, attr: {type: 'button', value: "New"}},
        { nameid: "fsDeleteButton", type: "input", notify: true, attr: {type: 'button', value: "Delete"}},
        { nameid: "fsUploadButton", type: "input", notify: true, attr: {type: 'button', value: "Upload"}}
        ]
    },
    { nameid: 'currPathDiv', notify: true},
    { nameid: 'fileDetailsDiv', notify: true},
    {
        nameid: 'fileContentsDiv', style: { width: '100%' },
        kids: [
        {
            nameid: 'fileContentsTable',
            type: 'table', 
            style: { width: '100%' },
            notify: true,
            kids: [
            {
                type: 'tr', 
                kids: [
                {
                    type: 'td',
                    style: {width: '80px'},
                    kids: [ {type: "label", attr: {'for': 'fsFileName'}, kids: ["Name: "]}]
                },{
                    type: 'td', 
                    kids: [{
                        style: { width: '100%' },
                        nameid: 'fsFileName', notify: true, type: "input", attr: {type: 'text'}
                    }]
                }]
            },{ 
                type: 'tr',
                kids: [
                {
                    type: 'td',
                    style: {width: '80px'},
                    kids: [ {type: "label", attr: {'for': 'fsFileType'}, kids: ["Type: "]}]
                },
                {
                    type: 'td', 
                    kids: [{ style: { width: '100%' }, nameid: 'fsFileType', notify: true, type: "select" }]
                }]
            }]
        }]
    }]
};

// 
// Template for display the file list in a tabular fashion
//
var FSFileContents = {
    type: "center",
    kids: [{
        type: "table", notify: true, attr: { border: 2}, style: {width: "90%"},
        kids: [{
            type: "thead",
            kids: [
            { type: "td", style: {'text-align': "center", width: "60%"}, kids: [ "File/Folder" ] },
            { type: "td", style: {'text-align': "center"}, kids: [ "Options" ] },
            { type: "td", style: {'text-align': "center"}, kids: [ "Size" ] },
            { type: "td", style: {'text-align': "center"}, kids: [ "Date Created" ] },
            { type: "td", style: {'text-align': "center"}, kids: [ "Date Modified" ] }
            ]
        }]
    }]
};

//
// A row in the file contents
//
var FSFileContentsRow = {
    type: "tr",
    kids: [
    {
        type: "td",
        kids: [
        function (ctx)
        {
            var delCheck = CreateEl("input",
                                    {attribs: {value: false, type: "checkbox", id: "deleteItem_" + ctx.index}},
                                    ctx);
            AddEventListener(delCheck, "change",
                             function(checkBox, listitem) {
                                return function(ev) { listitem.markedForDelete = checkBox.checked; }
                             }(delCheck, ctx.item));
            return delCheck;
        },
        " ",
        function (ctx)
        {
            var itname  = ctx.item.name;
            var link    = CreateLink(ctx.item.isdir ? "[" + itname + "]" : itname, null, null, ctx);
            var handler = null;
            if (ctx.item.isdir)
            {
                handler = function(ev) { ctx.fsObj._listFolder(ctx.path + "/" + itname); };
            }
            else
            {
                handler = function(ev) { ctx.fsObj._setSelection(itname); };
            }
            AddEventListener(link, "click", handler);
            return link;
        }]
    },
    {
        type: "td",
        kids: [
        function (ctx)
        {
            var link    = CreateLink("R", null, null, ctx);
            AddEventListener(link, "click",
                             function(ev) { ctx.fsObj._renameHandler(ctx.item.name + "/" + ctx.path)} );
            return link;
        }, " ",
        function(ctx)
        {
            if (ctx.item.isdir)
                return null;
            
            return CreateLink("V", "/testzone/wmaker/download/" + ctx.path + "/" + ctx.item.name, null, ctx);
        }]
    },
    {
        type: "td", style: {'text-align': "center"},
        kids: [ function(ctx) { return "" + ctx.item.size; } ],
    },
    {
        type: "td", style: {'text-align': "center"},
        kids: [ function(ctx) { return "" + ctx.item.created; } ],
    },
    {
        type: "td", style: {'text-align': "center"},
        kids: [ function(ctx) { return "" + ctx.item.modified; } ],
    }]
};

// 
// FS Listener interface:
//
function FSListener()
{
    // Called before the path in the FS is changed
    this.FSPathChanging = function(fs) { }

    // Called after the path has chagned
    this.FSPathChanged = function(fs) { }

    // Called to indicate that folder listing has failed
    this.FSListingFailed = function(fs, path) { }
}

// 
// Creates a new file selector and returns a handle to it
//
function FileSelector(parent, fsName, fsListener)
{
    // 
    // Sets a given path
    //
    this.SetPath = function(path)
    {
        return this._listFolder(path);
    }

    // 
    // Return the selected folder
    //
    this.SelectedFolder = function()
    {
        return this.currentFolder;
    }

    // 
    // Return the selected filename
    //
    this.SelectedFile = function()
    {
        return this.fsFileName.value;
    }

    // 
    // Return the full path of the selected item
    //
    this.SelectedPath = function()
    {
        var selFolder   = this.SelectedFolder();
        var selFile     = this.SelectedFile();

        if (selFolder == null)
        {
            if (selFile == null)
                return null;

            selFolder = "";
        }

        if (selFile == null)
            selFile = ""

        return selFolder + selFile;
    }

    /////////////////////////////////////////////////////////////////
    //                      Private Functions
    /////////////////////////////////////////////////////////////////

    //
    // List the contents of a given folder
    //
    this._listFolder = function(path)
    {
        var theFSObj = this;

        // 
        // Process the folder contents received from the server
        //
        function ProcessFolders(request)
        {
            if (request.readyState == 4)
            {
                if (request.status == 200)
                {
                    var list = eval("(" + request.responseText + ")");
                    list = list.success.value;

                    theFSObj._showCurrentPath(path);
                    theFSObj.folderContents             = list;
                    theFSObj.fileDetailsDiv.innerHTML   = "";

                    var theTable = null;

                    // register a call back to see what the "table" is
                    // so we can add rows to it
                    var func = function(node) { theTable = node; }
                    theFSObj.fileDetailsDiv.appendChild(Build(FSFileContents, {nodeCreated: func}));

                    for (var i = 0;i < list.length;i++)
                    {
                        theTable.appendChild(Build(FSFileContentsRow,
                                                   {index: i, path: path, item: list[i], fsObj: theFSObj}));
                    }

                    //
                    // Notify listeners that our path change trial has finished
                    //
                    if (theFSObj.fsListener && theFSObj.fsListener.FSPathChanged)
                    {
                        theFSObj.fsListener.FSPathChanged(theFSObj);
                    }
                }
                else
                {
                    theFSObj.fileDetailsDiv.innerHTML = "Listing failed: " + request.responseText;

                    //
                    // Notify listeners that our path change trial has finished
                    //
                    if (theFSObj.fsListener && theFSObj.fsListener.FSListingFailed)
                    {
                        theFSObj.fsListener.FSListingFailed(theFSObj, path);
                    }
                }
                theFSObj._processResponseText(request.responseText);
            }
        }

        //
        // Notify listeners that path is about to changing
        // No Guarantee that path will change - merely we will try.
        //
        if (this.fsListener && the.fsListener.FSPathChanging)
        {
            this.fsListener.FSPathChanging(this);
        }

        this.fileDetailsDiv.innerHTML = "Waiting for reply from server...";
        return MakeAjaxRequest("GET", "/testzone/list/" + path + "/", ProcessFolders);
    }

    //
    // Initialises the file dialog
    //
    this._initialise = function(par, fsName, fsListener)
    {
        if (par == null)
        {
            var args='width=350,height=125,left=325,top=300,toolbar=0,';
                      args+='location=0,status=0,menubar=0,scrollbars=1,resizable=0';
            var wnd = window.open("", "File Dialog", args);
            var doc = wnd.document;

            doc.open("text/html");
            doc.write("<html>");
            doc.write("<head>");
            doc.write("<script src='/djutils/js/ajax.js'>");
            doc.write("<script src='/djutils/js/fdialog.js'>");
            doc.write("<script src='/djutils/js/dialogs.js'>");
            doc.write("</head>");
            doc.write("<body>");
            doc.write("</body>");
            doc.write("</html>");
            doc.close();

            var timeout = 0;

            // wait till doc.body is finalised!
            // while (doc.body == null) { setTimeout("", 100); }

            par = doc.body;

            //var headEl = CreateEl("head");
            //headEl.appendChild(CreateEl("script", {src: '/djutils/js/common.js'}));
            //headEl.appendChild(CreateEl("script", {src: '/djutils/js/fsialog.js'}));
            //headEl.appendChild(CreateEl("script", {src: '/djutils/js/dialogs.js'}));
            //doc.documentElement.appendChild(headEl);

            var a = 0;
        }

        this.parent = par;

        if (typeof(par) == "string")
        {
            this.parent         = ElementById(par);
        }

        // A unique way to identify the file dialog
        this.fsName         = fsName;
        this.fsID           = fsName;
        this.isShowing      = false;
        this.pathStack      = [];
        this.folderContents = [];
        this.currentFolder  = "/";
        this.fsListener     = fsListener;
        var theFSObj        = this;
        var fs_id           = this.fsID;

        var nodeCreatedFunc   =
            function(node)
            { 
                if (node.id == 'fsUpButton')
                    theFSObj.fsUpButton = node;
                else if (node.id == 'fsHomeButton')
                    theFSObj.fsHomeButton = node;
                else if (node.id == 'fsNewButton')
                    theFSObj.fsNewButton = node;
                else if (node.id == 'fsDeleteButton')
                    theFSObj.fsDeleteButton = node;
                else if (node.id == 'fsUploadButton')
                    theFSObj.fsUploadButton = node;
                else if (node.id == 'fsFileName')
                    theFSObj.fsFileName = node;
                else if (node.id == 'fileDetailsDiv')
                    theFSObj.fileDetailsDiv = node;
                else if (node.id == 'currPathDiv')
                    theFSObj.currPathDiv = node;
                else if (node.id == 'FSDlgContentDiv')
                    theFSObj.dlgContentDiv = node;
                else if (node.id == 'dlgOkButton')
                    theFSObj.dlgOkButton = node;
                else if (node.id == 'dlgCancelButton')
                    theFSObj.dlgCancelButton = node;
                else if (node.id == 'newDirNameField')
                    theFSObj.newDirNameField = node;
                else if (node.id == 'uploadFileField')
                    theFSObj.uploadFileField = node;
                else if (node.id == 'fileUploadForm')
                    theFSObj.fileUploadForm = node;
                else if (node.id == fs_id + 'uploadResultsIFrame')
                    theFSObj.resultsIFrame = node;
            }

        var context         = {nodeCreated: nodeCreatedFunc, fs_id: fs_id}
        this.contentHolder  = Build(FSTemplate, context);
        this.dlgParent      = Build(FSDlgTemplate, context);
        this.newDirDlg      = Build(FSNewDirDlgTemplate, context);
        this.uploadFileDlg  = Build(FSUploadDlgTemplate, context);
        this.renameDlg      = Build(FSRenameDlgTemplate, context);

        this.parent.appendChild(this.contentHolder);
        this.parent.appendChild(this.dlgParent);
        this.dlgContentDiv.appendChild(this.newDirDlg);
        this.dlgContentDiv.appendChild(this.uploadFileDlg);
        this.dlgContentDiv.appendChild(this.renameDlg);

        // Add button handlers
        AddEventListener(this.fsUpButton, "click", function(ev) { theFSObj._upHandler(ev); }, false);
        AddEventListener(this.fsHomeButton, "click", function(ev) { theFSObj._homeHandler(ev); }, false);
        AddEventListener(this.fsNewButton, "click", function(ev) { theFSObj._newHandler(ev); }, false);
        AddEventListener(this.fsDeleteButton, "click", function(ev) { theFSObj._deleteHandler(ev); }, false);
        AddEventListener(this.fsUploadButton, "click", function(ev) { theFSObj._uploadHandler(ev); }, false);

        // Add dlg event listener
        AddEventListener(this.dlgOkButton, "click", function(ev) { theFSObj._dialogClosed(false); });
        AddEventListener(this.dlgCancelButton, "click", function(ev) { theFSObj._dialogClosed(true); });

        this._setSelection("");
    }

    // 
    // Shows the current path in the file dialog
    //
    this._showCurrentPath = function(path)
    {
        var folders = path.split("/");
        var curr    = "/";
        var theThis = this;

        // clear the html
        this.currPathDiv.innerHTML = "";
        this.pathStack = [];

        var node = CreateLink("<home>");
        this.currPathDiv.appendChild(node);
        this.pathStack.push("/");
        AddEventListener(node, "click", function(ev) { PreventEventDefault(ev); theThis._listFolder("/"); });

        for (var i = 0; i < folders.length;i++)
        {
            var currFolder = folders[i].trim();
            if (currFolder.length != 0)
            {
                curr += (currFolder + "/");
                this.pathStack.push(curr);
                this.currPathDiv.appendChild(document.createTextNode("/"));
                node = CreateLink(currFolder);
                this.currPathDiv.appendChild(node);
                var evhandler = function(_path_) { return function(ev) { theThis._listFolder(_path_); } }(curr);
                AddEventListener(node, "click", evhandler);
            }
        }
        
        this._setSelection("");
        this.currentFolder  = curr;
    }

    // 
    // Sets the currently selected file
    //
    this._setSelection = function(path)
    {
        this.fsFileName.value   = path;
    }

    // 
    // Does a file upload 
    //
    this._uploadFile = function()
    {
    }

    // 
    // Cancel handler
    //
    this._cancelHandler = function(ev)
    {
        if (this.fsListener)
        {
            if (this.fsListener.FSHiding && ! this.fsListener.FSHiding(this))
            {
                return ;
            }

            this.Show(false);

            if (this.fsListener.FSHidden)
                this.fsListener.FSHidden(this);
        }
        else
        {
            this.Show(false);
        }
    }

    // Up button handler
    this._upHandler = function(ev)
    {
        if (this.pathStack && this.pathStack.length >= 2)
        {
            var newPath = this.pathStack[this.pathStack.length - 2];
            this._listFolder(newPath);
        }
    }

    // Home button handler
    this._homeHandler = function(ev)
    {
        this._listFolder("/");
    }

    // New button handler
    this._newHandler = function(ev)
    {
        this.dialogName                         = "new";
        this.renameDlg.style.visibility         = "hidden";
        this.renameDlg.style.display            = "none";
        this.uploadFileDlg.style.visibility     = "hidden";
        this.uploadFileDlg.style.display        = "none";
        this.newDirDlg.style.visibility         = "visible";
        this.newDirDlg.style.display            = "block";
        this.dlgParent.style.visibility         = "visible";
    }

    // upload button handler
    this._uploadHandler = function(ev)
    {
        this.dialogName                         = "upload";
        this.renameDlg.style.visibility         = "hidden";
        this.renameDlg.style.display            = "none";
        this.newDirDlg.style.visibility         = "hidden";
        this.newDirDlg.style.display            = "none";
        this.uploadFileDlg.style.visibility     = "visible";
        this.uploadFileDlg.style.display        = "block";
        this.dlgParent.style.visibility         = "visible";
    }

    this._renameHandler = function(path) 
    {
        this.dialogName                         = "rename";
        this.renamePath                         = path;
        this.uploadFileDlg.style.visibility     = "hidden";
        this.uploadFileDlg.style.display        = "none";
        this.newDirDlg.style.visibility         = "hidden";
        this.newDirDlg.style.display            = "none";
        this.renameDlg.style.visibility         = "visible";
        this.renameDlg.style.display            = "block";
        this.dlgParent.style.visibility         = "visible";
    }

    // Dialog button handler
    this._dialogClosed = function(cancelled)
    {
        var theFSObj        = this;
        var refresherData = {fsObj: theFSObj, done: false, refresh: false};

        if ( ! cancelled)
        {
            function ProcessResponse(request)
            {
                if (request.readyState == 4)
                {
                    refresherData.done = true;
                    if (request.status == 200)
                    {
                        var list = eval("(" + request.responseText + ")");

                        if (list.success)
                        {
                            refresherData.refresh = true;
                            //
                            // Notify listeners that our path change trial has finished
                            //
                            if (theFSObj.fsListener && theFSObj.fsListener.FSFolderCreated)
                            {
                                theFSObj.fsListener.FSFolderCreated(theFSObj);
                            }
                        }
                        else
                        {
                            alert(list.failure.message);
                        }
                    }
                    else
                    {
                        alert('Error: ' + request.responseText);
                    }
                    theFSObj._processResponseText(request.responseText);
                }
            }

            if (this.dialogName == "new")
            {
                MakeAjaxRequest("PUT",
                                "/testzone/mkdir" +
                                encodeURI(this.currentFolder) + "/" +
                                encodeURI(this.newDirNameField.value.trim()) +
                                "/?recurse=true",
                                ProcessResponse);
            }
            else if (this.dialogName == "upload")
            {
                this.fileUploadForm.action = "/testzone/wmaker/upload" +
                                             this.currentFolder + "?fieldName=uploadFileField";
                this.fileUploadForm.submit();
            }
            else if (this.dialogName == "rename")
            {
                refresherData.done = true;
            }
            else
            {
                refresherData.done = true;
            }

            // now wait for the request to be processed
            function refresher(data)
            {
                function intervalFunc()
                {
                    if (data.done)
                    {
                        if (data.refresh)
                        {
                            data.fsObj._listFolder(data.fsObj.currentFolder);
                            clearInterval(data.timerid);
                        }
                    }
                }

                data.timerid = setInterval(intervalFunc, 1000);
            }

            refresher(refresherData);
        }

        this.renameDlg.style.visibility         = "hidden";
        this.renameDlg.style.display            = "none";
        this.uploadFileDlg.style.visibility     = "hidden";
        this.uploadFileDlg.style.display        = "none";
        this.newDirDlg.style.visibility         = "hidden";
        this.newDirDlg.style.display            = "none";
        this.dlgParent.style.visibility         = "hidden";
        // setTimeout("this._listFolder(this.currentFolder);", 2000);
    }

    // for debug mode printing of server responses to api calls
    this._processResponseText = function(text)
    {
        /*
        if (this.respWindow == null)
        {
            var args='width=950,height=725,left=50,top=50,toolbar=0,';
                args+='location=0,status=0,menubar=0,scrollbars=1,resizable=0';
            this.respWindow = window.open("", "Server Response", args);
        }
        var doc = this.respWindow.document;
        doc.write("<p>" +  text + "</p>");
        */
    }

    // Delete button handler
    this._deleteHandler = function(ev)
    {
        var files = "[";
        var count = 0;
        for (var i in this.folderContents)
        {
            if (this.folderContents[i].markedForDelete)
            {
                if (files.length > 1)
                    files += ", ";
                files += "'" + escape(this.folderContents[i].name) + "'\n";
                count++;
            }
        }
        files += "]";

        if (count == 0)
        {
            alert('You have not marked any files for deletion.');
            return ;
        }

        var fileList = "fileList=" + files;

        var theFSObj = this;

        function ProcessResponse(request)
        {
            if (request.readyState == 4)
            {
                if (request.status == 200)
                {
                    theFSObj._listFolder(theFSObj.currentFolder);
                }
                else
                {
                    alert('Could not delete folders.');

                    theFSObj._listFolder(this.currentFolder);
                }

                theFSObj._processResponseText(request.responseText);
            }
        }

        var httpRequest = GetHttpRequest();

        httpRequest.onreadystatechange = function() { ProcessResponse(httpRequest); }

        // just some URL cleanup
        if (this.currentFolder == "" || this.currentFolder == "/")
        {
            httpRequest.open('DELETE', "/testzone/delete/?recurse=true");
        }
        else
        {
            httpRequest.open('DELETE', "/testzone/delete/" + this.currentFolder + "/?recurse=true");
        }

        httpRequest.setRequestHeader("Content-type", "text/text");
        httpRequest.setRequestHeader("Content-length", fileList.length);
        httpRequest.setRequestHeader("Connection", "close");
        httpRequest.send(fileList);
    }

    this._initialise(parent, fsName);
}

