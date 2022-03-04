import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from ligapp.forms import MatchType, NewMatchForm
from ligapp.views import NewMatchView

from .model_fixtures import other_player, player, season


@pytest.fixture
def new_match_view(season, player):
    view = NewMatchView()
    view.kwargs = {"season": season.pk}


@pytest.mark.django_db
def test_valid(season, player, other_player):
    season.participants.add(player)
    season.participants.add(other_player)
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season.pk,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": str(timezone.now().date()),
            "first_score_1": 30,
            "second_score_1": 29,
        },
    )
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_empty(season):
    form = NewMatchForm(data={}, season=season.pk)
    assert not form.is_valid()
    assert set(form.errors.keys()) == {
        "season",
        "first_player",
        "second_player",
        "match_type",
        "date_played",
        "first_score_1",
        "second_score_1",
    }


@pytest.mark.django_db
def test_invalid_scores(season, player, other_player):
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": str(timezone.now()),
            "first_score_1": 31,
            "second_score_1": -11,
        },
    )
    assert not form.is_valid()
    assert form.errors["first_score_1"] == ["Can not be larger than 30."]
    assert form.errors["second_score_1"] == ["Can not be below 0."]


@pytest.mark.django_db
def test_invalid_draw(season, player, other_player):
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": str(timezone.now()),
            "first_score_1": 11,
            "second_score_1": 11,
        },
    )
    assert not form.is_valid()
    assert form.errors["first_score_1"] == ["Scores in set must be different."]
    assert form.errors["second_score_1"] == ["Scores in set must be different."]


@pytest.mark.django_db
def test_incomplete_set(season, player, other_player):
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": str(timezone.now()),
            "first_score_1": 11,
            "second_score_1": 11,
            "first_score_2": 11,
        },
    )
    assert not form.is_valid()
    assert form.errors["second_score_2"] == ["Incomplete set."]


@pytest.mark.django_db
def test_player_vs_self(season, player):
    season.participants.add(player)
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season,
            "first_player": player,
            "second_player": player,
            "match_type": MatchType.SETS,
            "date_played": timezone.now(),
            "first_score_1": 21,
            "second_score_1": 11,
        },
    )
    assert not form.is_valid()
    assert form.errors["second_player"] == ["Can not be the same as the first player."]


@pytest.mark.django_db
def test_nonseason_player(season, player, other_player):
    season.participants.add(player)
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": timezone.now(),
            "first_score_1": 21,
            "second_score_1": 11,
        },
    )
    assert not form.is_valid()
    assert form.errors["second_player"][0].startswith("Select a valid choice.")


@pytest.mark.django_db
def test_view_valid(season, player, other_player):
    season.participants.add(player)
    season.participants.add(other_player)
    client = Client()
    response = client.get(reverse("ligapp:new-match", kwargs={"season": season.pk}))
    view = NewMatchView(request=response.wsgi_request, kwargs={"season": season.pk})
    form = NewMatchForm(
        season=season.pk,
        initial={"season": season},
        data={
            "season": season.pk,
            "first_player": player,
            "second_player": other_player,
            "match_type": MatchType.SETS,
            "date_played": str(timezone.now().date()),
            "first_score_1": 30,
            "second_score_1": 29,
        },
    )
    form.full_clean()
    assert form.is_valid(), form.errors
    view.form_valid(form)
    match = season.matches.get(first_player=player, second_player=other_player)
    assert match
    assert match.sets.first().first_score == 30
