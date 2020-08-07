import pytest


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server.url
