"""Custom form layouts."""

import json
from typing import Optional

from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms import layout  # noqa: I900 # comes from django-crispy-forms
from django.utils.safestring import mark_safe


class ConditionalMixin:
    """Layout for a field shown or hidden based on the state of a choice field."""

    conditional_id = ""
    switch_id = ""
    switch_value = ""

    def gen_script(self) -> str:
        name = self.conditional_id.replace("-", "_") + "_switcher"
        return mark_safe(  # noqa: S308 ## safe because no user input involved
            "<script type='text/javascript'>"
            f"const {name} = new ConditionalFieldSwitcher("
            f"'{self.conditional_id}', '{self.switch_id}', '{self.switch_value}', true, false"
            ");"
            f"register_switcher({name});"
            "</script>"
        )

    class Media:
        """Load the local conditional switcher script."""

        js = {"screen": ["ligapp/conditional.js"]}


class DatePickerLayout(layout.Layout):
    """Layout for a date input with js for date picker widget."""

    def __init__(
        self,
        name: str,
        *args,
        css_class: Optional[str] = None,
        date_lang: str = "de_CH",
        **kwargs,
    ):
        """Add a floating field and a script html tag."""
        self.name = name
        self.date_lang = date_lang.replace("_", "-").lower()
        super().__init__(
            FloatingField(name, css_class=css_class, id=f"{name}_picker"),
            layout.HTML(self._gen_script()),
            *args,
            **kwargs,
        )

    def _gen_config(self) -> str:
        return json.dumps(
            {
                "container": f"document.querySelector('div#div_id_{self.name}')",
                "localization": {"locale": f"'{self.date_lang}'"},
                "display": {
                    "components": {
                        "date": True,
                        "decades": True,
                        "month": True,
                        "year": True,
                        "hours": False,
                        "minutes": False,
                        "seconds": False,
                    }
                },
            }
        ).replace('"', "")

    def _gen_script(self) -> str:
        element = f"document.getElementById('{self.name}_picker')"
        config = self._gen_config()
        return mark_safe(  # noqa: S308 ## safe because no user input involved
            "<script type='text/javascript'>"
            f"const {self.name}_datepicker = new tempusDominus.TempusDominus({element}, {config})"
            "</script>"
        )


class SetScoresLayout(layout.Layout):
    """Layout for scores of both players for a set of play."""

    def __init__(self, name_left: str, name_right: str, *args, **kwargs):
        """Create a bootstrap 5 row / col layout with <score> : <score>."""
        super().__init__(
            layout.Row(
                layout.Div(
                    FloatingField(
                        name_left,
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                layout.HTML("<div class='col score-vs'>:</div>"),
                layout.Div(
                    FloatingField(
                        name_right,
                        label="Score",
                        css_class="match-input score-input",
                    ),
                    css_class="col",
                ),
                *args,
                css_class="row g-0 match-input",
                **kwargs,
            ),
        )


class ConditionalScoresLayout(ConditionalMixin, SetScoresLayout):
    """ScoresLayout that only appears when another form field has the right value."""

    def __init__(
        self,
        *args,
        css_id: str,
        switch_name: str,
        switch_value: str,
        **kwargs,
    ):
        """Set the attributes required for ConditionalMixin."""
        self.conditional_id = css_id
        self.switch_id = f"id_{switch_name}"
        self.switch_value = switch_value
        super().__init__(
            *args,
            **kwargs,
            css_id=css_id,
        )

    def render(self, *args, **kwargs):
        return super().render(*args, **kwargs) + self.gen_script()
