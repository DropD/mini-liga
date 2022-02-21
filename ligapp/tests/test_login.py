from pytest_bdd import given, scenario, then, when


@scenario("login.feature", "Try to access without logging in")
def test_nologin():
    ...


@scenario("login.feature", "Login and access")
def test_login():
    ...


@given("I'm not logged in")
def not_logged_in(auth):
    auth["user"] = None


@when("I try to access the index page")
def try_access_index(browser):
    browser.visit("/")


@when("I log in")
def try_login(browser):
    browser.find_by_css("input[value=login]").first.click()


@then("I should be asked to login")
def see_login_page(browser):
    assert browser.find_by_css("input[value=login]")


@then("I should see the index page")
def see_index_page(browser):
    assert browser.find_by_text("Running Seasons")
