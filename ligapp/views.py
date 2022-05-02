"""Ligapp views."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from .match_builder import MatchBuilder
from .match_form import NewMatchForm, NewPlannedMatchForm, NewPlayerMatchForm
from .models import Match, Player, Season
from .player_form import AddPlayerForm


class SeasonListView(LoginRequiredMixin, ListView):
    """Main view lists Seasons."""

    login_url = "/accounts/login"
    model = Season
    context_object_name = "all_seasons"


class SeasonDetailView(LoginRequiredMixin, DetailView):
    """Display a season."""

    model = Season
    context_object_name = "season"


class SeasonRankingView(LoginRequiredMixin, DetailView):
    """Display the full ranking of the season."""

    model = Season
    template_name = "ligapp/season_ranking.html"
    context_object_name = "season"


class SeasonMatchHistoryView(LoginRequiredMixin, DetailView):
    """Display the full match history of the season."""

    model = Season
    template_name = "ligapp/season_match_history.html"
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
        """Inject the season object into the template context."""
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
            if k
            in [
                "season",
                "date_played",
                "first_player",
                "second_player",
                "minutes_played",
            ]
        }
        match_builder = MatchBuilder(**kwargs).set_type_from_enum_value(
            data["match_type"]
        )
        for i in range(1, 4):
            match_builder.add_score(data[f"first_score_{i}"], data[f"second_score_{i}"])
        match_builder.build()
        return super().form_valid(form)

    def get_success_url(self):
        """URL to redirect to on success."""
        return reverse("ligapp:season-detail", kwargs={"pk": self.kwargs["season"]})


class NewPlannedMatchView(UserPassesTestMixin, SingleObjectMixin, FormView):
    """View for planning a match."""

    form_class = NewPlannedMatchForm
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
        """Inject the season object into the template context."""
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def get_initial(self):
        """Get initial data to prefill the form."""
        initial = super().get_initial()
        initial["date_planned"] = timezone.now().date()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial

    def form_valid(self, form):
        """Create and save the right objects if the form was submitted in a valid state."""
        data = form.cleaned_data
        kwargs = {k: v for k, v in data.items()}
        match_type = kwargs.pop("match_type")
        match_builder = MatchBuilder(**kwargs).set_type_from_enum_value(match_type)
        match_builder.plan()
        return super().form_valid(form)

    def get_success_url(self):
        """URL to redirect to on success."""
        return reverse("ligapp:season-detail", kwargs={"pk": self.kwargs["season"]})


class CompletePlannedMatchView(UserPassesTestMixin, SingleObjectMixin, FormView):
    """View for recording the result of a planned match."""

    form_class = NewMatchForm
    template_name = "ligapp/new_match_form.html"
    model = Match
    pk_url_kwarg = "match"
    context_object_name = "Match"

    def test_func(self):
        """Make sure the user should be allowed to see this view."""
        is_season_admin = self.request.user.season_admin_for.contains(self.get_object())
        is_staff = self.request.user.is_staff
        is_superuser = self.request.user.is_superuser
        return is_season_admin or is_staff or is_superuser

    def get_form_kwargs(self):
        """Pass the season from the match url parameter on to the form."""
        self.object = self.get_object()
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({"season": self.object.season.pk})
        return form_kwargs

    def get_context_data(self, **kwargs):
        """Inject the match object into the template context."""
        self.object = self.get_object()
        context_data = super().get_context_data(**kwargs)
        context_data["season"] = self.object.season
        return context_data

    def get_initial(self):
        """Get initial data to prefill the form."""
        initial = super().get_initial()
        initial["season"] = self.object.season
        initial["first_player"] = self.object.first_player
        initial["second_player"] = self.object.second_player
        initial["match_type"] = self.object.match_type
        initial["date_played"] = self.object.date_planned
        return initial

    def form_valid(self, form):
        """Create the scores and update the ranking, setting the match to completed."""
        data = form.cleaned_data
        match_builder = (
            MatchBuilder()
            .set_completed(False)
            .set_first_player(data["first_player"])
            .set_second_player(data["second_player"])
            .set_date_played(data["date_played"])
            .set_type_from_enum_value(data["match_type"])
            .set_minutes_played(data["minutes_played"])
            .add_score(data["first_score_1"], data["second_score_1"])
            .add_score(data["first_score_2"], data["second_score_2"])
            .add_score(data["first_score_3"], data["second_score_3"])
        )
        match_builder.complete(self.object)
        return super().form_valid(form)

    def get_success_url(self):
        """URL to redirect to on success."""
        return reverse("ligapp:season-detail", kwargs={"pk": self.object.season.pk})


class NewPlayerMatchView(NewMatchView):
    """View for recording a new match as a player."""

    form_class = NewPlayerMatchForm

    def test_func(self):
        """Make sure the user is a player in the season."""
        season = self.get_object()
        player = Player.objects.get(pk=self.kwargs["player"])
        user_player = self.request.user.player
        return season.participants.contains(user_player) and user_player == player

    def get_initial(self):
        """Prefill the first player additionally."""
        initial = super().get_initial()
        initial["first_player"] = self.request.user.player
        return initial


class AddPlayerView(UserPassesTestMixin, SingleObjectMixin, FormView):
    """View for adding a new or existing player to the season."""

    form_class = AddPlayerForm
    template_name = "ligapp/add_player_form.html"
    model = Season
    pk_url_kwarg = "season"
    context_object_name = "season"

    def form_valid(self, form):
        """Create the player or simply add it to the season."""
        data = form.cleaned_data
        season = data["season"]
        player = data["name"]
        if player.pk is not None and not season.participants.contains(player):
            season.add_player(player)
        elif player.pk is None and not season.participants.filter(name=player.name):
            season.create_player(name=player.name)
        return super().form_valid(form)

    def test_func(self):
        """Make sure the user should be allowed to see this view."""
        is_season_admin = self.request.user.season_admin_for.contains(self.get_object())
        is_staff = self.request.user.is_staff
        is_superuser = self.request.user.is_superuser
        return is_season_admin or is_staff or is_superuser

    def get_initial(self):
        """Get initial data to prefill the form."""
        initial = super().get_initial()
        initial["date_played"] = timezone.now().date()
        if "season" in self.kwargs:
            initial["season"] = Season.objects.get(pk=self.kwargs["season"])
        return initial

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse("ligapp:add-player", kwargs={"season": self.kwargs["season"]})

    def get_form_kwargs(self):
        """Pass the season url parameter on to the form."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({"season": self.kwargs["season"]})
        return form_kwargs
