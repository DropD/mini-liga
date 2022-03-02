"""Forms for the ligapp."""
from datetime import datetime

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms import layout  # noqa: I900 # comes from django-crispy-forms
from crispy_forms.helper import FormHelper  # noqa: I900
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import TextChoices
from django.utils.formats import get_format
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


class DatePickerField(forms.DateField):
    """Field for use with TempusDominus date picker."""

    def __init__(self, *args, lang, **kwargs):
        """Add the lang keyword for date localization."""
        super().__init__(*args, **kwargs)
        self.lang = lang

    def to_python(self, value):
        for format in get_format("DATE_INPUT_FORMATS", self.lang):
            try:
                return datetime.strptime(value, format).date()
            except ValueError:
                continue
        raise ValidationError(_("Invalid date."), code="invalid")


class NewMatchForm(forms.Form):
    """Form for recording a match."""

    season = forms.ModelChoiceField(
        queryset=Season.objects, disabled=True, widget=forms.HiddenInput()
    )
    first_player = forms.ModelChoiceField(
        queryset=Player.objects, empty_label="Select a Player"
    )
    second_player = forms.ModelChoiceField(
        queryset=Player.objects, empty_label="Select a Player"
    )
    match_type = forms.ChoiceField(choices=MatchType.choices, initial=MatchType.SETS)
    date_played = DatePickerField(lang="de-ch")
    first_score_1 = ScoreField(label="Score", localize=True)
    second_score_1 = ScoreField(label="Score", localize=True)
    first_score_2 = ScoreField(label="Score", required=False, localize=True)
    second_score_2 = ScoreField(label="Score", required=False, localize=True)
    first_score_3 = ScoreField(label="Score", required=False, localize=True)
    second_score_3 = ScoreField(label="Score", required=False, localize=True)

    def __init__(self, *args, **kwargs):
        """Add the helper instance attr."""
        super().__init__(*args, **kwargs)
        self.helper = self.get_helper()

    def clean(self):
        cleaned_data = super().clean()
        self.validate_players_different(cleaned_data)
        self.validate_players_in_season(cleaned_data)
        self.validate_scores(cleaned_data)
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

    def validate_scores(self, cleaned_data):
        scores = [
            (
                cleaned_data.get(f"first_score_{i}"),
                cleaned_data.get(f"second_score_{i}"),
            )
            for i in range(1, 4)
        ]
        match_type = cleaned_data.get("match_type")
        if match_type == MatchType.SETS.value:
            for i, score_set in enumerate(scores):
                self._validate_set_complete(score_set, i + 1)
                self._validate_set_is_regulation(score_set, i + 1)

    def _validate_set_complete(self, score_set, set_nr):
        scores_added = [i is not None for i in score_set]
        message = _("Can not be empty if the other player has a score in this set.")
        if any(scores_added):
            if not scores_added[0]:
                self.add_error(
                    f"first_score_{set_nr}", ValidationError(message, code="required")
                )
            if not scores_added[1]:
                self.add_error(
                    f"second_score_{set_nr}", ValidationError(message, code="required")
                )

    def _validate_set_is_regulation(self, score_set, set_nr):
        """
        Validate scoring rules.

        Currently, regulation only means there are no draws.
        More rigorous rules should be added in a customizable way on the season record.
        """
        scores_added = [i is not None for i in score_set]
        message = _("Can not be the same as the other player's score in this set.")
        if any(scores_added):
            if score_set[0] == score_set[1]:
                self.add_error(
                    f"first_score_{set_nr}", ValidationError(message, code="invalid")
                )
                self.add_error(
                    f"second_score_{set_nr}", ValidationError(message, code="invalid")
                )

    def get_helper(self):
        helper = FormHelper()
        helper.add_input(layout.Submit("submit", "Save", css_class="btn btn-success"))
        helper.add_input(layout.Button("cancel", "Cancel", css_class="btn btn-danger"))
        date_lang = self.fields["date_played"].lang
        helper.layout = layout.Layout(
            layout.Fieldset(
                "",
                FloatingField("first_player", css_class="match-input"),
                layout.HTML("<div class='match-input player-vs'>vs.</div>"),
                FloatingField("second_player", css_class="match-input"),
            ),
            layout.Fieldset(
                "",
                FloatingField("match_type", css_class="match-input"),
                FloatingField(
                    "date_played", css_class="match-input", id="dateplayedpicker"
                ),
                layout.HTML(
                    "<script type='text/javascript'>"
                    "const datepicker = new tempusDominus.TempusDominus("
                    "document.getElementById('div_id_date_played'), "
                    f"{{localization: {{locale: '{date_lang}' }}, "
                    "display: {components: {date: true, decades: true, month: true, "
                    "year: true, hours: false, minutes: false, seconds: false}}}"
                    ");"
                    "</script>"
                ),
            ),
            layout.Fieldset(
                "",
                layout.Div(
                    FloatingField(
                        "first_score_1",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                layout.HTML("<div class='col score-vs'>:</div>"),
                layout.Div(
                    FloatingField(
                        "second_score_1",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                css_class="row g-0 match-input",
            ),
            layout.Fieldset(
                "",
                layout.Div(
                    FloatingField(
                        "first_score_2",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                layout.HTML("<div class='col score-vs'>:</div>"),
                layout.Div(
                    FloatingField(
                        "second_score_2",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                css_class="row g-0 match-input",
            ),
            layout.Fieldset(
                "",
                layout.Div(
                    FloatingField(
                        "first_score_3",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                layout.HTML("<div class='col score-vs'>:</div>"),
                layout.Div(
                    FloatingField(
                        "second_score_3",
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                css_class="row g-0 match-input",
            ),
        )
        return helper
