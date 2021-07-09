from datetime import datetime
import time

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase
import django

import pytest

from ..models import AdvancedFilter
from ..forms import AdvancedFilterQueryForm, AdvancedFilterForm


class TestQueryForm(TestCase):
    data = dict(field='fname', value='john', operator='iexact')
    fields = dict(bday='birthday', fname='first name')

    def test_valid_field_choices(self):
        form = AdvancedFilterQueryForm({}, data=self.data)
        assert not form.is_valid()
        assert 'field' in form.errors
        err_msg = form.errors['field'][0]
        assert 'fname is not one of the available choices.' in err_msg

        form = AdvancedFilterQueryForm(self.fields, data=self.data)
        assert form.is_valid()

    def test_range_value(self):
        data = dict(field='bday', value='-', operator='range',
                    value_from=None, value_to=None)
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert not form.is_valid()
        assert 'value' in form.errors
        err_msg = form.errors['value'][0]
        assert 'Date range requires values' in err_msg

        data.update(dict(value_from='1980-01-01', value_to='1990-01-01'))
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form.is_valid(), 'errors: %s' % form.errors
        drange = form.cleaned_data['value']
        assert isinstance(drange, tuple)
        d1, d2 = drange
        assert d1.replace(tzinfo=None) == datetime(1980, 1, 1)
        assert d2.replace(tzinfo=None) == datetime(1990, 1, 1)

    def test_range_value_one_missing(self):
        """ Test, that range filter works even if one range is missing """
        Rep = get_user_model()
        field = {
            'value_to': 504921600.0,
            'negate': False,
            'value_from': None,
            'field': 'date_joined',
            'value': [None, 504921600.0],
            'operator': 'range',
        }
        res = AdvancedFilterQueryForm._parse_query_dict(field, Rep)
        assert res['value'] == ',1986-01-01'

    def test_build_field_choices(self):
        form = AdvancedFilterQueryForm(self.fields)
        assert 'field' in form.fields
        fchoices = dict(form.fields['field'].choices)
        assert '_OR' in fchoices
        fchoices.pop('_OR').encode() == 'Or'
        assert fchoices == {
            'bday': 'Birthday',
            'fname': 'First name'
        }

    def test_build_query_dict(self):
        data = self.data.copy()
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form._build_query_dict() == {'fname__iexact': 'john'}

        data['operator'] = 'isnull'
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form._build_query_dict() == {'fname__isnull': None}

        data['operator'] = 'istrue'
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form._build_query_dict() == {'fname': True}

        data['operator'] = 'isfalse'
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form._build_query_dict() == {'fname': False}

    def test_make_query(self):
        form = AdvancedFilterQueryForm(self.fields, data=self.data)
        assert form.is_valid()
        q = form.make_query()
        assert isinstance(q, Q)
        assert isinstance(q.children, list)
        assert q.children[0] == ('fname__iexact', 'john')
        assert q.connector == 'AND'
        assert not q.negated

        data = self.data.copy()
        data['negate'] = True  # fname is exactly not john
        form = AdvancedFilterQueryForm(self.fields, data=data)
        assert form.is_valid()
        q = form.make_query()
        assert isinstance(q, Q)
        assert isinstance(q.children, list)
        assert q.connector == 'AND'
        if django.VERSION >= (2, 0):
            # django 2+ flattens nested empty Query
            assert q.negated
            assert q.children[0] == ('fname__iexact', 'john')
        else:
            # django <2 has a parent Query that stays default
            assert not q.negated
            subquery = q.children[0]
            assert isinstance(subquery, Q)
            assert subquery.negated
            assert subquery.children[0] == ('fname__iexact', 'john')

    def test_invalid_existing_query(self):
        Rep = get_user_model()
        bad_query = Q(foo='baz')
        af = AdvancedFilter(query=bad_query)
        with pytest.raises(FieldDoesNotExist) as excinfo:
            AdvancedFilterQueryForm._parse_query_dict(af.list_fields()[0], Rep)
        assert "SalesRep has no field named " in str(excinfo.value)
        assert "'foo'" in str(excinfo.value)

        Rep = get_user_model()
        bad_query = Q(groups__test='baz')
        af = AdvancedFilter(query=bad_query)
        with pytest.raises(FieldDoesNotExist) as excinfo:
            AdvancedFilterQueryForm._parse_query_dict(af.list_fields()[0], Rep)
        assert "Group has no field named" in str(excinfo.value)
        assert "'test'" in str(excinfo.value)

    def test_restore_stored_complex_query(self):
        Rep = get_user_model()
        date_range = (datetime(1980, 1, 1), datetime(1986, 1, 1))
        complex_query = (Q(groups__name='bar') |
                         (Q(first_name__iexact='fez') & ~Q(is_staff=False)) |
                         (Q(date_joined__range=date_range) &
                          Q(is_superuser=True) & ~Q(is_active=None)))
        af = AdvancedFilter(query=complex_query)

        expected = [
            {'field': 'groups__name', 'negate': False, 'operator': 'iexact', 'value': 'bar'},
            {'field': '_OR', 'operator': 'iexact', 'value': 'null'},
            {'field': 'first_name', 'negate': False, 'operator': 'iexact', 'value': 'fez'},
            {'field': 'is_staff', 'negate': True, 'operator': 'isfalse', 'value': False},
            {'field': '_OR', 'operator': 'iexact', 'value': 'null'},
            {'field': 'date_joined',
             'negate': False,
             'operator': 'range',
             'value': '1980-01-01,1986-01-01',
             'value_from': time.mktime(date_range[0].timetuple()),
             'value_to': time.mktime(date_range[1].timetuple())},
            {'field': 'is_superuser', 'negate': False, 'operator': 'istrue', 'value': True},
            {'field': 'is_active', 'negate': True, 'operator': 'isnull', 'value': None},
        ]
        for i, field in enumerate(af.list_fields()):
            res = AdvancedFilterQueryForm._parse_query_dict(field, Rep)
            assert isinstance(res, dict)
            assert res == expected[i]

    def test_all_operators_are_restored(self):
        Rep = get_user_model()
        date_range = (datetime(1980, 1, 1), datetime(1986, 1, 1))
        complex_query = (Q(first_name='bar') |
                         (Q(first_name__iexact='fez') &
                          Q(is_staff=False) &
                          Q(date_joined__range=date_range) &
                          Q(is_superuser=True) &
                          Q(is_active=None) &
                          Q(is_staff=False) &
                          Q(last_name__icontains='foo') &
                          Q(last_name__lt='q') &
                          Q(last_name__lte='r') &
                          Q(last_name__gt='b') &
                          Q(last_name__gte='c') &
                          Q(email__iregex=r'^(foo|bar)$')
                          ))
        af = AdvancedFilter(query=complex_query)

        expected = [
            {'field': 'first_name', 'negate': False, 'operator': 'iexact', 'value': 'bar'},
            {'field': '_OR', 'operator': 'iexact', 'value': 'null'},
            {'field': 'first_name', 'negate': False, 'operator': 'iexact', 'value': 'fez'},
            {'field': 'is_staff', 'negate': False, 'operator': 'isfalse', 'value': False},
            {'field': 'date_joined',
             'negate': False,
             'operator': 'range',
             'value': '1980-01-01,1986-01-01',
             'value_from': time.mktime(date_range[0].timetuple()),
             'value_to': time.mktime(date_range[1].timetuple())},
            {'field': 'is_superuser', 'negate': False, 'operator': 'istrue', 'value': True},
            {'field': 'is_active', 'negate': False, 'operator': 'isnull', 'value': None},
            {'field': 'is_staff', 'negate': False, 'operator': 'isfalse', 'value': False},
            {'field': 'last_name', 'negate': False, 'operator': 'icontains', 'value': 'foo'},
            {'field': 'last_name', 'negate': False, 'operator': 'lt', 'value': 'q'},
            {'field': 'last_name', 'negate': False, 'operator': 'lte', 'value': 'r'},
            {'field': 'last_name', 'negate': False, 'operator': 'gt', 'value': 'b'},
            {'field': 'last_name', 'negate': False, 'operator': 'gte', 'value': 'c'},
            {'field': 'email', 'negate': False, 'operator': 'iregex', 'value': r'^(foo|bar)$'}
        ]
        for i, field in enumerate(af.list_fields()):
            res = AdvancedFilterQueryForm._parse_query_dict(field, Rep)
            assert isinstance(res, dict)
            assert res == expected[i]


class CommonFormTest(TestCase):
    mgmg_form_data = {
        'form-TOTAL_FORMS': 1,
        'form-INITIAL_FORMS': 0
    }
    formset_data = dict(field='first_name', value='john', operator='iexact')
    default_non_field_err = ['Error validating filter forms']
    default_error = {'__all__': default_non_field_err}
    field_error = 'Select a valid choice. first_name is not one of the available choices.'

    def setUp(self):
        simple_query = Q(first_name__iexact='foo')
        self.Rep = get_user_model()
        self.user = self.Rep.objects.create(username='test')
        self.af = AdvancedFilter(query=simple_query, model='reps.SalesRep',
                                 created_by=self.user)

    def _create_query_form_data(self, form_number=0, data=None, **kwargs):
        form_data = dict(('form-%d-%s' % (form_number, k), v)
                         for k, v in (data or self.formset_data).items())
        form_data.update(self.mgmg_form_data)
        form_data.update(dict(title='baz filter'))
        form_data.update(kwargs)
        return form_data


class TestAdvancedFilterForm(CommonFormTest):
    def test_failed_validation(self):
        form = AdvancedFilterForm(self.mgmg_form_data, instance=self.af)
        assert form._model == self.Rep
        assert not form.is_valid()
        assert form.errors == dict(title=['This field is required.'],
                                   **self.default_error)
        assert form.non_field_errors() == self.default_non_field_err
        assert form.fields_formset.errors == [
            {'operator': [u'This field is required.'],
             'field': [u'This field is required.'],
             'value': [u'This field is required.']}]

    def test_invalid_field_validation(self):
        form = AdvancedFilterForm(self._create_query_form_data(), instance=self.af,
                                  filter_fields=['birth_day'])
        assert not form.is_valid()
        assert form.errors == self.default_error
        assert form.non_field_errors() == self.default_non_field_err
        assert form.fields_formset.errors == [dict(field=[self.field_error])]

    def _assert_query_content(self, query, should_be):
        assert query.children == [should_be]

    def test_update_existing_query(self):
        data = self._create_query_form_data()
        form = AdvancedFilterForm(data, instance=self.af,
                                  filter_fields=['first_name'])
        assert form.is_valid(), (form.errors, form.fields_formset.errors)
        new_instance = form.save()
        assert isinstance(new_instance, AdvancedFilter)
        assert new_instance.title == 'baz filter'
        self._assert_query_content(new_instance.query,
                                   ['first_name__iexact', 'john'])

    def test_remove_existing_query(self):
        # add new form (last name) and delete initial 1st form (for first name)
        updated_data = {'form-1-field': 'last_name', 'form-0-DELETE': True,
                        'form-INITIAL_FORMS': 1, 'form-TOTAL_FORMS': 2}
        data = self._create_query_form_data(form_number=1, **updated_data)
        form = AdvancedFilterForm(data, instance=self.af,
                                  filter_fields=['first_name', 'last_name'])
        assert form.is_valid(), (form.errors, form.fields_formset.errors)
        new_instance = form.save()
        assert isinstance(new_instance, AdvancedFilter)
        assert new_instance.title == 'baz filter'
        self._assert_query_content(new_instance.query,
                                   ['last_name__iexact', 'john'])


class TestAdminInitialization(CommonFormTest):
    def setUp(self):
        super(TestAdminInitialization, self).setUp()
        self.fdata = self._create_query_form_data(form_number=0, data={
            'field': 'groups__name', 'negate': False, 'operator': 'iexact',
            'value': 'bar'})
        self.fdata.update(self._create_query_form_data(form_number=1, data={
            'field': '_OR', 'operator': 'iexact', 'value': 'null'}))
        self.fdata.update(self._create_query_form_data(form_number=2, data={
            'field': 'first_name', 'negate': False, 'operator': 'iexact',
            'value': 'fez'}))
        self.fdata['form-TOTAL_FORMS'] = 3
        print(self.fdata)

        class RepModelAdmin(admin.ModelAdmin):
            model = self.Rep
            advanced_filter_fields = ['groups__name', 'first_name']

        self.rep_model_admin = RepModelAdmin

        # modeladmin is initially unregistered
        try:
            admin.site.unregister(self.Rep)
        except admin.sites.NotRegistered:
            print('Rep Not registered yet')

    def test_field_resolution(self):
        # registering admin is not required if passing model_admin
        form = AdvancedFilterForm(data=self.fdata, model_admin=self.rep_model_admin)
        assert form.is_valid()

        # but if passing only instance, then field choices is empty
        form = AdvancedFilterForm(data=self.fdata, instance=self.af)
        assert not form.is_valid()
        field_choices = form.fields_formset.forms[0].fields['field'].choices
        assert len(field_choices) == 1  # _OR choice always present

        # registering an admin allows passing only instance to find valid choices
        admin.site.register(self.Rep, self.rep_model_admin)
        form = AdvancedFilterForm(data=self.fdata, instance=self.af)
        assert form.is_valid()
        field_choices = form.fields_formset.forms[0].fields['field'].choices
        assert len(field_choices) == 3

    def test_create_instance_with_modeladmin(self):
        form = AdvancedFilterForm(data=self.fdata, model_admin=self.rep_model_admin)
        assert form.is_valid(), 'errors: %s, %s' % (form.errors, form.fields_formset.errors)
        instance = form.save(commit=False)
        instance.created_by = self.user
        assert isinstance(instance, AdvancedFilter)
        instance.save()
        assert instance.pk is not None
        print(vars(instance.query))
        assert instance.query.connector == 'OR'
        assert instance.query.children == [
            ['groups__name__iexact', 'bar'],
            ['first_name__iexact', 'fez']
        ]

    def test_invalid_initialization(self):
        # exception is raised when passing neither instance nor model admin
        with pytest.raises(Exception) as excinfo:
            AdvancedFilterForm(data=self.fdata)

        # the message refers to the missing implementation
        assert 'Adding new AdvancedFilter from admin is not supported' in str(excinfo.value)
