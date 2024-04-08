"""Test settings."""

import os

from .settings import *  # noqa: F403  # we want all the settings

DATABASES["default"]["NAME"] = os.environ.get(  # noqa: F405  # overriding from settings
    "MINILIGA_BROWSER_TEST_DB", "db.tests"
)
