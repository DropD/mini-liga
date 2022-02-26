import pytest
from django.utils import timezone

from .model_fixtures import player, season


@pytest.mark.django_db
def test_str(season):
    assert str(season) == "Test Season"


@pytest.mark.django_db
def test_end_date_str(season):
    assert season.end_date_str == "open"
    now = timezone.now()
    season.end_date = now
    assert season.end_date_str == str(now)
