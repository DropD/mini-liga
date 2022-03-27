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
def test_season_add_player(season, player, other_player):
    """Test that adding a player also adds a rank and history."""
    season.add_player(player)
    assert season.ranks.get(player=player).rank == 1
    assert season.histories.get(player=player).history[0]["rank"] == 1
    season.add_player(other_player)
    assert season.ranks.get(player=other_player).rank == 2
    assert season.histories.get(player=other_player).history[0]["rank"] == 2


@pytest.mark.django_db
def test_season_create_player(season):
    """Test that creating a new player also adds rank and history."""
    ananas = season.create_player(name="Anders Antonsen")
    assert season.ranks.get(player=ananas).rank == 1
    assert season.histories.get(player=ananas).history[0]["rank"] == 1


@pytest.mark.django_db
def test_season_rank_up_player(season, player):
    """Test that promoting a player makes the right adjustments and only those."""
    season.add_player(player)
    ananas = season.create_player(name="Anders Antonsen")
    lohky = season.create_player(name="Loh Kean Yew")
    lasen = season.create_player(name="Lakshya Sen")
    ctc = season.create_player(name="Chou Tien Chen")
    assert list(season.ranks.values_list("rank", "player__name")) == [
        (1, player.name),
        (2, ananas.name),
        (3, lohky.name),
        (4, lasen.name),
        (5, ctc.name),
    ]
    season.update_rank(lasen, 2)
    assert list(season.ranks.values_list("rank", "player__name")) == [
        (1, player.name),
        (2, lasen.name),
        (3, ananas.name),
        (4, lohky.name),
        (5, ctc.name),
    ]
    assert [i["rank"] for i in player.histories.get(season=season).history] == [1]
    assert [i["rank"] for i in lasen.histories.get(season=season).history] == [4, 2]
    assert [i["rank"] for i in ananas.histories.get(season=season).history] == [2, 3]
    assert [i["rank"] for i in lohky.histories.get(season=season).history] == [3, 4]
    assert [i["rank"] for i in ctc.histories.get(season=season).history] == [5]


@pytest.mark.django_db
def test_timed_match_str(timed_match, get_sets):
    """Test the string representation of a TimedMatch object."""
    assert (
        str(timed_match) == "2000-01-02 (10 minutes): Test Player vs Other Player; --"
    )
    get_sets(timed_match)[0].save()
    assert (
        str(timed_match)
        == "2000-01-02 (10 minutes): Test Player vs Other Player; 17 : 9"
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
    """Test the ``winner`` property of a objects in different cases."""
    sets = get_sets(sets_match)
    assert sets[0].winner == player
    assert sets[1].winner == other_player
    assert models.Set(first_score=6, second_score=6, match=sets_match).winner is None
