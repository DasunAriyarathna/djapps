"""
Extra HTML Widget classes
"""

import time
import datetime
import re

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
        choices = [(i, i) for i in self.years]
        if not value:
            # set to current time if value is not given
            value = right_now = datetime.datetime.utcnow()
            year_val, month_val, day_val        = value.year, value.month, value.day
            hour_val, minute_val, second_val    = value.hour, value.minute, value.second

        year_html = self.create_select(name, self.year_field, value, year_val, choices)
        choices = self.months.items()
        month_html = self.create_select(name, self.month_field, value, month_val, choices)
        choices = [(i, "%02d" % i) for i in range(0, 32)]
        day_html = self.create_select(name, self.day_field, value, day_val,  choices)
        choices = [(i, "%02d" % i) for i in range(0, 24)]
        hour_html = self.create_select(name, self.hour_field, value, hour_val, choices)
        choices = [(i, "%02d" % i) for i in range(0, 60)]
        minute_html = self.create_select(name, self.minute_field, value, minute_val, choices)
        second_html = self.create_select(name, self.second_field, value, second_val, choices)

        format = get_format('DATE_FORMAT')
        print "Date Format: ", format
        escaped = False
        output = []
        for char in format:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char in 'Yy':
                output.append(year_html)
            elif char in 'bFMmNn':
                output.append(month_html)
            elif char in 'dj':
                output.append(day_html)
        # now append time if necessary
        if self.show_hours or self.show_minutes or self.show_seconds:
            output.append("<br/>")
            if self.show_hours:
                output.append(hour_html)
            if self.show_minutes:
                output.append(minute_html)
            if self.show_seconds:
                output.append(second_html)
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        hr = data.get(self.hour_field % name, "0")
        min = data.get(self.minute_field % name, "0")
        sec = data.get(self.second_field % name, "0")
        if y == m == d == "0":
            return None
        if y and m and d:
            if settings.USE_L10N:
                input_format = get_format('DATE_INPUT_FORMATS')[0]
                try:
                    date_value = datetime.datetime(int(y), int(m), int(d), int(hr), int(min), int(sec))
                except ValueError:
                    pass
                else:
                    date_value = datetime_safe.new_date(date_value)
                    return date_value.strftime(input_format)
            else:
                return '%s-%s-%s %s:%s:%s' % (y, m, d, hr, min, sec)
        return data.get(name, None)

    def create_select(self, name, field, value, val, choices):
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

