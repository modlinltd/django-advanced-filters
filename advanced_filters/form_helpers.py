import logging
import re

from django import forms

from django.utils import six
from easy_select2.widgets import Select2TextInput

logger = logging.getLogger('advanced_filters.form_helpers')

extra_spaces_pattern = re.compile('\s+')


class VaryingTypeCharField(forms.CharField):
    """
    This CharField subclass returns a regex OR patterns from a
    comma separated list value.
    """
    _default_separator = ","

    def to_python(self, value):
        """
        Split a string value by separator (default to ",") into a
        list; then, returns a regex pattern string that ORs the values
        in the resulting list.

        >>> field = VaryingTypeCharField()
        >>> assert field.to_python('') == ''
        >>> assert field.to_python('test') == 'test'
        >>> assert field.to_python('and,me') == '(and|me)'
        >>> assert field.to_python('and,me;too') == '(and|me;too)'
        """
        res = super(VaryingTypeCharField, self).to_python(value)
        split_res = res.split(self._default_separator)
        if not res or len(split_res) < 2:
            return res.strip()

        # create a regex string out of the list of choices passed, i.e: (a|b)
        res = r"({pattern})".format(pattern="|".join(
            map(lambda x: x.strip(), split_res)))
        return res


class CleanWhiteSpacesMixin(object):
    """
    This mixin, when added to any form subclass, adds a clean method which
    strips repeating spaces in and around each string value of "clean_data".
    """
    def clean(self):
        """
        >>> import django.forms
        >>> class MyForm(CleanWhiteSpacesMixin, django.forms.Form):
        ...     some_field = django.forms.CharField()
        >>>
        >>> form = MyForm({'some_field': ' a   weird value  '})
        >>> assert form.is_valid()
        >>> assert form.cleaned_data == {'some_field': 'a weird value'}
        """
        cleaned_data = super(CleanWhiteSpacesMixin, self).clean()
        for k in self.cleaned_data:
            if isinstance(self.cleaned_data[k], six.string_types):
                cleaned_data[k] = re.sub(extra_spaces_pattern, ' ',
                                         self.cleaned_data[k] or '').strip()
        return cleaned_data


def get_select2textinput_widget(choices=None):
    """
    Accepts django-style choices (tuple of tuples), prepares
    and returns an instance of a Select2TextInput widget.

    For more info on this custom widget, see doc here:
    http://django-easy-select2.readthedocs.org/en/latest/index.html

    >>> from django.utils.translation import ugettext_lazy as _
    >>> widget = get_select2textinput_widget()
    >>> args, kwargs = ('test_field', None,), dict(attrs=dict(id='id_test_field'))
    >>> widget = get_select2textinput_widget([
    ...     (1, 'first option'),
    ...     (2, _('test me')),
    ... ])
    >>> data = {'data': [{'id': 1, 'text': 'first option'},
    ...                  {'id': 2, 'text': 'test me'}],
    ...         'width': '250px'}
    >>> assert widget.select2attrs == data
    """
    attributes = {
        # select2 script takes data in json values such as:
        # 'data': [ {'id': 'value', 'text': 'description'}, ... ],
    }
    if choices:
        attributes['data'] = [{'id': c[0], 'text': six.text_type(c[1])}
                              for c in choices]
    return Select2TextInput(select2attrs=attributes)
