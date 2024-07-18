"""Forms for batch recording matches."""

import datetime

from crispy_forms import layout, helper
from django import forms

from . import models, match_form, layouts


class CreateSparringDayForm(forms.Form):
    """Form for starting a match day."""

    season = forms.ModelChoiceField(
        queryset=models.Season.objects, disabled=True, widget=forms.HiddenInput()
    )
    date = match_form.DatePickerField(lang="de_CH", initial=datetime.datetime.now().date())

    def __init__(self, *args, season, **kwargs):
        super().__init__(*args, **kwargs)
        self.season = season
        self.helper = self.get_helper()

    def get_helper(self) -> helper.FormHelper:
        """Build the form helper."""
        season = models.Season.objects.get(pk=self.season)
        form_helper = helper.FormHelper()
        date_lang = self.fields["date"].lang
        form_helper.layout = layout.Layout(
            layouts.DatePickerLayout("date", date_lang=date_lang),
            layout.Div(
                layout.Submit("submit", "Save", css_class="btn btn-success"),
                layout.HTML(
                    f"<a href={season.get_absolute_url()} class='btn btn-danger'>Cancel</a>"
                ),
                css_class="mb-3",
            ),
        )
        return form_helper
