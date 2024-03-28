import pytest
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.urls import reverse

from advanced_filters.models import AdvancedFilter
from advanced_filters.tests.factories import AdvancedFilterFactory

URL_NAME_CHANGE = "admin:advanced_filters_advancedfilter_change"
URL_NAME_ADD = "admin:advanced_filters_advancedfilter_add"
URL_NAME_CLIENT_CHANGELIST = "admin:customers_client_changelist"


@pytest.fixture
def advanced_filter(user):
    af = AdvancedFilterFactory.build(created_by=user)
    af.query = Q(email__iexact="a@a.com")
    af.save()
    return af


def test_change_page_requires_perms(client, advanced_filter):
    url = reverse(URL_NAME_CHANGE, args=(advanced_filter.pk,))
    res = client.get(url)
    assert res.status_code == 403


def test_change_page_renders(client, user, settings, advanced_filter):
    user.user_permissions.add(Permission.objects.get(codename="change_advancedfilter"))
    url = reverse(URL_NAME_CHANGE, args=(advanced_filter.pk,))

    settings.ADVANCED_FILTER_EDIT_BY_USER = False
    res = client.get(url)
    assert res.status_code == 200


def test_change_and_goto(client, user, settings, advanced_filter):
    user.user_permissions.add(Permission.objects.get(codename="change_advancedfilter"))
    url = reverse(URL_NAME_CHANGE, args=(advanced_filter.pk,))
    form_data = {"form-TOTAL_FORMS": 1, "form-INITIAL_FORMS": 0, "_save_goto": 1}
    settings.ADVANCED_FILTER_EDIT_BY_USER = False
    res = client.post(url, data=form_data)
    assert res.status_code == 302
    url = res["location"]
    changelist_url = reverse(URL_NAME_CLIENT_CHANGELIST)
    new_filter_id = AdvancedFilter.objects.last().pk
    assert url.endswith(f"{changelist_url}?_afilter={new_filter_id}")


def test_create_page_disabled(client, user):
    user.user_permissions.add(Permission.objects.get(codename="add_advancedfilter"))
    url = reverse(URL_NAME_ADD)
    res = client.get(url)
    assert res.status_code == 403
    assert AdvancedFilter.objects.count() == 0
