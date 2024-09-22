"""Forms for the ligapp."""

from datetime import date, datetime
from typing import Any, Optional

import babel.dates
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms import layout  # noqa: I900 # comes from django-crispy-forms
from crispy_forms.helper import FormHelper  # noqa: I900
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_select2 import forms as s2forms

from .layouts import ConditionalScoresLayout, DatePickerLayout, SetScoresLayout
from .models import Match, Player, Season


class ScoreField(forms.IntegerField):
    """Integer field type with validators for max and min values."""

    default_validators = [
        validators.MaxValueValidator(90, message="Can not be larger than 90."),
        validators.MinValueValidator(0, message="Can not be below 0."),
    ]


class DatePickerField(forms.DateField):
    """Field for use with TempusDominus date picker."""

    def __init__(self, *args, lang: str, **kwargs):
        """Add the lang keyword for date localization."""
        super().__init__(*args, **kwargs)
        self.lang = lang

    def to_python(self, value: Optional[str]) -> Optional[date]:
        """Allow non-existent players to pass through."""
        if not isinstance(value, str):
            return value
        try:
            return babel.dates.parse_date(value, self.lang)
        except (babel.dates.ParseError, IndexError, ValueError):
            try:
                return datetime.fromisoformat(value)
            except ValueError as err:
                raise ValidationError(_("Invalid date."), code="invalid") from err


class BootstrapSelect2(s2forms.Select2Widget):
    """Bootstrap 5 themed version of the light Select2 widget."""

    theme = "bootstrap-5"

    def build_attrs(self, *args, **kwargs):
        """Fix the placeholder behaviour by passing the label manually."""
        attrs = super().build_attrs(*args, **kwargs)
        attrs["data-placeholder"] = self.label
        attrs["data-tags"] = str(self.tags).lower()
        return attrs

    def __init__(self, label="", *args, new_allowed=False, **kwargs):
        """Take in the label attribute for the placeholder."""
        self.label = label
        self.tags = new_allowed
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        """Dynamically update the media to include select2 bootstrap-5 theme."""
        return super().media + forms.Media(
            css={
                "screen": [
                    (
                        "//cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.2.0"
                        "/dist/select2-bootstrap-5-theme.min.css"
                    )
                ]
            }
        )


class ConditionalMixin:
    """Mixin for conditionally visible / required form field widgets."""

    def __init__(
        self,
        *,
        switch_field: str,
        switch_value: str,
        switch_show: bool = True,
        switch_required: bool = True,
    ):
        """Take in the required values for the switcher js class."""
        self.switch_field = switch_field
        self.switch_value = switch_value
        self.switch_show = switch_show
        self.switch_required = switch_required
        super().__init__()

    @property
    def media(self):
        """Add the local conditional switcher script."""
        return super().media + forms.Media(js=["ligapp/conditional.js"])

    def render(self, name, value, attrs=None, renderer=None):
        """Append the switcher setup script to the field widget html."""
        widget_html = super().render(name, value, attrs, renderer)
        switch_element = f"'id_{self.switch_field}'"
        conditional_element = f"'id_{name}'"
        return (
            widget_html
            + mark_safe(  # noqa: S308 ## safe because no user input involved
                "<script type='text/javascript'>"
                f"const {name}_switcher = new ConditionalFieldSwitcher("
                f"{conditional_element}, {switch_element}, '{self.switch_value}'"
                f", {str(self.switch_show).lower()}, {str(self.switch_required).lower()}"
                ");\n"
                f"register_switcher({name}_switcher);"
                "</script>"
            )
        )


class ConditionalNumberInput(ConditionalMixin, forms.NumberInput):
    """Conditionally visible / required number input widget."""

    ...


class NewMatchForm(forms.Form):
    """Form for recording a match."""

    season = forms.ModelChoiceField(
        queryset=Season.objects, disabled=True, widget=forms.HiddenInput()
    )
    first_player = forms.ModelChoiceField(
        queryset=Player.objects,
        label="",
        widget=BootstrapSelect2(label="First Player"),
    )
    second_player = forms.ModelChoiceField(
        queryset=Player.objects,
        label="",
        widget=BootstrapSelect2(label="Second Player"),
    )
    match_type = forms.ChoiceField(choices=Match.MatchType.choices, initial=Match.MatchType.SETS)
    minutes_played = forms.IntegerField(
        validators=[validators.MaxValueValidator(60)],
        required=False,
        widget=ConditionalNumberInput(switch_field="match_type", switch_value="Time"),
    )
    date_played = DatePickerField(lang="de_CH", initial=datetime.now().date())
    first_score_1 = ScoreField(label="Score")
    second_score_1 = ScoreField(label="Score")
    first_score_2 = ScoreField(label="Score", required=False)
    second_score_2 = ScoreField(label="Score", required=False)
    first_score_3 = ScoreField(label="Score", required=False)
    second_score_3 = ScoreField(label="Score", required=False)

    def __init__(self, *args, season, **kwargs):
        """Add the helper instance attr."""
        super().__init__(*args, **kwargs)
        self.season = season
        self.fields["first_player"].queryset = Player.objects.filter(season=season)
        self.fields["second_player"].queryset = Player.objects.filter(season=season)
        self.helper = self.get_helper()

    def get_helper(self) -> FormHelper:
        """Get the form helper."""
        season = Season.objects.get(pk=self.season)
        helper = FormHelper()
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
                FloatingField("minutes_played", css_class="match-input"),
                DatePickerLayout("date_played", css_class="match-input", date_lang=date_lang),
            ),
            layout.Fieldset(
                "",
                SetScoresLayout("first_score_1", "second_score_1"),
                ConditionalScoresLayout(
                    "first_score_2",
                    "second_score_2",
                    css_id="set-2",
                    switch_name="match_type",
                    switch_value="Points",
                ),
                ConditionalScoresLayout(
                    "first_score_3",
                    "second_score_3",
                    css_id="set-3",
                    switch_name="match_type",
                    switch_value="Points",
                ),
            ),
            layout.Div(
                layout.Submit("submit", "Save", css_class="btn btn-success"),
                layout.HTML(
                    f"<a href={season.get_absolute_url()} class='btn btn-danger'>Cancel</a>"
                ),
                css_class="mb-3",
            ),
        )
        return helper

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        self.validate_players_different(cleaned_data)
        self.validate_players_in_season(cleaned_data)
        self.validate_scores(cleaned_data)
        return cleaned_data

    def validate_players_different(self, cleaned_data: dict[str, Any]) -> None:
        if "first_player" and "second_player" in cleaned_data:
            first = cleaned_data["first_player"]
            second = cleaned_data["second_player"]
            if first == second:
                self.add_error(
                    "second_player",
                    ValidationError(_("Can not be the same as the first player."), code="invalid"),
                )

    def validate_players_in_season(self, cleaned_data: dict[str, Any]) -> None:
        season = cleaned_data.get("season")
        if not season:
            return None
        for player_field in ["first_player", "second_player"]:
            player = cleaned_data.get(player_field)
            if player and player not in season.participants.all():
                self.add_error(
                    player_field,
                    ValidationError(_("Is not a participant in this season."), code="invalid"),
                )

    def validate_scores(self, cleaned_data: dict[str, Any]) -> None:
        scores = [
            (
                cleaned_data.get(f"first_score_{i}"),
                cleaned_data.get(f"second_score_{i}"),
            )
            for i in range(1, 4)
        ]
        match_type = cleaned_data.get("match_type")
        if match_type == Match.MatchType.SETS:
            for i, score_set in enumerate(scores):
                self._validate_set_complete(score_set, i + 1)
                self._validate_set_is_regulation(score_set, i + 1)

    def _validate_set_complete(
        self, score_set: tuple[Optional[int], Optional[int]], set_nr: int
    ) -> None:
        scores_added = [i is not None for i in score_set]
        message = _("Incomplete set.")
        if any(scores_added):
            if not scores_added[0]:
                self.add_error(f"first_score_{set_nr}", ValidationError(message, code="required"))
            if not scores_added[1]:
                self.add_error(f"second_score_{set_nr}", ValidationError(message, code="required"))

    def _validate_set_is_regulation(
        self, score_set: tuple[Optional[int], Optional[int]], set_nr: int
    ) -> None:
        """
        Validate scoring rules.

        Currently, regulation only means there are no draws.
        More rigorous rules should be added in a customizable way on the season record.
        """
        scores_added = [i is not None for i in score_set]
        message = _("Scores in set must be different.")
        if any(scores_added):
            if score_set[0] == score_set[1]:
                self.add_error(f"first_score_{set_nr}", ValidationError(message, code="invalid"))
                self.add_error(f"second_score_{set_nr}", ValidationError(message, code="invalid"))


class NewPlayerMatchForm(NewMatchForm):
    """Same as NewMatchForm, except the first player is fixed."""

    def __init__(self, *args, **kwargs):
        """Add the helper instance attr."""
        super().__init__(*args, **kwargs)
        self.fields["first_player"].disabled = True


class NewPlannedMatchForm(forms.Form):
    """Create a new planned match."""

    season = forms.ModelChoiceField(
        queryset=Season.objects, disabled=True, widget=forms.HiddenInput()
    )
    first_player = forms.ModelChoiceField(
        queryset=Player.objects,
        label="",
        widget=BootstrapSelect2(label="First Player"),
    )
    second_player = forms.ModelChoiceField(
        queryset=Player.objects,
        label="",
        widget=BootstrapSelect2(label="Second Player"),
    )
    match_type = forms.ChoiceField(choices=Match.MatchType.choices, initial=Match.MatchType.SETS)
    minutes_played = forms.IntegerField(
        validators=[validators.MaxValueValidator(60)],
        required=False,
        widget=ConditionalNumberInput(switch_field="match_type", switch_value="Time"),
    )
    date_planned = DatePickerField(lang="de_CH", initial=datetime.now().date())

    def __init__(self, *args, season, **kwargs):
        """Add the helper instance attr."""
        super().__init__(*args, **kwargs)
        self.season = season
        self.fields["first_player"].queryset = Player.objects.filter(season=season)
        self.fields["second_player"].queryset = Player.objects.filter(season=season)
        self.helper = self.get_helper()

    def get_helper(self) -> FormHelper:
        """Get the form helper."""
        season = Season.objects.get(pk=self.season)
        helper = FormHelper()
        date_lang = self.fields["date_planned"].lang
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
                FloatingField("minutes_played", css_class="match-input"),
                DatePickerLayout("date_planned", css_class="match-input", date_lang=date_lang),
            ),
            layout.Div(
                layout.Submit("submit", "Save", css_class="btn btn-success"),
                layout.HTML(
                    f"<a href={season.get_absolute_url()} class='btn btn-danger'>Cancel</a>"
                ),
                css_class="mb-3",
            ),
        )
        return helper
