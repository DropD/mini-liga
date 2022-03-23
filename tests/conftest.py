"""Fixtures & stuff for behavioral tests."""
import pytest  # noqa: I900
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone

from ligapp.models import Player, Season  # noqa: I900 # the app is not a requirement ;)


@pytest.fixture
def index_page(live_server):
    """Provide the root url of the site."""
    yield live_server.url


@pytest.fixture
def user_credentials():
    """Provide user credentials for logging in."""
    yield "testuser", "test the pw"


@pytest.fixture
def season_name():
    """Provide the name of the test season."""
    yield "Test Season"


@pytest.fixture
def user(user_credentials):
    """Provide the user instance for authentication."""
    username, password = user_credentials
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create(username=username, password=make_password(password))
    yield user


@pytest.fixture
def season(season_name):
    """Provide a test season instance."""
    season = Season.objects.get_or_create(name=season_name, start_date=timezone.now())[
        0
    ]
    victor = Player.objects.get_or_create(name="Victor")[0]
    kento = Player.objects.get_or_create(name="Kento")[0]
    season.add_player(victor)
    season.add_player(kento)
    yield season


@pytest.fixture
def user_is_seasonadmin(season, user):
    """Make the test user admin of the test season."""
    season.admins.add(user)


@pytest.fixture
def authbrowser(browser, client, index_page, user, django_db_serialized_rollback):
    """Provide a pre-authenticated browser."""
    client.force_login(user)
    cookie = client.cookies["sessionid"]
    browser.visit(index_page)
    browser.cookies.add({cookie.key: cookie.value})
    browser.visit(index_page)
    yield browser
