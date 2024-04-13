"""Ligapp models."""

import datetime
from typing import Any, Optional

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _


class Player(models.Model):
    """A participant in the league."""

    name = models.CharField(max_length=80, unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        """Options for the player model."""

        verbose_name = "player"
        verbose_name_plural = "players"
        ordering = ["name"]

    def __str__(self) -> str:
        """Represent participant as a string."""
        return self.name


class Season(models.Model):
    """A league season."""

    name = models.CharField(max_length=80)
    start_date = models.DateTimeField("start date")
    end_date = models.DateTimeField("end date", null=True, blank=True)
    participants = models.ManyToManyField(Player, blank=True)
    admins = models.ManyToManyField(User, related_name="season_admin_for", blank=True)

    class Meta:
        """Options for the Season model."""

        verbose_name = "season"
        verbose_name_plural = "seasons"

    def __str__(self) -> str:
        """Represent seaon as a string."""
        return self.name

    def get_absolute_url(self):
        """Absolute URL for the model object."""
        return reverse("ligapp:season-detail", kwargs={"pk": self.pk})

    def add_player(self, player: Player):
        """Add a player, starting at the bottom of the ranking."""
        with transaction.atomic():
            self.participants.add(player)
            self.ranks.create(season=self, player=player, rank=self.next_free_rank)

    def create_player(self, **kwargs) -> Player:
        """Create a new player, adding them to the season."""
        player = None
        with transaction.atomic():
            player = self.participants.create(**kwargs)
            self.ranks.create(season=self, player=player, rank=self.next_free_rank)

        return player

    def update_rank(self, player: Player, new_position: int):
        """Update a player's rank and everything that follows."""
        current_rank, _ = self.ranks.get_or_create(
            player=player, defaults={"season": self, "rank": self.next_free_rank}
        )
        old_position = current_rank.rank
        if old_position == new_position:
            return None
        step = 1 if old_position < new_position else -1
        affected_ranks = self.ranks.filter(
            rank__in=range(old_position + step, new_position + step, step)
        )
        with transaction.atomic():
            for rank in affected_ranks:
                rank.update(rank.rank - step)
            current_rank.update(new_position)

    @property
    def next_free_rank(self) -> int:
        """Calculate what rank the next added player would start at."""
        return self.ranks.last().rank + 1 if self.ranks.last() else 1

    @property
    def end_date_str(self) -> str:
        """Stringify the end date."""
        return str(self.end_date or "open")

    def matches_by_date(
        self, queryset=None, n_matches: Optional[int] = None
    ) -> list[tuple[datetime.date, list["Match"]]]:
        if queryset is None:
            queryset = self.matches
        if not queryset:
            return []
        last_n_matches = queryset.order_by("-date_played")[:n_matches]

        def add_match(matches_by_date, match):
            display_date = match.date_played or match.date_planned or timezone.now()
            matches_by_date.setdefault(display_date.date(), []).append(match)

        def group_matches(matches):
            result = {}
            for match in matches:
                add_match(result, match)
            return result

        return group_matches(last_n_matches).items()

    @property
    def latest_matches(self) -> list[tuple[datetime.date, list["Match"]]]:
        return self.matches_by_date(self.matches.filter(completed=True), 10)

    @property
    def match_history(self) -> list[tuple[datetime.date, list["Match"]]]:
        return self.matches_by_date(self.matches.filter(completed=True))

    @property
    def top_16(self) -> list[tuple[datetime.date, list["Match"]]]:
        return self.ranks.all()[:16]

    @property
    def planned_matches(self) -> list[tuple[datetime.date, list["Match"]]]:
        planned_matches = self.matches.filter(completed=False)
        return self.matches_by_date(queryset=planned_matches)


class Rank(models.Model):
    """A rank of a player in a season."""

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="ranks")
    player = models.ForeignKey(Player, on_delete=models.RESTRICT, related_name="ranks")
    rank = models.PositiveSmallIntegerField()

    class Meta:
        """Rank settings."""

        verbose_name = "player rank"
        verbose_name_plural = "player ranks"
        unique_together = [["season", "player"]]
        ordering = ["season", "rank"]

    def __str__(self) -> str:
        """Stringify rank object."""
        return f"{self.season.name} | {self.rank}. {self.player.name}"

    def save(self, *args, **kwargs):
        """Update the ranking history when saving."""
        with transaction.atomic():
            history, created = self.season.histories.get_or_create(
                player=self.player,
                defaults={
                    "season": self.season,
                    "history": ranking_history_entry(self.rank),
                },
            )
            if not created:
                history.history.extend(ranking_history_entry(self.rank))
                history.save()
            return super().save(*args, **kwargs)

    def update(self, new_position):
        """Update the ranking position."""
        self.rank = new_position
        self.save()


def ranking_history_entry(rank: int = -1):
    """Build a ranking history entry."""
    return [{"timestamp": str(timezone.now()), "rank": rank}]


class RankingHistory(models.Model):
    """History of a player's rank in a season."""

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="histories"
    )
    player = models.ForeignKey(
        Player, on_delete=models.RESTRICT, related_name="histories"
    )
    history = models.JSONField(default=ranking_history_entry)

    class Meta:
        """RankingHistory settings."""

        verbose_name = "ranking history"
        verbose_name_plural = "ranking histories"

    def __str__(self) -> str:
        """Stringify ranking history object."""
        return f"Ranking History | {self.season.name} | {self.player.name}"


class Match(models.Model):
    """A match between two participants."""

    date_played = models.DateTimeField("date played", null=True, blank=True)
    date_planned = models.DateTimeField("date planned", null=True, blank=True)
    completed = models.BooleanField(default=True)
    first_player = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="matches_first"
    )
    second_player = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="matches_second"
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )

    class Meta:
        """Options for the match model."""

        verbose_name = "match"
        verbose_name_plural = "matches"
        ordering = ["date_played"]

    class MatchType(models.TextChoices):
        """Enum for match type choices."""

        SETS = "Points"
        TIME = "Time"

    class NotInSeasonError(Exception):
        """Error for trying to save a match with one or more players not in the season."""

    class NoScoresError(Exception):
        """Error for trying to save a match with a season but no scores."""

    def __str__(self) -> str:
        """Represent match as a string."""
        return "{date}{minutes}: {first} vs {second}; {score}".format(
            date=self.date_played.date() if self.date_played else "pending",
            minutes=self.minutes_played_str,
            first=self.first_player,
            second=self.second_player,
            score=self.score_str,
        )

    def get_absolute_url(self):
        """Get url to view this match."""
        return reverse("ligapp:match-detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        super().clean()
        if self.completed and self.date_played is None:
            raise ValidationError(
                _(
                    "The date when the match was played must be set for complete matches!"
                )
            )
        if self.completed and not self.sets.all():
            raise ValidationError(_("A completed match must have scores."))
        if self.date_played and not self.completed:
            raise ValidationError(
                _(
                    "To record the time when a match was played,"
                    " it must also be set to completed state!"
                )
            )
        if self.first_player == self.second_player:
            raise ValidationError(_("Must have two different players!"))

    @property
    def score_str(self) -> str:
        """Represent all possible score states (including no scores)."""
        return ", ".join(str(set) for set in self.sets.all()) or "--"

    @property
    def minutes_played_str(self) -> str:
        """Represent duration of the match (empty except for ``TimedMatch``)."""
        return ""

    @property
    def child(self) -> Any:
        """Handle to the derived database record if accessed through ``Match``."""
        return getattr(self, "multisetmatch", getattr(self, "timedmatch", self))

    @property
    def match_type(self) -> str:
        if isinstance(self.child, TimedMatch):
            return self.MatchType.TIME
        elif isinstance(self.child, MultiSetMatch):
            return self.MatchType.SETS
        raise TypeError("Invalid match type!")


class TimedMatch(Match):
    """A match played for time, not points."""

    minutes_played = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60)]
    )

    class Meta:
        """Options for the timed match model."""

        verbose_name = "match for time"
        verbose_name_plural = "matches for time"

    @property
    def minutes_played_str(self) -> str:
        """Represent the match duration."""
        return f" ({self.minutes_played} minutes)"

    @property
    def winner(self) -> Optional[Player]:
        """Find the player who won more points or None in case of a draw."""
        score = self.sets.first()
        if score:
            return score.winner
        return None


class MultiSetMatch(Match):
    """A match played over multiple sets."""

    class Meta:
        """Options for the multi set match model."""

        verbose_name = "match for points"
        verbose_name_plural = "matches for points"

    @property
    def winner(self) -> Optional[Player]:
        """Find the player who won more sets or None in case of a draw."""
        set_winners = [s.winner for s in self.sets.all()]
        first_sets_won = set_winners.count(self.first_player)
        second_sets_won = set_winners.count(self.second_player)
        if first_sets_won > second_sets_won:
            return self.first_player
        elif first_sets_won < second_sets_won:
            return self.second_player
        return None

    @property
    def minutes_played_str(self) -> str:
        """Represent the match duration (always empty)."""
        return ""


class Set(models.Model):
    """A set (game)."""

    first_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    second_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    match = models.ForeignKey(Match, related_name="sets", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])

    class Meta:
        """Options for the set model."""

        ordering = ["order"]
        verbose_name = "set of points"
        verbose_name_plural = "sets of points"

    def __str__(self) -> str:
        """Represent a set as a string."""
        return f"{self.first_score} : {self.second_score}"

    @property
    def winner(self) -> Optional[Player]:
        """Find the player who won this set or None in case of a draw."""
        if self.first_score > self.second_score:
            return self.match.first_player
        elif self.first_score < self.second_score:
            return self.match.second_player
        return None
