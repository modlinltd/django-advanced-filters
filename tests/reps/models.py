from django.contrib.auth.models import AbstractUser


class SalesRep(AbstractUser):
    USERNAME_FIELD = 'username'
