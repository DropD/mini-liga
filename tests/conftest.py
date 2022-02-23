"""Database fixture setup for behavioral tests."""
import pytest  # noqa: I900 # pytest is a dev requirement
from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "ligapp/fixtures/examples.yaml")
