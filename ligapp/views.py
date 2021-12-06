"""Ligapp views."""
from django.views.generic import ListView

from .models import Season


class SeasonListView(ListView):
    """Main view lists Seasons."""

    model = Season
    context_object_name = "all_seasons"
