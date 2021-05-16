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
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(SalesRepFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'customers.Client'

    first_name = factory.faker.Faker('first_name')
    email = factory.Sequence(lambda n: 'c%d@foo.com' % n)
