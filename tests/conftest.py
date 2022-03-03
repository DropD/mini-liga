"""Fixtures & stuff for behavioral tests."""
import os

import pytest  # noqa: I900


@pytest.fixture
def index_page():
    yield "http://127.0.0.1:8000/"


@pytest.fixture
def user_credentials():
    yield os.environ["TESTUSER_NAME"], os.environ["TESTUSER_PW"]
