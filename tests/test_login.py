"""Test steps for logging in after requesting the index page."""

from pytest_bdd import scenario, then, when  # noqa: I900 # dev requirement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import wait


@scenario("login.feature", "Try to access without logging in")
def test_nologin(): ...


@scenario("login.feature", "Login and access")
def test_login(): ...


@when("I try to access the index page")
def try_access_index(browser, index_page):
    browser.get(index_page)


@when("I log in")
def try_login(user_credentials, browser):
    username, password = user_credentials
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password + Keys.ENTER)
    wait.WebDriverWait(browser, 5).until(
        lambda b: b.find_element(By.TAG_NAME, "h2").text == "Running Seasons"
    )
    assert browser.find_element(By.TAG_NAME, "h2").text == "Running Seasons"


@then("I should be asked to login")
def see_login_page(browser):
    assert browser.find_element(By.CSS_SELECTOR, "input[value=login]")


@then("I should see the index page")
def see_index_page(browser):
    assert browser.find_element(By.TAG_NAME, "h2").text == "Running Seasons"
