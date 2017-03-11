import sys

from django.test import TestCase
try:
    from django.test import override_settings
except ImportError:
    from django.test.utils import override_settings
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
import django

from tests import factories


class TestGetFieldChoicesView(TestCase):
    url_name = 'afilters_get_field_choices'

    def setUp(self):
        self.user = factories.SalesRep()
        assert self.client.login(username='user', password='test')

    def assert_json(self, response, expect):
        self.assertJSONEqual(force_text(response.content), expect)

    def assert_view_error(self, error, exception=None, **view_kwargs):
        """ Ensure view either raises exception or returns a 400 json error """
        view_url = reverse(self.url_name, kwargs=view_kwargs)
        if exception is not None:
            self.assertRaisesMessage(
                exception, error, self.client.get, view_url)
            return
        res = self.client.get(view_url)
        assert res.status_code == 400
        self.assert_json(res, dict(error=error))

    def test_invalid_args(self):
        self.assert_view_error("GetFieldChoices view requires 2 arguments")
        if 'PyPy' in getattr(sys, 'subversion', ()):
            self.assert_view_error(
                'expected length 2, got 1',
                model='a', field_name='b', exception=ValueError)
        elif sys.version_info >= (3, 5):
            self.assert_view_error(
                'not enough values to unpack (expected 2, got 1)', model='a',
                field_name='b', exception=ValueError)
        else:
            self.assert_view_error(
                'need more than 1 value to unpack', model='a',
                field_name='b', exception=ValueError)
        if django.VERSION >= (1, 7):
            self.assert_view_error("No installed app with label 'foo'.",
                                   model='foo.test', field_name='baz')
            self.assert_view_error("App 'reps' doesn't have a 'foo' model.",
                                   model='reps.Foo', field_name='b')
        else:
            self.assert_view_error("No installed app/model: foo.test",
                                   model='foo.test', field_name='baz')
            self.assert_view_error("No installed app/model: reps.Foo",
                                   model='reps.Foo', field_name='b')
        if sys.version_info >= (3, 3):
            expected_exception = "SalesRep has no field named 'baz'"
        else:
            expected_exception = "SalesRep has no field named u'baz'"
        self.assert_view_error(expected_exception,
                               model='reps.SalesRep', field_name='baz')

    def test_field_with_choices(self):
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='language'))
        res = self.client.get(view_url)
        self.assert_json(res, {
            'results': [
                {'id': 'en', 'text': 'English'},
                {'id': 'it', 'text': 'Italian'},
                {'id': 'sp', 'text': 'Spanish'}
            ]
        })

    @override_settings(ADVANCED_FILTERS_DISABLE_FOR_FIELDS=('email',))
    def test_disabled_field(self):
        factories.Client.create_batch(3, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='email'))
        res = self.client.get(view_url)
        self.assert_json(res, {'results': []})

    def test_disabled_field_types(self):
        factories.Client.create_batch(3, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='is_active'))
        res = self.client.get(view_url)
        self.assert_json(res, {'results': []})

    def test_database_choices(self):
        clients = factories.Client.create_batch(3, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='email'))
        res = self.client.get(view_url)
        self.assert_json(res, {
            'results': [dict(id=e.email, text=e.email) for e in clients]
        })

    @override_settings(ADVANCED_FILTERS_MAX_CHOICES=4)
    def test_more_than_max_database_choices(self):
        factories.Client.create_batch(5, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='id'))
        res = self.client.get(view_url)
        self.assert_json(res, {'results': []})

    @override_settings(ADVANCED_FILTERS_MAX_CHOICES=4)
    def test_distinct_database_choices(self):
        factories.Client.create_batch(5, assigned_to=self.user, email="foo@bar.com")
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='email'))
        res = self.client.get(view_url)
        self.assert_json(res, {'results': [{'id': 'foo@bar.com', 'text': 'foo@bar.com'}]})
