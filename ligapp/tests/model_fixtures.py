"""
Provide fixtures for model objects.

Tests using these need to request the database with pytest.mark.django_db.
"""

from datetime import datetime

import pytest
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
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
    yield season


@pytest.fixture
def two_player_season(season, player, other_player):
    season.add_player(player)
    season.add_player(other_player)
    yield season


@pytest.fixture
def timed_match(two_player_season, player, other_player):
    """Provide a TimedMatch object."""
    match = models.TimedMatch(
        date_played=timezone.make_aware(datetime(2000, 1, 2)),
        minutes_played=10,
        first_player=player,
        second_player=other_player,
        season=two_player_season,
    )
    match.save()
    yield match


@pytest.fixture
def sets_match(two_player_season, player, other_player):
    """Provide a MultiSetMatch object."""
    match = models.MultiSetMatch(
        date_played=timezone.make_aware(datetime(2000, 1, 2)),
        first_player=player,
        second_player=other_player,
        season=two_player_season,
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


@pytest.fixture
def season_admin(season):
    """Provide a user instance which is allowed to change the test season."""
    user = User.objects.get_or_create(
        username="seasonadmin", password=make_password("season admin password")
    )[0]
    season.admins.add(user)
    yield user
