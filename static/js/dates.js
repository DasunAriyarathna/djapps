
function difference_in_days(date1, date2)
{
    var ONE_DAY = 1000 * 60 * 60 * 24;
    var date1_ms = date1.getTime();
    var date2_ms = date2.getTime();
    var diff_ms = Math.abs(date1_ms - date2_ms);
    return Math.round(difference_ms/ONE_DAY);
}

function date_cmp(date1, date2)
{
    var date1_ms = date1.getTime();
    var date2_ms = date2.getTime();
    return date1_ms - date2_ms;
}

