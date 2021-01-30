from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

# django < 1.9 support
from django import VERSION
if VERSION >= (2, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


class Client(AbstractBaseUser):
    VALID_LANGUAGES = (
        ('en', 'English'),
        ('sp', 'Spanish'),
        ('it', 'Italian'),
    )
    USERNAME_FIELD = 'email'

    language = models.CharField(max_length=8, choices=VALID_LANGUAGES,
                                default='en')
    email = models.EmailField(_('email address'), blank=True)
    first_name = models.CharField(_('first name'), max_length=30, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    assigned_to = models.ForeignKey('reps.SalesRep', on_delete=models.CASCADE)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
