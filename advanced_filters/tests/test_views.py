from django.test import TestCase, override_settings

from django.core.urlresolvers import reverse
from tests import factories


class TestGetFieldChoicesView(TestCase):
    url_name = 'afilters_get_field_choices'

    def setUp(self):
        self.user = factories.SalesRep()
        self.assertTrue(self.client.login(username='user', password='test'))

    def assert_view_error(self, error, exception=None, **view_kwargs):
        """ Ensure view either raises exception or returns a 400 json error """
        view_url = reverse(self.url_name, kwargs=view_kwargs)
        if exception is not None:
            with self.assertRaisesMessage(exception, error):
                self.client.get(view_url)
            return
        res = self.client.get(view_url)
        self.assertEqual(res.status_code, 400)
        self.assertJSONEqual(res.content, dict(error=error))

    def test_invalid_args(self):
        self.assert_view_error("GetFieldChoices view requires 2 arguments")
        self.assert_view_error('need more than 1 value to unpack', model='a',
                               field_name='b', exception=ValueError)
        self.assert_view_error("No installed app with label 'foo'.",
                               model='foo.test', field_name='baz')
        self.assert_view_error("App 'reps' doesn't have a 'foo' model.",
                               model='reps.Foo', field_name='b')
        self.assert_view_error("SalesRep has no field named u'baz'",
                               model='reps.SalesRep', field_name='baz')

    def test_field_with_choices(self):
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='language'))
        res = self.client.get(view_url)
        self.assertJSONEqual(res.content, {
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
        self.assertJSONEqual(res.content, {'results': []})

    def test_disabled_field_types(self):
        factories.Client.create_batch(3, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='is_active'))
        res = self.client.get(view_url)
        self.assertJSONEqual(res.content, {'results': []})

    def test_database_choices(self):
        factories.Client.create_batch(3, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='email'))
        res = self.client.get(view_url)
        self.assertJSONEqual(res.content, {
            'results': [
                {'id': 'c0@foo.com', 'text': 'c0@foo.com'},
                {'id': 'c1@foo.com', 'text': 'c1@foo.com'},
                {'id': 'c2@foo.com', 'text': 'c2@foo.com'}
            ]
        })

    @override_settings(ADVANCED_FILTERS_MAX_CHOICES=4)
    def test_more_than_max_database_choices(self):
        factories.Client.create_batch(5, assigned_to=self.user)
        view_url = reverse(self.url_name, kwargs=dict(
            model='customers.Client', field_name='first_name'))
        res = self.client.get(view_url)
        self.assertJSONEqual(res.content, {'results': []})
