"""Fixtures & stuff for behavioral tests."""
import pytest  # noqa: I900
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import wait

from .shared_steps import *  # noqa: F401,F403 # this is required for shared steps


@pytest.fixture()
def browser():
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.close()


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
    browser.get(index_page)
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password + Keys.ENTER)
    wait.WebDriverWait(browser, 5).until(
        lambda b: b.find_element(By.TAG_NAME, "h2").text == "Running Seasons"
    )
    yield browser


@pytest.fixture
def nonadmin_authbrowser(browser, index_page, nonadmin_credentials):
    username, password = nonadmin_credentials
    browser.get(index_page)
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password + Keys.ENTER)
    wait.WebDriverWait(browser, 5).until(
        lambda b: b.find_element(By.TAG_NAME, "h2").text == "Running Seasons"
    )
    yield browser
