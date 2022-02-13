"""Template tags for commonly used bootstrap components."""
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(name="accordion-button-props")
def accordion_button_props(target: str, classes: str = ""):
    """Generate html properties for an accordion button element."""
    props_str = (
        'class="accordion-button {classes}" '
        'type="button" data-bs-toggle="collapse" '
        'data-bs-target="#{target}" '
        'aria-expanded="true" aria-controls="{target}"'
    )
    return format_html(props_str, classes=classes, target=target)


@register.simple_tag(name="accordion-body-props")
def accordion_body_props(tagid: str, classes: str = "", show: bool = True):
    """Generate html properties for an accordion-body element."""
    show_str = "show" if show else ""
    props_str = (
        'id="{tagid}" class="accordion-body accordion-collapse collapse {show} {classes}"'
        "aria-labelledby={tagid}"
    )
    return format_html(props_str, tagid=tagid, classes=classes, show=show_str)
