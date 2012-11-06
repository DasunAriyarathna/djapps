"""
Custom HTML Widget classes
"""
from django.utils import datetime_safe, formats
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.forms.util import flat_att
import time
import datetime

class DateTimeWidget(Widget):
    is_hidden = True
    needs_multipart_form = False # Determines does this widget need multipart-encrypted form
    format = '%Y-%m-%d %H:%M:%S'     # '2006-10-25 14:30:59'

    def __init__(self, attrs=None, format=None):
        super(DateTimeWidget, self).__init__(attrs)
        if format:
            self.format         = format
            self.manual_format  = True
        else:
            self.format         = formats.get_format('DATETIME_INPUT_FORMATS')[0]
            self.manual_format = False

    def _format_value(self, value):
        if self.is_localized and not self.manual_format:
            return formats.localize_input(value)
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_datetime(value)
            return value.strftime(self.format)
        return value

    def _has_changed(self, initial, data):
        # If our field has show_hidden_initial=True, initial will be a string
        # formatted by HiddenInput using formats.localize_input, which is not
        # necessarily the format used for this widget. Attempt to convert it.
        try:
            input_format = formats.get_format('DATETIME_INPUT_FORMATS')[0]
            initial = datetime.datetime(*time.strptime(initial, input_format)[:6])
        except (TypeError, ValueError):
            pass
        return super(DateTimeWidget, self)._has_changed(self._format_value(initial), data)

    def render(self, name, value, attrs=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.

        The 'value' given is not guaranteed to be valid input, so subclass
        implementations should program defensively.
        """
        return mark_safe(u'<div%s>%s</div>' % (flatatt(final_attrs), conditional_escape(force_unicode(value))))

    def build_attrs(self, extra_attrs=None, **kwargs):
        "Helper function for building an attribute dictionary."
        attrs = dict(self.attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        return data.get(name, None)

    def id_for_label(self, id_):
        """
        Returns the HTML ID attribute of this Widget for use by a <label>,
        given the ID of the field. Returns None if no ID is available.

        This hook is necessary because some widgets have multiple HTML
        elements and, thus, multiple IDs. In that case, this method should
        return an ID value that corresponds to the first ID in the widget's
        tags.
        """
        return id_
    id_for_label = classmethod(id_for_label)

