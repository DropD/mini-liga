"""Test steps for logging in after requesting the index page."""
import pytest  # noqa: I900 # dev requirement
from pytest_bdd import scenario, then, when  # noqa: I900 # dev requirement


@pytest.fixture
def index_page():
    yield "http://127.0.0.1:8000/"


@pytest.fixture
def user_credentials():
    yield "testuser", "test the pw"


@scenario("login.feature", "Try to access without logging in")
def test_nologin():
    ...


@scenario("login.feature", "Login and access")
def test_login():
    ...


@when("I try to access the index page")
def try_access_index(browser, index_page):
    browser.visit(index_page)


@when("I log in")
def try_login(browser, user_credentials):
    username, password = user_credentials
    browser.fill("username", username)
    browser.fill("password", password)
    browser.find_by_css("input[value=login]").first.click()


@then("I should be asked to login")
def see_login_page(browser):
    assert browser.find_by_css("input[value=login]")


@then("I should see the index page")
def see_index_page(browser):
    assert browser.find_by_text("Running Seasons")
