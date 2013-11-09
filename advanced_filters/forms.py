from functools import reduce
from pprint import pformat
import logging
import operator

from django import forms
from django.contrib.admin.util import get_fields_from_path
from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from .models import AdvancedFilter


logger = logging.getLogger('advanced_filters')


class VaryingTypeCharField(forms.CharField):
    def to_python(self, value):
        res = super(VaryingTypeCharField, self).to_python(value)
        split_res = res.split(",")
        if not res or len(split_res) < 2:
            return res
        # create a regex string out of the list of choices passed, i.e: (a|b)
        res = r"({})".format("|".join(map(lambda x: x.strip(), split_res)))
        return res


class AdvancedFilterQueryForm(forms.Form):
    """ Build the query from field, operator and value """
    model_name = None

    OPERATORS = (
        ("iexact", _("Equals")),
        ("icontains", _("Contains")),
        ("iregex", _("One of")),
        ("range", _("DateTime Range")),
    )

    FIELD_CHOICES = (
        ("_OR", _("Or (mark an or between blocks)")),
    )

    field = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'query-field'}))
    operator = forms.ChoiceField(required=True, choices=OPERATORS,
                                 initial="iexact", widget=forms.Select(
                                 attrs={'class': 'query-operator'}))
    value = VaryingTypeCharField(required=True, widget=forms.TextInput(
        attrs={'class': 'query-value'}))
    value_from = forms.DateTimeField(widget=forms.HiddenInput(
        attrs={'class': 'query-dt-from'}), required=False)
    value_to = forms.DateTimeField(widget=forms.HiddenInput(
        attrs={'class': 'query-dt-to'}), required=False)
    negate = forms.BooleanField(initial=False, required=False)

    def _build_field_choices(self, fields):
        """
        Iterate over passed model fields tuple and update initial choices
        """
        return tuple(
            [(fquery, capfirst(f.verbose_name))
                for fquery, f in fields.items()]
        ) + self.FIELD_CHOICES

    def set_range_value(self, data):
        """
        Validates date range by parsing into 2 datetime objects and
        validating them both.
        """
        dtfrom = data.pop('value_from')
        dtto = data.pop('value_to')
        data['value'] = (dtfrom, dtto)

    def _build_query_dict(self, formdata):
        """
        Take submitted data from form and create a query dict to be
        used in a Q object (or filter)
        """
        key = "{}__{}".format(formdata['field'], formdata['operator'])
        return {key: formdata['value']}

    def clean(self):
        if self.cleaned_data['operator'] == "range":
            if ('value_from' in self.cleaned_data
                    and 'value_to' in self.cleaned_data):
                self.set_range_value(self.cleaned_data)
        return self.cleaned_data

    def make_query(self, *args, **kwargs):
        """ Returns a Q object from the submitted form """
        query = Q()  # initial is an empty query
        query_dict = self._build_query_dict(self.cleaned_data)
        if 'negate' in self.cleaned_data and self.cleaned_data['negate']:
            query = query & ~Q(**query_dict)
        else:
            query = query & Q(**query_dict)
        return query

    def __init__(self, model_fields, *args, **kwargs):
        super(AdvancedFilterQueryForm, self).__init__(*args, **kwargs)
        self.FIELD_CHOICES = self._build_field_choices(model_fields)
        self.fields['field'].choices = self.FIELD_CHOICES
        self.fields['field'].initial = self.FIELD_CHOICES[0]


class AdvancedFilterFormSet(BaseFormSet):
    """ """
    fields = ()
    extra_kwargs = {}

    def __init__(self, extra_kwargs={}, *args, **kwargs):
        self.extra_kwargs = extra_kwargs
        super(AdvancedFilterFormSet, self).__init__(*args, **kwargs)
        if self.forms:
            form = self.forms[0]
            self.fields = form.visible_fields()

    @property
    def empty_form(self):
        model_fields = self.extra_kwargs.get('model_fields', {})
        form = self.form(
            model_fields=model_fields,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,
        )
        self.add_fields(form, None)
        return form

    def _construct_forms(self):
        """Allow passing of additional kwargs to form instance upon init"""
        self.forms = []
        for i in range(min(self.total_form_count(), self.absolute_max)):
            self.forms.append(self._construct_form(i, **self.extra_kwargs))
        self.forms.append(self.empty_form)

AFQFormSet = formset_factory(
    AdvancedFilterQueryForm, formset=AdvancedFilterFormSet,
    extra=1, can_delete=True)


class AdvancedFilterForm(forms.ModelForm):
    """ Form to save/edit advanced filter forms (currently just adds) """
    class Meta:
        model = AdvancedFilter
        fields = ('title',)

    model_admin = None

    def __init__(self, model_admin, *args, **kwargs):
        fields = getattr(model_admin, 'advanced_filter_fields', ())
        model = model_admin.model
        # validate fields and pass model fields to query formset
        model_fields = {}
        for field in fields:
            try:
                model_fields[field] = get_fields_from_path(model, field)[-1]
            except FieldDoesNotExist as e:
                logger.warn("AdvancedFilterForm: skipping invalid field %s", e)
                continue

        self.fields_formset = AFQFormSet(
            data=kwargs.get('data'),
            extra_kwargs={'model_fields': model_fields}
        )
        return super(AdvancedFilterForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.fields_formset.is_valid():
            logger.debug("Errors validating advanced query filters: %s",
                         pformat([(f.errors, f.non_field_errors())
                                  for f in self.fields_formset.forms]))
            raise forms.ValidationError("Error validating filter forms")
        return self.cleaned_data

    def generate_query(self, *args, **kwargs):
        """ Reduces multiple queries into a single usable query """
        query = Q()
        ORed = []
        for form in self.fields_formset.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data['field'] == "_OR":
                ORed.append(query)
                query = Q()
            else:
                query = query & form.make_query()
        if ORed:
            if query:  # add last query for OR if any
                ORed.append(query)
            query = reduce(operator.or_, ORed)
        return query
