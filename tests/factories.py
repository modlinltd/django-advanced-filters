import factory


class SalesRepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'reps.SalesRep'
        django_get_or_create = ('username',)

    username = 'user'
    password = 'test'
    email = 'jacob@example.com'
    is_staff = True
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # avoid ``manager.create(*args, **kwargs)`` = encrypt password
        return manager.create_user(*args, **kwargs)


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'customers.Client'

    first_name = factory.faker.Faker('first_name')
    email = factory.Sequence(lambda n: 'c%d@foo.com' % n)
