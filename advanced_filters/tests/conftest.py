import pytest
from tests.factories import SalesRepFactory


@pytest.fixture
def user(db):
    return SalesRepFactory()


@pytest.fixture()
def client(client, user):
    client.force_login(user)
    return client
