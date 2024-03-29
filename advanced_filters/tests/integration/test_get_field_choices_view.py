import json
from datetime import timedelta
from operator import itemgetter

import factory
import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str

from tests.factories import ClientFactory

URL_NAME = "afilters_get_field_choices"


def parse_json(content):
    return json.loads(force_str(content))


def assert_json(content, expect):
    assert parse_json(content) == expect


def assert_view_error(client, error, exception=None, **view_kwargs):
    """Ensure view either raises exception or returns a 400 json error"""
    view_url = reverse(URL_NAME, kwargs=view_kwargs)

    if exception is not None:
        with pytest.raises(exception) as excinfo:
            client.get(view_url)
        assert error == str(excinfo.value)
        return

    response = client.get(view_url)
    assert response.status_code == 400
    assert_json(response.content, dict(error=error))


NO_APP_INSTALLED_ERROR = "No installed app with label 'foo'."
ARGUMENT_LENGTH_ERROR = "not enough values to unpack (expected 2, got 1)"
MISSING_FIELD_ERROR = "SalesRep has no field named 'baz'"
NO_MODEL_ERROR = "App 'reps' doesn't have a 'Foo' model."


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
    result = parse_json(response.content)
    data = (dict(id=e.email, text=e.email) for e in three_clients)
    sort_func = itemgetter("id")
    assert sorted(result["results"], key=sort_func) == sorted(data, key=sort_func)


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


def test_choices_no_date_fields_support(user, client, settings):
    settings.ADVANCED_FILTERS_MAX_CHOICES = 4
    logins = [timezone.now(), timezone.now() - timedelta(days=1), None]
    ClientFactory.create_batch(
        3, assigned_to=user, email="foo@bar.com", last_login=factory.Iterator(logins)
    )
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="last_login")
    )
    response = client.get(view_url)
    assert_json(response.content, {"results": []})


def test_choices_has_null(user, client, settings):
    settings.ADVANCED_FILTERS_MAX_CHOICES = 4
    named_users = ClientFactory.create_batch(2, assigned_to=user)
    names = [None] + sorted({nu.first_name for nu in named_users})
    assert len(named_users) == 2
    ClientFactory.create_batch(2, assigned_to=user, first_name=None)
    view_url = reverse(
        URL_NAME, kwargs=dict(model="customers.Client", field_name="first_name")
    )
    response = client.get(view_url)
    assert_json(
        response.content,
        {"results": [{"id": name, "text": str(name)} for name in names]},
    )
