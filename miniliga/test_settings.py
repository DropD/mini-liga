"""Test settings."""
from .settings import *  # noqa: F403  # we want all the settings

DATABASES["default"]["NAME"] = "db.tests"  # noqa: F405  # overriding from settings
