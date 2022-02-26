"""Ligapp models."""
from typing import Optional, Union

from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse


class Player(models.Model):
    """A participant in the league."""

    name = models.CharField(max_length=80)

    class Meta:
        """Options for the player model."""

        ordering = ["name"]

    def __str__(self) -> str:
        """Represent participant as a string."""
        return self.name


class Season(models.Model):
    """A league season."""

    name = models.CharField(max_length=80)
    start_date = models.DateTimeField("start date")
    end_date = models.DateTimeField("end date", null=True)
    participants = models.ManyToManyField(Player)

    def __str__(self) -> str:
        """Represent seaon as a string."""
        return self.name

    def get_absolute_url(self):
        return reverse("ligapp:season-detail", kwargs={"pk": self.pk})

    @property
    def end_date_str(self):
        return str(self.end_date or "open")


class Match(models.Model):
    """A match between two participants."""

    date_played = models.DateTimeField("date played")
    first_player = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="matches_first"
    )
    second_player = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="matches_second"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="matches", null=True
    )

    class Meta:
        """Options for the match model."""

        verbose_name_plural = "Matches"
        ordering = ["date_played"]

    def __str__(self) -> str:
        """Represent match as a string."""
        return f"{self.date_played}: {self.first_player} vs {self.second_player}; {self.score_str}"

    def get_absolute_url(self):
        return reverse("ligapp:match-detail", kwargs={"pk": self.pk})

    @property
    def score_str(self) -> str:
        return ", ".join(str(set) for set in self.sets.all())

    @property
    def minutes_played_str(self) -> str:
        timedmatch = getattr(self, "timedmatch", None)
        if timedmatch:
            return timedmatch.minutes_played_str
        return ""

    @property
    def child(self) -> Union["TimedMatch", "MultiSetMatch"]:
        return getattr(self, "multisetmatch", getattr(self, "timedmatch", self))


class TimedMatch(Match):
    """A match played for time, not points."""

    minutes_played = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60)]
    )

    class Meta:
        """Options for the timed match model."""

        verbose_name_plural = "TimedMatches"

    def __str__(self) -> str:
        """Represent a timed match as a string."""
        return (
            f"{self.date_played} ({self.minutes_played_str}): "
            f"{self.first_player} vs {self.second_player}; "
            f"{self.sets.first()}"
        )

    @property
    def minutes_played_str(self) -> str:
        return f"{self.minutes_played} min"

    @property
    def winner(self) -> Optional[Player]:
        """Find the player who won more points or None in case of a draw."""
        score = self.sets.first()
        return score.winner


class MultiSetMatch(Match):
    """A match played over multiple sets."""

    class Meta:
        """Options for the multi set match model."""

        verbose_name_plural = "MultiSetMatches"

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


class Set(models.Model):
    """A set (game)."""

    first_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    second_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    match = models.ForeignKey(Match, related_name="sets", on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])

    class Meta:
        """Options for the set model."""

        ordering = ["order"]

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
