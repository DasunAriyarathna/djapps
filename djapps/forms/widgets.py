"""
Extra HTML Widget classes
"""

import time, itertools, datetime, re

from django.forms.widgets import Widget, Select
from django.utils import datetime_safe
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.formats import get_format
from django.conf import settings

__all__ = ('SelectDateTimeWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?) (\d\d?):(\d\d?):(\d\d?)$')

class SelectDateTimeWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    none_value = (0, '---')
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'
    hour_field = '%s_hour'
    minute_field = '%s_minute'
    second_field = '%s_second'

    date_field = '%s'
    time_field = '%s'

    def __init__(self,
                 attrs=None, years=None, required=True,
                 show_hours = True, show_minutes = True, show_seconds = True, **kwargs):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs          = attrs or {}
        self.required       = required
        self.show_hours     = show_hours
        self.show_minutes   = show_minutes
        self.show_seconds   = show_seconds
        self.months         = kwargs.get("month_dict", MONTHS)
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val        = value.year, value.month, value.day
            hour_val, minute_val, second_val    = value.hour, value.minute, value.second
        except AttributeError:
            year_val = month_val = day_val  = None
            hour_val = minute_val = second_val = None
            if isinstance(value, basestring):
                if settings.USE_L10N:
                    try:
                        input_format = get_format('DATE_INPUT_FORMATS')[0]
                        # Python 2.4 compatibility:
                        #     v = datetime.datetime.strptime(value, input_format)
                        # would be clearer, but datetime.strptime was added in 
                        # Python 2.5
                        v = datetime.datetime(*(time.strptime(value, input_format)[0:6]))
                        year_val, month_val, day_val        = v.year, v.month, v.day
                        hour_val, minute_val, second_val    = v.hour, v.minute, v.second
                    except ValueError:
                        pass
                else:
                    match = RE_DATE.match(value)
                    if match:
                        match_groups = match.groups()
                        year_val, month_val, day_val, hour_val, minute_val, second_val = [int(v) for v in match_groups]

        if not value:
            # set to current time if value is not given
            value = right_now = datetime.datetime.now()
            year_val, month_val, day_val        = value.year, value.month, value.day
            hour_val, minute_val, second_val    = value.hour, value.minute, value.second

        # now the actual render
        format = get_format('DATE_INPUT_FORMATS')[0] ; print "Date Format: ", format
        date_html = self.render_date(name, year_val, month_val, day_val, format)
        time_html = self.render_time(name, hour_val, minute_val, second_val, format)
        return mark_safe(date_html + time_html)

    def render_date(self, name, year_val, month_val, day_val, format):
        """
        Renders the date part of the field.
        """
        choices = [(i, i) for i in self.years]
        year_html = self.create_select(name, self.year_field, year_val, choices)
        choices = self.months.items()
        month_html = self.create_select(name, self.month_field, month_val, choices)
        choices = [(i, "%02d" % i) for i in range(0, 32)]
        day_html = self.create_select(name, self.day_field, day_val,  choices)

        escaped = False
        output = ""
        for char in format:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char in 'Yy':
                output += year_html
            elif char in 'bFMmNn':
                output += month_html
            elif char in 'dj':
                output += day_html
        return output

    def render_time(self, name, hour_val, minute_val, second_val, format):
        """
        Renders the time part of the field.
        """
        choices = [(i, "%02d" % i) for i in range(0, 24)]
        hour_html = self.create_select(name, self.hour_field, hour_val, choices)
        choices = [(i, "%02d" % i) for i in range(0, 60)]
        minute_html = self.create_select(name, self.minute_field, minute_val, choices)
        second_html = self.create_select(name, self.second_field, second_val, choices)

        # now append time if necessary
        output = ""
        if self.show_hours or self.show_minutes or self.show_seconds:
            output += "<br/>"
            if self.show_hours:
                output += hour_html
            if self.show_minutes:
                output += minute_html
            if self.show_seconds:
                output += second_html
        return output

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y,m,d = self.parse_date_from_datadict(data, files, name)
        hr,min,sec = self.parse_time_from_datadict(data, files, name)
        if y == m == d == "0":
            return None
        if y and m and d:
            if settings.USE_L10N:
                input_format = get_format('DATE_INPUT_FORMATS')[0]
                try:
                    date_value = datetime.datetime(int(y), int(m), int(d), int(hr), int(min), int(sec))
                except ValueError, ve:
                    print "Value Error: ", ve
                    pass
                else:
                    date_value = datetime_safe.new_date(date_value)
                    return date_value.strftime(input_format)
            else:
                return '%s-%s-%s %s:%s:%s' % (y, m, d, hr, min, sec)
        return data.get(name, None)

    def parse_date_from_datadict(self, data, files, name):
        """
        This parses the actual date from the data dictionary.
        """
        # if the date field does not have it then check for the individual
        # year, month, day fields for values

        # first check if the date_field has the date in it:
        date = data.get(self.date_field % name)
        if date and type(date) != datetime.datetime:
            input_formats = itertools.chain(get_format('DATE_INPUT_FORMATS'), get_format('DATETIME_INPUT_FORMATS'))
            for input_format in input_formats:
                # try all formats
                try:
                    date = datetime.datetime.strptime(date, input_format)
                    y,m,d = date.year, date.month, date.day
                    break
                except ValueError, ve:
                    pass
        y = data.get(self.year_field % name, y)
        m = data.get(self.month_field % name, m)
        d = data.get(self.day_field % name, d)
        return y,m,d

    def parse_time_from_datadict(self, data, files, name):
        """
        This parses the actual time from the data dictionary.
        """
        # see if the time_field overrides the hr/min/sec fields
        hr = min = sec = 0
        date = data.get(self.time_field % name)
        if date and type(date) != datetime.datetime:
            for input_format in get_format('DATETIME_INPUT_FORMATS'):
                # try all formats
                try:
                    date = datetime.datetime.strptime(date, input_format)
                    hr,min,sec = date.hour, date.minute, date.second
                    break
                except ValueError, ve:
                    pass
        hr = data.get(self.hour_field % name, hr)
        min = data.get(self.minute_field % name, min)
        sec = data.get(self.second_field % name, sec)
        return hr,min,sec

    def create_select(self, name, field, val, choices):
        """
        Creates a "select" field with a given name, populated list of
        choices and a chosen value.
        """
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        if not (self.required and val):
            choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=field % id_)
        s = Select(choices=choices)
        select_html = s.render(field % name, val, local_attrs)
        return select_html

