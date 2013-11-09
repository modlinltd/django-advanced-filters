from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class UserLookupManager(models.Manager):
    def filter_by_user(self, user):
        """All filters that should be displayed to a user (by users/group)"""

        return self.filter(Q(users=user) | Q(groups__in=user.groups.all()))


class AdvancedFilter(models.Model):
    class Meta:
        verbose_name = _('Advanced Filter')
        verbose_name_plural = _('Advanced Filters')

    objects = UserLookupManager()

    title = models.CharField(max_length=255, null=False, blank=False)
    created_by = models.ForeignKey(get_user_model(),
                                   related_name='created_advanced_filters')
    users = models.ManyToManyField(get_user_model(), blank=True)
    groups = models.ManyToManyField('auth.Group', blank=True)
    b64_query = models.CharField(max_length=2048)
