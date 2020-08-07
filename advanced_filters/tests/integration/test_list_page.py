import re

from django.contrib.auth.models import Permission
from playwright.sync_api import Page, expect
import pytest

TEXT = {
    "login_page_title": re.compile(r".*Log in.*"),
    "client_page_title": re.compile(r".*Select client to change.*"),
    "advanced_filter_button_text": "Advanced Filter",
    "advanced_filter_modal_heading": "Create advanced filter",
    "advanced_filter_title_label": "Title",
    "advanced_filter_add_another_rule_link": "Add another filter",
}
SELECTOR = {
    "modal_id": "#advanced_filters",
}

expect.set_options(timeout=2_000)


@pytest.fixture(autouse=True)
def grant_permissions(user):
    # grant permission to our admin user
    user.user_permissions.add(Permission.objects.get(codename="change_client"))


def authenticate(base_url, page: Page):
    page.goto(f"{base_url}/admin/")
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(TEXT["login_page_title"])
    # Expect auth form to have a well known structure
    page.get_by_label("Username").fill("user")
    page.get_by_label("Password").fill("test")
    page.get_by_text("Log in").click()
    expect(page.get_by_text("Welcome, user")).not_to_be_empty()


@pytest.mark.only_browser("chromium")
def test_advanced_filter_modal_shown(page: Page, base_url):
    # GIVEN a logged in user
    authenticate(base_url, page)

    # WHEN the user navigates to the list page
    page.goto(f"{base_url}/admin/customers/client/")

    # THEN the client list page should load
    expect(page).to_have_title(TEXT["client_page_title"])
    # the page should contain an unordered list with a link to the filter
    tools_list = page.get_by_role("listitem").filter(
        has_text=TEXT["advanced_filter_button_text"]
    )
    advanced_filter_link = tools_list.get_by_role(
        "link", name=TEXT["advanced_filter_button_text"]
    )
    expect(advanced_filter_link).to_be_visible()
    # when the button is clicked, the modal is displayed
    advanced_filter_link.click()
    modal = page.locator(SELECTOR["modal_id"])
    # the modal contains a heading
    expect(
        modal.get_by_role("heading", name=TEXT["advanced_filter_modal_heading"])
    ).to_be_visible()
    # and a form with a mandatory title field
    expect(modal.get_by_label(TEXT["advanced_filter_title_label"])).to_be_visible()
    # TODO: the following assertion demonstrates a bug
    # below it, the modal contains a blank "extra" filter, with the required fields
    # expect(modal.locator("select[name=form-0-field]")).to_be_visible()
    # and a button to add another filter
    expect(
        modal.get_by_role("link", name=TEXT["advanced_filter_add_another_rule_link"])
    ).to_be_visible()
