import os
from time import sleep
from types import MethodType

import pytest
from django.contrib.auth.models import Permission
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import Options, WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tests.factories import ClientFactory

try:
    from django.urls import reverse
except ImportError:  # Django < 2.0
    from django.core.urlresolvers import reverse


LOGGED_IN_CLIENT_SELECTOR = ".app-customers.module .model-client"
CREATE_AFILTER_SELECTOR = ".object-tools li .afilters a"
AFILTER_MODAL_ID = "advanced_filters"
FORM_TITLE_INPUT = "#id_title"
FORM_SELECT2_CONTAINER = "#form-group tr.form-row .query-value"
FORM_SELECT2_INPUT = ".select2-input"
FORM_ROW_VALUE = "#id_form-0-value"
SAVE_AND_FILTER = "input[name='_save_goto']"
CHANGELIST_FIELD_NAME = "td.field-first_name"
# FILTER_HEADING = "h3:not(#changelist-filter-clear)"
FILTER_HEADING = "//h3[contains(text(), 'By Advanced filters')]"
FILTER_UL = "%s/following::ul" % FILTER_HEADING


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def selenium(live_server, user, pytestconfig):
    """ Initialize and authenticate the selenium driver """
    options = Options()
    if os.getenv("CI"):
        options.headless = True
        options.add_argument("-headless")
        if pytestconfig.getoption("verbose") > 0:
            options.log.level = "trace"
    try:
        driver = WebDriver(firefox_options=options)
    except Exception as exc:
        print("Exception while initializing driver:", exc)
        raise

    driver.live_server_url = live_server.url

    # override get to help with url construction
    def get(self, partial_url):
        return self._get(live_server.url + partial_url)

    driver._get = driver.get
    driver.get = MethodType(get, driver)

    # grant permission and login the user
    user.user_permissions.add(Permission.objects.get(codename="change_client"))
    driver.get(reverse("admin:login"))
    username_input = driver.find_element_by_name("username")
    username_input.send_keys("user")
    password_input = driver.find_element_by_name("password")
    password_input.send_keys("test" + Keys.RETURN)
    WebDriverWait(driver, timeout=10).until(
        lambda x: x.find_element_by_css_selector(LOGGED_IN_CLIENT_SELECTOR)
    )

    return driver


def test_filter_is_usable(three_clients, selenium):
    """ Basic e2e sanity test """
    first_client = three_clients[0]
    selenium.get(reverse("admin:customers_client_changelist"))
    WebDriverWait(selenium, timeout=5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, CREATE_AFILTER_SELECTOR))
    )
    # the changelist table includes 3 rows of clients
    name_cells = selenium.find_elements_by_css_selector(CHANGELIST_FIELD_NAME)
    names = [cell.text for cell in name_cells]
    assert set(names) == set(client.first_name for client in three_clients)

    # the filters modal is hidden by default, but clicking it shows it
    assert not selenium.find_element_by_id(AFILTER_MODAL_ID).is_displayed()
    button = selenium.find_element_by_css_selector(CREATE_AFILTER_SELECTOR)
    button.click()
    WebDriverWait(selenium, timeout=5).until(
        EC.visibility_of_element_located((By.ID, AFILTER_MODAL_ID))
    )

    # fill in the title and select2 "name" value
    title_input = selenium.find_element_by_css_selector(FORM_TITLE_INPUT)
    assert title_input
    title_input.send_keys("my name filter")
    name_value = selenium.find_element_by_css_selector(FORM_ROW_VALUE)
    assert name_value.get_attribute("value") == ""

    # type a user's name autocompletes to the name
    select2_trigger = selenium.find_element_by_css_selector(FORM_SELECT2_CONTAINER)
    assert select2_trigger
    select2_trigger.click()
    select2_input = selenium.find_element_by_css_selector(FORM_SELECT2_INPUT)
    select2_input.send_keys(first_client.first_name + Keys.RETURN)
    assert name_value.get_attribute("value") == first_client.first_name

    # click save & filter to navigate to the filtered page
    save_and_filter = selenium.find_element_by_css_selector(SAVE_AND_FILTER)
    assert save_and_filter
    current_url = selenium.current_url
    save_and_filter.click()
    WebDriverWait(selenium, timeout=5).until(EC.url_changes(current_url))

    # assert filter was created and avialable in changelist filter list
    filters = selenium.find_element_by_id('changelist-filter')
    assert filters
    filter_heading = filters.find_element_by_xpath(FILTER_HEADING)
    advanced_filter_list = filters.find_element_by_xpath(FILTER_UL)
    filter_choices = advanced_filter_list.find_elements_by_css_selector("li > a")
    assert [choice.text for choice in filter_choices] == ["All", "my name filter"]

    # assert the change list is filtered by our filter's query
    name_cells = selenium.find_elements_by_css_selector(CHANGELIST_FIELD_NAME)
    names = [cell.text for cell in name_cells]
    assert set(names) == {first_client.first_name}
