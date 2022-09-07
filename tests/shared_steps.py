"""Shared steps for behavioral tests."""
from pytest_bdd import given, then  # noqa: I900  # dev requirements
from selenium.webdriver.common.by import By


@given("I am logged in on the season list", target_fixture="logged_in_on_season_list")
def logged_in(
    authbrowser,
    index_page,
):
    """Ensure logged in and on seasons list."""
    authbrowser.get(index_page)
    assert authbrowser.find_element(By.TAG_NAME, "h2").text == "Running Seasons"


@given(
    "I am logged in on the season list as nonadmin",
    target_fixture="logged_in_on_sl_nonadmin",
)
def logged_in_nonadmin(
    nonadmin_authbrowser,
    index_page,
):
    """Ensure logged in and on seasons list."""
    nonadmin_authbrowser.get(index_page)
    assert (
        nonadmin_authbrowser.find_element(By.TAG_NAME, "h2").text == "Running Seasons"
    )


@given("I am logged in on the season detail view")
def on_season_detail(authbrowser, index_page):
    """Visit the season detail page as season admin."""
    authbrowser.get(index_page + "/season/1")


@given("I am logged in on the season detail view as nonadmin")
def on_season_detail_nonadmin(nonadmin_authbrowser, index_page):
    """Visit season detail page as non-season admin."""
    nonadmin_authbrowser.get(index_page + "/season/1")


@given("I am season admin for the test season")
def am_season_admin():
    """Nothing to do."""
    ...


@then("I should be redirected to the season detail page")
def redirected_to_season(
    season_name,
    authbrowser,
):
    """Ensure on season detail page."""
    assert authbrowser.find_element(By.TAG_NAME, "h1").text == season_name
