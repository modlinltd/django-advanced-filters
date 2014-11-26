import logging
import re

from django import forms

from easy_select2.widgets import Select2TextInput

logger = logging.getLogger('advanced_filters.form_helpers')

extra_spaces_pattern = re.compile('\s+')


class VaryingTypeCharField(forms.CharField):
    def to_python(self, value):
        res = super(VaryingTypeCharField, self).to_python(value)
        split_res = res.split(",")
        if not res or len(split_res) < 2:
            return res.strip()
        # create a regex string out of the list of choices passed, i.e: (a|b)
        res = r"({})".format("|".join(map(lambda x: x.strip(), split_res)))
        return res


class CleanWhiteSpacesMixin(object):
    def clean(self):
        """ Strip char fields """
        cleaned_data = super(CleanWhiteSpacesMixin, self).clean()
        for k in self.cleaned_data:
            if isinstance(self.cleaned_data[k], basestring):
                cleaned_data[k] = re.sub(extra_spaces_pattern, ' ',
                                         self.cleaned_data[k] or '').strip()
        return cleaned_data


def get_select2textinput_widget(choices=None):
    """
    Accepts django-style choices (tuple of tuples), prepares
    and returns an instance of a Select2TextInput widget.

    For more info on this custom widget, see doc here:
    http://django-easy-select2.readthedocs.org/en/latest/index.html
    """
    attributes = {
        # select2 script takes data in json values such as:
        # 'data': [ {'id': 'value', 'text': 'description'}, ... ],
    }
    if choices:
        attributes['data'] = [{'id': c[0], 'text': unicode(c[1])}
                              for c in choices]
    return Select2TextInput(select2attrs=attributes)
