import pytest
from tests.factories import ClientFactory, SalesRepFactory


@pytest.fixture
def user(db):
    return SalesRepFactory()


@pytest.fixture()
def client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def three_clients(user):
    return ClientFactory.create_batch(3, assigned_to=user)
