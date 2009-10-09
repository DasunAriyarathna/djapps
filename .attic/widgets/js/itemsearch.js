
//
// This is a simple widget for displaying a "search/add item" widget into a
// page.  So that people can use this to quickly add search results to a
// page.
//

// 
//
function CreateSearchWidget(formName, formAction, hiddenFields,
                            stmtFieldName, searchBtnName, searchBtnLabel, searchBtnHandler,
                            addBtnName, addBtnLabel, addBtnHandler)
{
    document.write("<form name = " + formName + " method = POST ");
    if (formAction != null)
    {
        document.write(" action = '" + formAction + "'");
    }
    document.writeln(">");

    if (hiddenFields)
    {
        for (field in hiddenFields)
        {
            // alert("<input type = 'hidden' name = '" + field + "' value = '" + hiddenFields[field] + "'/>");
            document.writeln("<input type = 'hidden' name = '" + field + "' value = '" + hiddenFields[field] + "'/>");
        }
    }

    if (stmtFieldName != null)
    {
        document.writeln("<input type = text style='width: 100%' name = '" + stmtFieldName + "'" +
                          "onkeypress ='if (keycode(event) == 13) { ");
        if (searchBtnHandler && searchBtnHandler != "") 
        {
            document.writeln(searchBtnHandler + "(this.form); ");
        }
        document.writeln(" return false; }'/>");
        document.writeln("<br>");
    }
    document.write("<center>");
    if (searchBtnName != null)
    {
        document.write("<input type=button name = '" + searchBtnName + "' value = '" + searchBtnLabel + "' ");
        if (searchBtnHandler != null && searchBtnHandler != "")
        {
            document.write("onClick='" + searchBtnHandler + "(this.form);'");
        }
        document.writeln("/>");
    }
    if (addBtnName != null)
    {
        document.write("<input type=submit name = '" + addBtnName + "' value = '" + addBtnLabel + "' ");
        if (addBtnHandler != null && addBtnHandler != "")
        {
            document.write("onClick='" + addBtnHandler + "(this.form);'");
        }
        document.writeln("/>");
    }
    document.write("</center>");
    document.writeln("</form>");
}
