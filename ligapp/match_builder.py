"""Builder for a match with all the additional tasks."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Type, Union

from django.db import transaction
from django.utils import timezone

from . import models


@dataclass
class MatchBuilder:
    """Build a match with all additional tasks taken care of."""

    season: Optional[models.Season] = None
    date_played: Optional[datetime] = None
    date_planned: Optional[datetime] = None
    completed = True
    first_player: Optional[models.Player] = None
    second_player: Optional[models.Player] = None
    match_type: Union[
        Type[models.MultiSetMatch], Type[models.TimedMatch]
    ] = models.MultiSetMatch
    minutes_played: Optional[int] = None
    scores: list[models.Set] = field(default_factory=list)

    def set_season(self, season: models.Season) -> "MatchBuilder":
        """Set the season field."""
        self.season = season
        return self

    def set_first_player(self, player: models.Player) -> "MatchBuilder":
        """Set the first player field."""
        self.first_player = player
        return self

    def set_second_player(self, player: models.Player) -> "MatchBuilder":
        """Set the second player field."""
        self.second_player = player
        return self

    def make_multiset(self) -> "MatchBuilder":
        """Create a MultiSetMatch."""
        self.match_type = models.MultiSetMatch
        return self

    def make_timed(self) -> "MatchBuilder":
        """Create a TimedMatch."""
        self.match_type = models.TimedMatch
        return self

    def set_type_from_enum_value(self, choice) -> "MatchBuilder":
        """Set the match type from the form field value."""
        if choice == models.Match.MatchType.SETS:
            self.make_multiset()
        elif choice == models.Match.MatchType.TIME:
            self.make_timed()
        return self

    def set_minutes_played(self, duration: int) -> "MatchBuilder":
        """Set the minutes played field (TimedMatch only)."""
        self.minutes_played = duration
        return self

    def add_set(self, score_set: models.Set) -> "MatchBuilder":
        """Add a score set model instance."""
        self.scores.append(score_set)
        return self

    def add_score(self, first: int, second: int) -> "MatchBuilder":
        """Add a score set from just score values."""
        if any([first, second]):
            self.scores.append(models.Set(first_score=first, second_score=second))
        return self

    def set_date_played(self, date: datetime) -> "MatchBuilder":
        """Set the date played field."""
        self.date_played = date
        return self

    def set_date_planned(self, date: datetime) -> "MatchBuilder":
        """Set the date played field."""
        self.date_planned = date
        return self

    def set_completed(self, completed: bool) -> "MatchBuilder":
        self.completed = completed
        return self

    def build(self, create_related: bool = False) -> models.Match:
        """Build a match instance, save it and update the ranking."""
        with transaction.atomic():
            self._save_if_necessary(self.season, allowed=create_related)
            self._save_if_necessary(self.first_player, allowed=create_related)
            self._save_if_necessary(self.second_player, allowed=create_related)
            match = self.match_type(
                season=self.season,
                date_played=self.date_played,
                first_player=self.first_player,
                second_player=self.second_player,
                completed=self.completed,
            )
            if self.match_type is models.TimedMatch:
                match.minutes_played = self.minutes_played
            match.save()
            self._create_scores(match)
            self._update_ranking_if_necessary(match)
            return match

    def plan(self, create_related: bool = False) -> models.Match:
        """Build a planned match instance and save it."""
        with transaction.atomic():
            self._save_if_necessary(self.season, allowed=create_related)
            self._save_if_necessary(self.first_player, allowed=create_related)
            self._save_if_necessary(self.second_player, allowed=create_related)
            match = self.match_type(
                completed=False,
                season=self.season,
                date_played=None,
                date_planned=self.date_planned,
                first_player=self.first_player,
                second_player=self.second_player,
            )
            if self.match_type is models.TimedMatch:
                match.minutes_played = self.minutes_played
            match.save()
            return match

    def complete(self, match) -> models.Match:
        """Add missing information to a planned match instance and set it to completed."""
        if self.match_type is not type(match):
            self.season = match.season
            self.date_planned = match.date_planned
            self.completed = True
            new_match = self.build()
            match.delete()
            return new_match
        match.first_player = self.first_player
        match.second_player = self.second_player
        match.date_played = self.date_played or timezone.now()
        match.completed = True
        with transaction.atomic():
            match.save()
            self._create_scores(match)
            self._update_ranking_if_necessary(match)
        return match

    def _create_scores(self, match):
        """Create score sets for a given match."""
        for index, score_set in enumerate(self.scores):
            score_set.match = match
            score_set.order = index + 1
            score_set.save()

    def _save_if_necessary(self, instance, allowed: bool = False):
        """Save a related model instance if necessary and allowed."""
        if instance and not instance.__class__.objects.contains(instance) and allowed:
            instance.save()

    def _update_ranking_if_necessary(self, match):
        """Check and update the ranking if necessary."""
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
