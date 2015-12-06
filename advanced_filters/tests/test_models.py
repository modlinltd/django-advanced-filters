from django.test import TestCase

from advanced_filters.models import AdvancedFilter


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

        self.assertEquals(qs.count(), 0)

    def test_filter_by_user_users(self):
        self.advancedfilter.users.add(self.user)

        qs = AdvancedFilter.objects.filter_by_user(user=self.user)

        self.assertEquals(qs.count(), 1)

    def test_filter_by_user_groups(self):
        self.advancedfilter.groups.add(self.group)

        qs = AdvancedFilter.objects.filter_by_user(user=self.user)

        self.assertEquals(qs.count(), 1)
