from django.test import TestCase
from django.db.models import Q

from ..models import AdvancedFilter


class AdvancedFilterPermissions(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        User = get_user_model()
        self.user = User.objects.create(email='test1@example.com')

        self.group = Group.objects.create(name='test')

        self.user.set_password('test')
        self.user.groups.add(self.group)
        self.user.save()

        self.advancedfilter = AdvancedFilter.objects.create(
            title='test', url='test', created_by=self.user,
            b64_query='MQ=='
        )

    def test_filter_by_user_empty(self):
        qs = AdvancedFilter.objects.filter_by_user(user=self.user)

        self.assertEqual(qs.count(), 0)

    def test_filter_by_user_users(self):
        self.advancedfilter.users.add(self.user)

        qs = AdvancedFilter.objects.filter_by_user(user=self.user)

        self.assertEqual(qs.count(), 1)

    def test_filter_by_user_groups(self):
        self.advancedfilter.groups.add(self.group)

        qs = AdvancedFilter.objects.filter_by_user(user=self.user)

        self.assertEqual(qs.count(), 1)

    def test_list_fields(self):
        self.advancedfilter.query = Q(some_field__iexact='some_value')
        fields = self.advancedfilter.list_fields()
        assert fields == [{
            'field': 'some_field__iexact',
            'value': 'some_value',
            'negate': False,
        }]

        self.advancedfilter.query = ~Q(another_field__range=(1, 10))
        fields = self.advancedfilter.list_fields()
        assert fields == [{
            'field': 'another_field__range',
            'value': [1, 10],
            'value_from': 1,
            'value_to': 10,
            'negate': True,
        }]
