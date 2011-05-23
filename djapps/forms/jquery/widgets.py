"""
jQuery based widgets
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
from .. import widgets

__all__ = ('JQDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?) (\d\d?):(\d\d?):(\d\d?)$')

class JQDateTimeWidget(widgets.SelectDateTimeWidget):
    date_field = '%s'
    def render_date(self, name, year_val, month_val, day_val, format):
        """
        Overridden to render date as a JQ date plugin.
        """
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        field_id = self.date_field % id_

        date_format = ""
        date_value = ""
        escaped = False
        for char in format:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char in 'Yy':
                if date_format: date_format += "-"
                if date_value: date_value += "-"
                date_format += "yy"
                date_value += "%04d" % year_val
            elif char in 'bFMmNn':
                if date_format: date_format += "-"
                if date_value: date_value += "-"
                date_format += "mm"
                date_value += "%02d" % month_val
            elif char in 'dj':
                if date_format: date_format += "-"
                if date_value: date_value += "-"
                date_format += "dd"
                date_value += "%02d" % day_val

        # TODO - replace this with a "template" instead of hardcoding html here
        return """
            <input type='text' name='%(name)s' id = '%(id)s' value='%(value)s'/>
            <script type=text/javascript>
                $(document).ready(function() {
                    $('#%(id)s').datepicker({dateFormat: '%(format)s'});
                });
            </script>
            """ % {'name': name, 'id': field_id, 'format': date_format, 'value': date_value}

    def parse_date_from_datadict(self, data, files, name):
        """
        This parses the actual date from the data dictionary.
        """
        print "Date_field, Date: ", self.date_field, data.get(self.date_field % name)
        input_format = get_format('DATE_INPUT_FORMATS')[0]
        date_str = data.get(self.date_field % name)
        date = datetime.datetime.strptime(date_str, input_format)
        return date.year, date.month, date.day
