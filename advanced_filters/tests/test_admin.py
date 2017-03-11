from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.test import TestCase

from ..models import AdvancedFilter
from tests import factories


class ChageFormAdminTest(TestCase):
    """ Test the AdvancedFilter admin change page """
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

        with self.settings(ADVANCED_FILTER_EDIT_BY_USER=False):
            res = self.client.get(url)
        assert res.status_code == 200

    def test_change_and_goto(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_advancedfilter'))
        url = reverse('admin:advanced_filters_advancedfilter_change',
                      args=(self.a.pk,))
        form_data = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 0,
                     '_save_goto': 1}
        with self.settings(ADVANCED_FILTER_EDIT_BY_USER=False):
            res = self.client.post(url, data=form_data)
        assert res.status_code == 302
        # django == 1.5 support
        if hasattr(res, 'url'):
            assert res.url.endswith('admin/customers/client/?_afilter=1')
        else:
            url = res['location']
            assert url.endswith('admin/customers/client/?_afilter=1')

    def test_create_page_disabled(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='add_advancedfilter'))
        url = reverse('admin:advanced_filters_advancedfilter_add')
        res = self.client.get(url)
        assert res.status_code == 403


class AdvancedFilterCreationTest(TestCase):
    """ Test creation of AdvancedFilter in target model changelist """
    form_data = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 0,
                 'action': 'advanced_filters'}
    good_data = {'title': 'Test title', 'form-0-field': 'language',
                 'form-0-operator': 'iexact', 'form-0-value': 'ru', }
    query = ['language__iexact', 'ru']

    def setUp(self):
        self.user = factories.SalesRep()
        assert self.client.login(username='user', password='test')

    def test_changelist_includes_form(self):
        self.user.user_permissions.add(Permission.objects.get(
            codename='change_client'))
        url = reverse('admin:customers_client_changelist')
        with self.settings(ADVANCED_FILTER_EDIT_BY_USER=False):
            res = self.client.get(url)
        assert res.status_code == 200
        title = ['Create advanced filter']
        fields = ['First name', 'Language', 'Sales Rep']
        # python >= 3.3 support
        response_content = res.content.decode('utf-8')
        for part in title + fields:
            assert part in response_content

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

        # django == 1.5 support
        created_filter = AdvancedFilter.objects.order_by('-pk')[0]

        assert created_filter.title == self.good_data['title']
        assert list(created_filter.query.children[0]) == self.query

        # save with redirect to filter
        form_data['_save_goto'] = 1
        res = self.client.post(url, data=form_data)
        assert res.status_code == 302
        assert AdvancedFilter.objects.count() == 2

        # django == 1.5 support
        created_filter = AdvancedFilter.objects.order_by('-pk')[0]
        if hasattr(res, 'url'):
            assert res.url.endswith('admin/customers/client/?_afilter=%s' %
                                    created_filter.pk)
        else:
            url = res['location']
            assert url.endswith('admin/customers/client/?_afilter=%s' %
                                created_filter.pk)

        assert list(created_filter.query.children[0]) == self.query


class AdvancedFilterUsageTest(TestCase):
    """ Test filter visibility and actual filtering of a changelist """
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
        cl = res.context_data['cl']
        assert not cl.filter_specs
        # filter not applied due to user not being in list
        if hasattr(cl, 'queryset'):
            assert cl.queryset.count() == 10
        else:
            # django == 1.5 support
            assert cl.query_set.count() == 10

    def test_filters_available_to_users(self):
        self.a.users.add(self.user)
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url, data={'_afilter': self.a.pk})
        assert res.status_code == 200
        cl = res.context_data['cl']
        assert cl.filter_specs
        if hasattr(cl, 'queryset'):
            assert cl.queryset.count() == 2
        else:
            # django == 1.5 support
            assert cl.query_set.count() == 2

    def test_filters_available_to_groups(self):
        group = self.user.groups.create()
        self.a.groups.add(group)
        url = reverse('admin:customers_client_changelist')
        res = self.client.get(url, data={'_afilter': self.a.pk})
        assert res.status_code == 200
        cl = res.context_data['cl']
        assert cl.filter_specs
        if hasattr(cl, 'queryset'):
            assert cl.queryset.count() == 2
        else:
            # django == 1.5 support
            assert cl.query_set.count() == 2
