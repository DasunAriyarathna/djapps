
// 
// Associate a new keyword with a given item
//
function AddKeyword(nodeid, kw)
{
    kw = kw.trim();

    if (kw.length == 0)
        return false;

    // alert("nodeid, Keyword: " + nodeid + ", " + escape(kw));
    document.location = "/factcheck/link/" + nodeid + "/?concept=" + escape(kw);
}

