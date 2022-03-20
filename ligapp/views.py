"""Ligapp views."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import NewMatchForm, NewPlayerMatchForm
from .models import Match, MultiSetMatch, Player, Season, Set


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
        match = MultiSetMatch(
            season=data["season"],
            date_played=data["date_played"],
            first_player=data["first_player"],
            second_player=data["second_player"],
        )
        match.save()
        Set(
            first_score=data["first_score_1"],
            second_score=data["second_score_1"],
            match=match,
            order=1,
        ).save()
        if data["first_score_2"]:
            Set(
                first_score=data["first_score_2"],
                second_score=data["second_score_2"],
                match=match,
                order=2,
            ).save()
            if data["first_score_3"]:
                Set(
                    first_score=data["first_score_3"],
                    second_score=data["second_score_3"],
                    match=match,
                    order=3,
                ).save()
        match.refresh_from_db()
        if match.winner:
            first_rank = match.first_player.ranks.get(season=match.season).rank
            second_rank = match.second_player.ranks.get(season=match.season).rank
            if match.winner.pk == match.first_player.pk and first_rank > second_rank:
                match.season.update_rank(match.first_player, second_rank)
            elif match.winner == match.second_player and second_rank > first_rank:
                match.season.update_rank(match.second_player, first_rank)
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
