"""Fixtures & stuff for behavioral tests."""
import pytest  # noqa: I900

from .shared_steps import *  # noqa: F401,F403 # this is required for shared steps


@pytest.fixture
def index_page():
    """Provide the root url of the site."""
    yield "http://localhost:8001"


@pytest.fixture
def user_credentials():
    """Provide user credentials for logging in."""
    yield "testuser", "test the pw"


@pytest.fixture
def nonadmin_credentials():
    """Provide user credentials for logging in."""
    yield "testuser2", "test the pw"


@pytest.fixture
def season_name():
    """Provide the name of the test season."""
    yield "Test Season"


@pytest.fixture
def authbrowser(browser, index_page, user_credentials):
    """Provide a pre-authenticated browser."""
    username, password = user_credentials
    browser.visit(index_page)
    browser.fill("username", username)
    browser.fill("password", password)
    browser.find_by_css("input[value=login]").first.click()
    yield browser


@pytest.fixture
def nonadmin_authbrowser(browser, index_page, nonadmin_credentials):
    username, password = nonadmin_credentials
    browser.visit(index_page)
    browser.fill("username", username)
    browser.fill("password", password)
    browser.find_by_css("input[value=login]").first.click()
    yield browser
