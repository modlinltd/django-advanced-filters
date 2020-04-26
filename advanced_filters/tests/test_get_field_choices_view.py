import json
import sys

import django
import pytest
from django.utils.encoding import force_text
from tests.factories import ClientFactory

try:
    from django.urls import reverse
except ImportError:  # Django < 2.0
    from django.core.urlresolvers import reverse


URL_NAME = "afilters_get_field_choices"


def assert_json(content, expect):
    assert json.loads(force_text(content)) == expect


def assert_view_error(client, error, exception=None, **view_kwargs):
    """ Ensure view either raises exception or returns a 400 json error """
    view_url = reverse(URL_NAME, kwargs=view_kwargs)

    if exception is not None:
        with pytest.raises(exception) as excinfo:
            client.get(view_url)
        assert error == str(excinfo.value)
        return

    response = client.get(view_url)
    assert response.status_code == 400
    assert_json(response.content, dict(error=error))


if django.VERSION < (1, 7):
    NO_APP_INSTALLED_ERROR = "No installed app/model: foo.test"
    NO_MODEL_ERROR = "No installed app/model: reps.Foo"
else:
    NO_APP_INSTALLED_ERROR = "No installed app with label 'foo'."
    NO_MODEL_ERROR = "App 'reps' doesn't have a 'Foo' model."


if "PyPy" in getattr(sys, "subversion", ()):
    ARGUMENT_LENGTH_ERROR = "expected length 2, got 1"
elif sys.version_info >= (3, 5):
    ARGUMENT_LENGTH_ERROR = "not enough values to unpack (expected 2, got 1)"
else:
    ARGUMENT_LENGTH_ERROR = "need more than 1 value to unpack"

MISSING_FIELD_ERROR = "SalesRep has no field named 'baz'"


def test_invalid_view_kwargs(client):
    assert_view_error(client, "GetFieldChoices view requires 2 arguments")
    assert_view_error(
        client, ARGUMENT_LENGTH_ERROR, model="a", field_name="b", exception=ValueError
    )
    assert_view_error(
        client, NO_APP_INSTALLED_ERROR, model="foo.test", field_name="baz"
    )
    assert_view_error(client, NO_MODEL_ERROR, model="reps.Foo", field_name="b")
    assert_view_error(
        client, MISSING_FIELD_ERROR, model="reps.SalesRep", field_name="baz"
    )


def test_field_with_choices(client):
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="language")
    )
    response = client.get(view_url)
    assert_json(
        response.content,
        {
            "results": [
                {"id": "en", "text": "English"},
                {"id": "it", "text": "Italian"},
                {"id": "sp", "text": "Spanish"},
            ]
        },
    )


@pytest.fixture
def three_clients(user):
    return ClientFactory.create_batch(3, assigned_to=user)


def test_disabled_field(three_clients, client, settings):
    settings.ADVANCED_FILTERS_DISABLE_FOR_FIELDS = ("email",)
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="email")
    )
    response = client.get(view_url)
    assert_json(response.content, {"results": []})


def test_disabled_field_types(three_clients, client):
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="is_active")
    )
    response = client.get(view_url)
    assert_json(response.content, {"results": []})


def test_database_choices(three_clients, client):
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="email")
    )
    response = client.get(view_url)
    assert_json(
        response.content,
        {"results": [dict(id=e.email, text=e.email) for e in three_clients]},
    )


def test_more_than_max_database_choices(user, client, settings):
    settings.ADVANCED_FILTERS_MAX_CHOICES = 4
    ClientFactory.create_batch(5, assigned_to=user)
    view_url = reverse(URL_NAME, kwargs=dict(model="customers.Client", field_name="id"))
    response = client.get(view_url)
    assert_json(response.content, {"results": []})


def test_distinct_database_choices(user, client, settings):
    settings.ADVANCED_FILTERS_MAX_CHOICES = 4
    ClientFactory.create_batch(5, assigned_to=user, email="foo@bar.com")
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="email")
    )
    response = client.get(view_url)
    assert_json(
        response.content, {"results": [{"id": "foo@bar.com", "text": "foo@bar.com"}]}
    )
