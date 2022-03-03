"""
Provide fixtures for model objects.

Tests using these need to request the database with pytest.mark.django_db.
"""
from datetime import datetime

import pytest
from django.utils import timezone

from ligapp import models


@pytest.fixture
def player():
    """Provide a player object."""
    player = models.Player(name="Test Player")
    player.save()
    yield player


@pytest.fixture
def other_player():
    """Provide a second player object for when an opponent is needed."""
    player = models.Player(name="Other Player")
    player.save()
    yield player


@pytest.fixture
def season(player):
    """Provide a season object."""
    season = models.Season(name="Test Season", start_date=timezone.now())
    season.save()
    season.participants.add(player)
    yield season


@pytest.fixture
def timed_match(season, player, other_player):
    """Provide a TimedMatch object."""
    match = models.TimedMatch(
        date_played=timezone.make_aware(datetime(2000, 1, 2)),
        minutes_played=10,
        first_player=player,
        second_player=other_player,
        season=season,
    )
    match.save()
    yield match


@pytest.fixture
def sets_match(season, player, other_player):
    """Provide a MultiSetMatch object."""
    match = models.MultiSetMatch(
        date_played=timezone.make_aware(datetime(2000, 1, 2)),
        first_player=player,
        second_player=other_player,
        season=season,
    )
    match.save()
    yield match


@pytest.fixture
def get_sets():
    """Provide a function which creates three sets for a given Match object."""

    def sets_(match):
        return (
            models.Set(first_score=17, second_score=9, match=match, order=1),
            models.Set(first_score=17, second_score=21, match=match, order=2),
            models.Set(first_score=14, second_score=19, match=match, order=3),
        )

    yield sets_
