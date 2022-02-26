"""Forms for the ligapp."""
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import TextChoices
from django.utils.translation import gettext as _

from .models import Player, Season


class MatchType(TextChoices):
    """Enum for match type choices."""

    SETS = "Points"
    TIME = "Time"


class ScoreField(forms.IntegerField):
    """Integer field type with validators for max and min values."""

    default_validators = [
        validators.MaxValueValidator(30, message="Can not be larger than 30."),
        validators.MinValueValidator(0, message="Can not be below 0."),
    ]


class NewMatchForm(forms.Form):
    """Form for recording a match."""

    season = forms.ModelChoiceField(
        queryset=Season.objects, disabled=True, widget=forms.HiddenInput()
    )
    first_player = forms.ModelChoiceField(queryset=Player.objects)
    second_player = forms.ModelChoiceField(queryset=Player.objects)
    match_type = forms.ChoiceField(choices=MatchType.choices, initial=MatchType.SETS)
    date_played = forms.DateTimeField()
    first_score_1 = ScoreField()
    second_score_1 = ScoreField()
    first_score_2 = ScoreField(required=False)
    second_score_2 = ScoreField(required=False)
    first_score_3 = ScoreField(required=False)
    second_score_3 = ScoreField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        self.validate_players_different(cleaned_data)
        self.validate_players_in_season(cleaned_data)
        return cleaned_data

    def validate_players_different(self, cleaned_data):
        if "first_player" and "second_player" in cleaned_data:
            first = cleaned_data["first_player"]
            second = cleaned_data["second_player"]
            if first == second:
                self.add_error(
                    "second_player",
                    ValidationError(
                        _("Can not be the same as the first player."), code="invalid"
                    ),
                )

    def validate_players_in_season(self, cleaned_data):
        season = cleaned_data.get("season")
        if not season:
            return None
        for player_field in ["first_player", "second_player"]:
            player = cleaned_data.get(player_field)
            if player and player not in season.participants.all():
                self.add_error(
                    player_field,
                    ValidationError(
                        _("Is not a participant in this season."), code="invalid"
                    ),
                )
