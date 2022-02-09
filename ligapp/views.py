"""Ligapp views."""
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView

from .forms import NewMatchForm
from .models import Match, Season


class SeasonListView(ListView):
    """Main view lists Seasons."""

    model = Season
    context_object_name = "all_seasons"


class SeasonDetailView(DetailView):
    """Display a season."""

    model = Season
    context_object_name = "season"


class MatchDetailView(DetailView):
    """Display a match."""

    model = Match
    context_object_name = "match"


class CreateSeasonView(CreateView):
    """Display the season creation form."""

    model = Season
    fields = "__all__"


class CreateMatchView(CreateView):
    """Automatic match creation view."""

    model = Match
    fields = ["first_player", "second_player", "date_played", "season"]

    def get_initial(self):
        initial = super().get_initial()
        initial["date_played"] = timezone.now()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial


class NewMatchView(FormView):
    """View for recording a new match with scores and all."""

    form_class = NewMatchForm
    template_name = "ligapp/new_match_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["date_played"] = timezone.now()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial
