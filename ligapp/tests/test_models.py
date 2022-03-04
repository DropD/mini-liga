"""
Test custom models code.

Such as custom properties, string representations etc. DO NOT TEST ordinary django provided model functionality.
"""
import pytest
from django.utils import timezone
from pytest_cases import parametrize_with_cases

from ligapp import models

from .cases_models import SetsMatchStrs, SetsMatchWinners


@pytest.mark.django_db
def test_player_str(player):
    """Test the string representation of a Player object."""
    assert str(player) == "Test Player"


@pytest.mark.django_db
def test_season_str(season):
    """Test the string representation of a Season object."""
    assert str(season) == "Test Season"


@pytest.mark.django_db
def test_season_end_date_str(season):
    """Test the end_date_str property of a Season object."""
    assert season.end_date_str == "open"
    now = timezone.now()
    season.end_date = now
    assert season.end_date_str == str(now)


@pytest.mark.django_db
def test_timed_match_str(timed_match, get_sets):
    """Test the string representation of a TimedMatch object."""
    assert str(timed_match) == "2000-01-02 (10 min): Test Player vs Other Player; --"
    get_sets(timed_match)[0].save()
    assert (
        str(timed_match) == "2000-01-02 (10 min): Test Player vs Other Player; 17 : 9"
    )


@pytest.mark.django_db
def test_timed_match_winner(timed_match, get_sets):
    """Test the ``winner`` property of a TimedMatch object."""
    assert timed_match.winner is None
    get_sets(timed_match)[0].save()
    assert timed_match.winner == timed_match.first_player


@parametrize_with_cases("setup, ref", cases=SetsMatchStrs)
@pytest.mark.django_db
def test_multisetmatch_str(sets_match, get_sets, setup, ref):
    """Test the string representation of a MultiSetMatch object."""
    setup(get_sets(sets_match))
    assert str(sets_match) == ref


@parametrize_with_cases("setup, ref", cases=SetsMatchWinners)
@pytest.mark.django_db
def test_multisetmatch_winner(sets_match, get_sets, setup, ref):
    """Test the ``winner`` property of a MultiSetMatch object in different cases."""
    setup(get_sets(sets_match))
    assert sets_match.winner == ref(sets_match)


@pytest.mark.django_db
def test_set_str(sets_match, get_sets):
    """Test the string representation of a Set object."""
    set_0 = get_sets(sets_match)[0]
    assert str(set_0) == "17 : 9"


@pytest.mark.django_db
def test_set_winner(sets_match, get_sets, player, other_player):
    "Test the ``winner`` property of a objects in different cases."
    sets = get_sets(sets_match)
    assert sets[0].winner == player
    assert sets[1].winner == other_player
    assert models.Set(first_score=6, second_score=6, match=sets_match).winner is None
