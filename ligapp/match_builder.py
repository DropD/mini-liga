"""Builder for a match with all the additional tasks."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Type, Union

from django.db import transaction
from django.utils import timezone

from . import forms, models


@dataclass
class MatchBuilder:
    """Build a match with all additional tasks taken care of."""

    season: Optional[models.Season] = None
    date_played: datetime = field(default_factory=timezone.now)
    first_player: Optional[models.Player] = None
    second_player: Optional[models.Player] = None
    match_type: Union[
        Type[models.MultiSetMatch], Type[models.TimedMatch]
    ] = models.MultiSetMatch
    minutes_played: Optional[int] = None
    scores: list[models.Set] = field(default_factory=list)

    def set_season(self, season: models.Season) -> "MatchBuilder":
        self.season = season
        return self

    def set_first_player(self, player: models.Player) -> "MatchBuilder":
        self.first_player = player
        return self

    def set_second_player(self, player: models.Player) -> "MatchBuilder":
        self.second_player = player
        return self

    def make_multiset(self) -> "MatchBuilder":
        self.match_type = models.MultiSetMatch
        return self

    def make_timed(self) -> "MatchBuilder":
        self.match_type = models.TimedMatch
        return self

    def set_type_from_enum_value(self, choice) -> "MatchBuilder":
        if choice == forms.MatchType.SETS:
            self.make_multiset()
        elif choice == forms.MatchType.TIME:
            self.make_timed()
        return self

    def set_minutes_played(self, duration: int) -> "MatchBuilder":
        self.minutes_played = duration
        return self

    def add_set(self, score_set: models.Set) -> "MatchBuilder":
        self.scores.append(score_set)
        return self

    def add_score(self, first: int, second: int) -> "MatchBuilder":
        if any([first, second]):
            self.scores.append(models.Set(first_score=first, second_score=second))
        return self

    def set_date_played(self, date: datetime) -> "MatchBuilder":
        self.date_played = date
        return self

    def build(self, create_related: bool = False) -> models.Match:
        with transaction.atomic():
            self._save_if_necessary(self.season, allowed=create_related)
            self._save_if_necessary(self.first_player, allowed=create_related)
            self._save_if_necessary(self.second_player, allowed=create_related)
            match = self.match_type(
                season=self.season,
                date_played=self.date_played,
                first_player=self.first_player,
                second_player=self.second_player,
            )
            if self.match_type is models.TimedMatch:
                match.minutes_played = self.minutes_played
            match.save()
            for index, score_set in enumerate(self.scores):
                score_set.match = match
                score_set.order = index + 1
                score_set.save()
            self._update_ranking_if_necessary(match)
            return match

    def _save_if_necessary(self, instance, allowed: bool = False):
        if (
            instance
            and not instance.__class__.objects.contains(self.season)
            and allowed
        ):
            instance.save()

    def _update_ranking_if_necessary(self, match):
        match.refresh_from_db()
        ranks = [
            self.first_player.ranks.get(season=self.season).rank,
            self.second_player.ranks.get(season=self.season).rank,
        ]
        lower_ranked_player = (
            self.first_player if ranks[0] > ranks[1] else self.second_player
        )
        if match.winner == lower_ranked_player:
            self.season.update_rank(lower_ranked_player, min(ranks))
