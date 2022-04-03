"""Test steps for logging in after requesting the index page."""
from pytest_bdd import scenario, then, when  # noqa: I900 # dev requirement


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
def try_login(user_credentials, browser):
    username, password = user_credentials
    browser.fill("username", username)
    browser.fill("password", password)
    browser.find_by_css("input[value=login]").first.click()
    assert browser.find_by_text("Running Seasons")


@then("I should be asked to login")
def see_login_page(browser):
    assert browser.find_by_css("input[value=login]")


@then("I should see the index page")
def see_index_page(browser):
    assert browser.find_by_text("Running Seasons")
