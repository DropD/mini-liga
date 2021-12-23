"""Ligapp views."""
from django.views.generic import DetailView, ListView

from .models import Season


class SeasonListView(ListView):
    """Main view lists Seasons."""

    model = Season
    context_object_name = "all_seasons"


class SeasonDetailView(DetailView):
    """Display a season."""

    model = Season
    context_object_name = "season"
