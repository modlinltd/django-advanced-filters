from ..form_helpers import CleanWhiteSpacesMixin

import django.forms


class FormToTest(CleanWhiteSpacesMixin, django.forms.Form):
    some_field = django.forms.CharField()


def test_spaces_removed():
    form = FormToTest(data={'some_field': ' a   weird value  '})
    assert form.is_valid()
    assert form.cleaned_data == {'some_field': 'a weird value'}

    form = FormToTest(data={'some_field': ' \n\r \n  '})
    assert not form.is_valid()
    assert form.cleaned_data == {}
