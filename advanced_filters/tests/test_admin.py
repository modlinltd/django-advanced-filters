from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.test import TestCase

from ..models import AdvancedFilter
from tests import factories


class ChageFormAdminTest(TestCase):
    def setUp(self):
        self.user = factories.SalesRep()
        assert self.client.login(username='user', password='test')
        self.a = AdvancedFilter(title='test', url='test', created_by=self.user,
                                model='customers.Client')
        self.a.query = Q(email__iexact='a@a.com')
        self.a.save()

    def test_change_page_requires_perms(self):
        url = reverse('admin:advanced_filters_advancedfilter_change',
                      args=(self.a.pk,))
        res = self.client.get(url)
        assert res.status_code == 403

    def test_change_page_renders(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_advancedfilter'))
        url = reverse('admin:advanced_filters_advancedfilter_change',
                      args=(self.a.pk,))
        res = self.client.get(url)
        assert res.status_code == 200

    def test_change_and_goto(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_advancedfilter'))
        url = reverse('admin:advanced_filters_advancedfilter_change',
                      args=(self.a.pk,))
        form_data = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 0,
                     '_save_goto': 1}
        res = self.client.post(url, data=form_data)
        assert res.status_code == 302
        assert res.url.endswith('admin/customers/client/?_afilter=1')

    def test_create_page_disabled(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='add_advancedfilter'))
        url = reverse('admin:advanced_filters_advancedfilter_add')
        res = self.client.get(url)
        assert res.status_code == 403


class AdvancedFilterCreationTest(TestCase):
    form_data = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 0,
                 'action': 'advanced_filters'}
    good_data = {'title': 'Test title', 'form-0-field': 'language',
                 'form-0-operator': 'iexact', 'form-0-value': 'ru', }
    b64query = ('eyJjb25uZWN0b3IiOiAiQU5EIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImNoaWxkcm'
                'VuIjogW1sibGFuZ3VhZ2VfX2lleGFjdCIsICJydSJdXX0=')

    def setUp(self):
        self.user = factories.SalesRep()
        assert self.client.login(username='user', password='test')

    def test_changelist_includes_form(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_client'))
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url)
        assert res.status_code == 200
        title = ['Create advanced filter']
        fields = ['First name', 'Language', 'Sales Rep']
        for part in title + fields:
            assert part in res.content

    def test_create_form_validation(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_client'))
        url = reverse('admin:customers_client_changelist')
        form_data = self.form_data.copy()
        res = self.client.post(url, data=form_data)
        assert res.status_code == 200
        form = res.context_data['advanced_filters']
        assert 'title' in form.errors
        assert '__all__' in form.errors
        assert form.errors['title'] == ['This field is required.']
        assert form.errors['__all__'] == ['Error validating filter forms']

    def test_create_form_valid(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_client'))
        url = reverse('admin:customers_client_changelist')
        form_data = self.form_data.copy()
        form_data.update(self.good_data)
        res = self.client.post(url, data=form_data)
        assert res.status_code == 200
        form = res.context_data['advanced_filters']
        assert form.is_valid()
        assert AdvancedFilter.objects.count() == 1
        created_filter = AdvancedFilter.objects.last()
        assert created_filter.title == self.good_data['title']
        assert created_filter.b64_query == self.b64query

        # save with redirect to filter
        form_data['_save_goto'] = 1
        res = self.client.post(url, data=form_data)
        assert res.status_code == 302
        assert AdvancedFilter.objects.count() == 2
        created_filter = AdvancedFilter.objects.last()
        assert res.url.endswith('admin/customers/client/?_afilter=%s' %
                                created_filter.pk)
        assert created_filter.b64_query == self.b64query


class AdvancedFilterUsageTest(TestCase):
    def setUp(self):
        self.user = factories.SalesRep()
        assert self.client.login(username='user', password='test')
        factories.Client.create_batch(8, assigned_to=self.user, language='en')
        factories.Client.create_batch(2, assigned_to=self.user, language='ru')
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_client'))
        self.a = AdvancedFilter(title='Russian speakers', url='foo',
                                created_by=self.user, model='customers.Client')
        self.a.query = Q(language='ru')
        self.a.save()

    def test_filters_not_available(self):
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url, data={'_afilter': self.a.pk})
        assert res.status_code == 200
        assert not res.context_data['cl'].filter_specs
        # filter not applied due to user not being in list
        assert res.context_data['cl'].queryset.count() == 10

    def test_filters_available_to_users(self):
        self.a.users.add(self.user)
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url, data={'_afilter': self.a.pk})
        assert res.status_code == 200
        assert res.context_data['cl'].filter_specs
        assert res.context_data['cl'].queryset.count() == 2

    def test_filters_available_to_groups(self):
        group = self.user.groups.create()
        self.a.groups.add(group)
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url, data={'_afilter': self.a.pk})
        assert res.status_code == 200
        assert res.context_data['cl'].filter_specs
        assert res.context_data['cl'].queryset.count() == 2
