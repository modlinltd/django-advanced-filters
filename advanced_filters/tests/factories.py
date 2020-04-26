import factory

from tests.factories import SalesRepFactory


class AdvancedFilterFactory(factory.django.DjangoModelFactory):
    model = 'customers.Client'

    class Meta:
        model = 'advanced_filters.AdvancedFilter'
