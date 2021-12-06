"""Ligapp models."""
from django.core.validators import MaxValueValidator
from django.db import models


class Participant(models.Model):
    """A participant in the league."""

    name = models.CharField(max_length=80)

    def __str__(self):
        """Represent participant as a string."""
        return self.name


class Season(models.Model):
    """A league season."""

    name = models.CharField(max_length=80)
    start_date = models.DateTimeField("start date")
    participants = models.ManyToManyField(Participant)

    def __str__(self):
        """Represent seaon as a string."""
        return self.name


class Match(models.Model):
    """A match between two participants."""

    date_played = models.DateTimeField("date played")
    first_player = models.ForeignKey(
        Participant, on_delete=models.PROTECT, related_name="matches_first"
    )
    second_player = models.ForeignKey(
        Participant, on_delete=models.PROTECT, related_name="matches_second"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="matches", null=True
    )

    class Meta:
        """Options for the match model."""

        verbose_name_plural = "Matches"

    def __str__(self):
        """Represent match as a string."""
        sets = ", ".join(str(set) for set in self.sets.all())
        return (
            f"{self.date_played}: {self.first_player} vs {self.second_player}; {sets}"
        )


class TimedMatch(Match):
    """A match played for time, not points."""

    minutes_played = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(60)]
    )

    class Meta:
        """Options for the timed match model."""

        verbose_name_plural = "TimedMatches"

    def __str__(self):
        """Represent a timed match as a string."""
        return (
            f"{self.date_played}: "
            f"{self.first_player} vs {self.second_player}; "
            "{self.sets.first()}"
        )


class MultiSetMatch(Match):
    """A match played over multiple sets."""

    class Meta:
        """Options for the multi set match model."""

        verbose_name_plural = "MultiSetMatches"


class Set(models.Model):
    """A set (game)."""

    first_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    second_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(90)])
    match = models.ForeignKey(Match, related_name="sets", on_delete=models.CASCADE)

    def __str__(self):
        """Represent a set as a string."""
        return f"{self.first_score} : {self.second_score}"
