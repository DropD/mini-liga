import pytest
from django.utils import timezone

from ligapp import models, stats
from ligapp.match_builder import MatchBuilder


@pytest.mark.django_db
def test_head2head(season, season_admin, player, other_player):
    season.add_player(player)
    season.add_player(other_player)
    MatchBuilder(
        season=season,
        match_type=models.MultiSetMatch,
        first_player=player,
        second_player=other_player,
    ).add_score(21, 15).add_score(7, 21).add_score(21, 19).build()

    other_season = models.Season(name="Other Season", start_date=timezone.now())
    other_season.save()
    other_season.add_player(other_player)
    other_season.add_player(player)

    head_to_head = stats.Head2Head(player, other_player, season_admin)
    assert head_to_head.season_stats == [(season, 1, 2)]
    assert head_to_head.stats == [
        ("Matches", [(1, 100), (0, 0)]),
        ("Sets", [(2, 2.0 / 3.0 * 100.0), (1, 1.0 / 3.0 * 100.0)]),
        ("Points", [(49, 49.0 / 104.0 * 100.0), (55, 55.0 / 104 * 100.0)]),
    ]


@pytest.mark.django_db
def test_head2head_nodata(player, other_player, season_admin):
    head_to_head = stats.Head2Head(player, other_player, season_admin)
    assert not head_to_head.season_stats
    assert head_to_head.stats == [
        ("Matches", [(0,), (0,)]),
        ("Sets", [(0,), (0,)]),
        ("Points", [(0,), (0,)]),
    ]
