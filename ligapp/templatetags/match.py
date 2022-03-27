"""Template tags for rendering match information."""
from typing import Any, Dict

from django import template
from django.db.models.manager import Manager

from ..models import Match

register = template.Library()


@register.inclusion_tag("match_item.html", takes_context=True)
def match_item(context: Dict[str, Any], match: Match) -> Dict[str, Any]:
    """Render the match_item template given a Match instance."""
    any_timed_matches = context.get("any_timed_matches", True)
    return {"match": match, "any_timed_matches": any_timed_matches}


@register.inclusion_tag("match_list.html")
def match_list(
    matches: Manager, tag_id: str = "matches", classes: str = ""
) -> Dict[str, Any]:
    """Render a list of matches."""
    any_timed_matches = any(m.child.minutes_played_str for m in matches.all())
    return {
        "any_timed_matches": any_timed_matches,
        "matches": matches.all(),
        "tag_id": tag_id,
        "add_classes": classes,
    }
