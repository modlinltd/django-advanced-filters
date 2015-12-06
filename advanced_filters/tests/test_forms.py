from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q, FieldDoesNotExist
from django.test import TestCase

import pytest

from ..models import AdvancedFilter
from ..forms import AdvancedFilterQueryForm


class TestVaryingCharField(TestCase):
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

    def test_restore_complex_existing_query(self):
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
             'value_from': 315532800.0,
             'value_to': 504921600.0},
            {'field': 'is_superuser', 'negate': False, 'operator': 'istrue', 'value': True},
            {'field': 'is_active', 'negate': True, 'operator': 'isnull', 'value': None},
        ]
        for i, field in enumerate(af.list_fields()):
            res = AdvancedFilterQueryForm._parse_query_dict(field, Rep)
            assert isinstance(res, dict)
            assert res == expected[i]
