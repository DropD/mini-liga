"""Ligapp views."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import NewMatchForm, NewPlayerMatchForm
from .match_builder import MatchBuilder
from .models import Match, Player, Season


class SeasonListView(LoginRequiredMixin, ListView):
    """Main view lists Seasons."""

    login_url = "/accounts/login"
    model = Season
    context_object_name = "all_seasons"


class SeasonDetailView(LoginRequiredMixin, DetailView):
    """Display a season."""

    model = Season
    context_object_name = "season"


class MatchDetailView(LoginRequiredMixin, DetailView):
    """Display a match."""

    model = Match
    context_object_name = "match"


class CreateSeasonView(LoginRequiredMixin, CreateView):
    """Display the season creation form."""

    model = Season
    fields = "__all__"


class CreateMatchView(LoginRequiredMixin, CreateView):
    """Automatic match creation view."""

    model = Match
    fields = ["first_player", "second_player", "date_played", "season"]

    def get_initial(self):
        """Get initial data to prefill the form."""
        initial = super().get_initial()
        initial["date_played"] = timezone.now().date()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial


class NewMatchView(UserPassesTestMixin, SingleObjectMixin, FormView):
    """View for recording a new match with scores and all."""

    form_class = NewMatchForm
    template_name = "ligapp/new_match_form.html"
    model = Season
    pk_url_kwarg = "season"
    context_object_name = "season"

    def test_func(self):
        """Make sure the user should be allowed to see this view."""
        is_season_admin = self.request.user.season_admin_for.contains(self.get_object())
        is_staff = self.request.user.is_staff
        is_superuser = self.request.user.is_superuser
        return is_season_admin or is_staff or is_superuser

    def get_form_kwargs(self):
        """Pass the season url parameter on to the form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({"season": self.kwargs["season"]})
        return form_kwargs

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def get_initial(self):
        """Get initial data to prefill the form."""
        initial = super().get_initial()
        initial["date_played"] = timezone.now().date()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial

    def form_valid(self, form):
        """Create and save the right objects if the form was submitted in a valid state."""
        data = form.cleaned_data
        kwargs = {
            k: v
            for k, v in data.items()
            if k in ["season", "date_played", "first_player", "second_player"]
        }
        match_builder = MatchBuilder(**kwargs).set_type_from_enum_value(
            data["match_type"]
        )
        for i in range(1, 4):
            match_builder.add_score(data[f"first_score_{i}"], data[f"second_score_{i}"])
        match_builder.build()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("ligapp:season-detail", kwargs={"pk": self.kwargs["season"]})


class NewPlayerMatchView(NewMatchView):
    """View for recording a new match as a player."""

    form_class = NewPlayerMatchForm

    def test_func(self):
        """Make sure the user is a player in the season."""
        season = self.get_object()
        player = Player.objects.get(pk=self.kwargs["player"])
        print(str(player))
        user_player = self.request.user.player
        print(str(user_player))
        print(season.participants.all())
        print(season.participants.contains(user_player))
        return season.participants.contains(user_player) and user_player == player

    def get_initial(self):
        """Prefill the first player additionally."""
        initial = super().get_initial()
        initial["first_player"] = self.request.user.player
        return initial
