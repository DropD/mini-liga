"""Ligapp apps."""

from django.apps import AppConfig


class LigappConfig(AppConfig):
    """Config for Ligapp."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ligapp"
