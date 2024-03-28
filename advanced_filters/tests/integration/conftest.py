import pytest

from tests.factories import ClientFactory, SalesRepFactory


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server.url


@pytest.fixture
@pytest.mark.usefixtures("db")
def user():
    return SalesRepFactory()


@pytest.fixture()
def client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def three_clients(user):
    return ClientFactory.create_batch(3, assigned_to=user)
