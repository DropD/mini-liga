"""Forms for the ligapp."""
from django import forms
from django.db.models import TextChoices

from .models import Player


class MatchType(TextChoices):
    """Enum for match type choices."""

    SETS = "Points"
    TIME = "Time"


class NewMatchForm(forms.Form):
    """Form for recording a match."""

    first_player = forms.ModelChoiceField(queryset=Player.objects)
    second_player = forms.ModelChoiceField(queryset=Player.objects)
    match_type = forms.ChoiceField(choices=MatchType.choices, initial=MatchType.SETS)
    date_played = forms.SplitDateTimeField()
    first_score_1 = forms.IntegerField()
    second_score_1 = forms.IntegerField()
    first_score_2 = forms.IntegerField(required=False)
    second_score_2 = forms.IntegerField(required=False)
    first_score_3 = forms.IntegerField(required=False)
    second_score_3 = forms.IntegerField(required=False)
