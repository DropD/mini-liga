import pytest
from django.utils import timezone

from ligapp import models


@pytest.fixture
def player():
    player = models.Player(name="Test Player")
    player.save()
    yield player


@pytest.fixture
def other_player():
    player = models.Player(name="Other Player")
    player.save()
    yield player


@pytest.fixture
def season(player):
    season = models.Season(name="Test Season", start_date=timezone.now())
    season.save()
    season.participants.add(player)
    yield season
