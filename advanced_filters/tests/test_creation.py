import pytest
from django.contrib.auth.models import Permission

from ..models import AdvancedFilter

try:
    from django.urls import reverse_lazy
except ImportError:  # Django < 2.0
    from django.core.urlresolvers import reverse_lazy

URL_CLIENT_CHANGELIST = reverse_lazy("admin:customers_client_changelist")


def test_changelist_includes_form(user, settings, client):
    user.user_permissions.add(Permission.objects.get(codename="change_client"))
    settings.ADVANCED_FILTER_EDIT_BY_USER = False
    res = client.get(URL_CLIENT_CHANGELIST)
    assert res.status_code == 200
    title = ["Create advanced filter"]
    fields = ["First name", "Language", "Sales Rep"]
    response_content = res.content.decode("utf-8")
    for part in title + fields:
        assert part in response_content


@pytest.fixture
def form_data():
    return {
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 0,
        "action": "advanced_filters",
    }


def test_create_form_validation(user, client, form_data):
    user.user_permissions.add(Permission.objects.get(codename="change_client"))
    res = client.post(URL_CLIENT_CHANGELIST, data=form_data)
    assert res.status_code == 200
    form = res.context_data["advanced_filters"]
    assert "title" in form.errors
    assert "__all__" in form.errors
    assert form.errors["title"] == ["This field is required."]
    assert form.errors["__all__"] == ["Error validating filter forms"]


@pytest.fixture()
def good_data(form_data):
    form_data.update(
        {
            "title": "Test title",
            "form-0-field": "language",
            "form-0-operator": "iexact",
            "form-0-value": "ru",
        }
    )
    return form_data


@pytest.fixture()
def query():
    return ["language__iexact", "ru"]


def test_create_form_valid(user, client, good_data, query):
    assert AdvancedFilter.objects.count() == 0
    user.user_permissions.add(Permission.objects.get(codename="change_client"))
    res = client.post(URL_CLIENT_CHANGELIST, data=good_data)
    assert res.status_code == 200
    form = res.context_data["advanced_filters"]
    assert form.is_valid()
    assert AdvancedFilter.objects.count() == 1

    created_filter = AdvancedFilter.objects.order_by("pk").last()

    assert created_filter.title == good_data["title"]
    assert list(created_filter.query.children[0]) == query

    # save with redirect to filter
    good_data["_save_goto"] = 1
    res = client.post(URL_CLIENT_CHANGELIST, data=good_data)
    assert res.status_code == 302
    assert AdvancedFilter.objects.count() == 2

    created_filter = AdvancedFilter.objects.order_by("pk").last()
    url = res["location"]
    assert url.endswith("%s?_afilter=%s" % (URL_CLIENT_CHANGELIST, created_filter.pk))

    assert list(created_filter.query.children[0]) == query
