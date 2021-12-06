"""Admin model registration."""
from django.contrib import admin

from .models import Match, MultiSetMatch, Participant, Season, Set, TimedMatch

admin.site.register(Season)
admin.site.register(Participant)
admin.site.register(Match)
admin.site.register(TimedMatch)
admin.site.register(Set)


class SetInline(admin.TabularInline):
    """Inline admin editor for sets."""

    model = Set


@admin.register(MultiSetMatch)
class MultiSetMatchAdmin(admin.ModelAdmin):
    """Admin editor for multi set matches."""

    inlines = [SetInline]
