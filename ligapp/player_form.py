"""Ligapp form for adding an existing or new player to a season."""

from crispy_forms import layout  # noqa: I900 # comes from django-crispy-forms
from crispy_forms.helper import FormHelper  # noqa: I900
from django import forms
from django.core.exceptions import ValidationError

from .match_form import BootstrapSelect2
from .models import Player, Season


class NewOrExistingModelChoiceField(forms.ModelChoiceField):
    """Extended model choice field that can deal with new instances."""

    def to_python(self, value):
        try:
            value = super().to_python(value)
        except ValidationError as err:
            try:
                value = self.queryset.model(**{self.to_field_name: value})
            except (ValueError, TypeError):
                raise err from err
        return value


class AddPlayerForm(forms.Form):
    """Form for adding a player to a season."""

    season = forms.ModelChoiceField(
        queryset=Season.objects, disabled=True, widget=forms.HiddenInput
    )
    name = NewOrExistingModelChoiceField(
        queryset=Player.objects,
        label="",
        to_field_name="name",
        widget=BootstrapSelect2(label="Select a Player or make a new one", new_allowed=True),
    )

    def __init__(self, *args, season, user, **kwargs):
        """Exclude already added players from the queryset."""
        super().__init__(*args, **kwargs)
        self.season = season
        self.fields["name"].queryset = (
            Player.objects.filter(season__in=user.season_admin_for.all())
            .exclude(season=season)
            .distinct()
        )
        self.helper = self.get_helper()

    def get_helper(self) -> FormHelper:
        season = Season.objects.get(pk=self.season)
        helper = FormHelper()
        helper.layout = layout.Layout(
            layout.Div("name", css_class="mb-3"),
            layout.Div(
                layout.Submit("submit", "Save", css_class="btn btn-success"),
                layout.HTML(
                    f"<a href={season.get_absolute_url()} class='btn btn-danger'>Cancel</a>"
                ),
                css_class="mb-3",
            ),
        )
        return helper
