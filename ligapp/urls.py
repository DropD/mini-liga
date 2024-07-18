"""Ligapp url configuration."""

from django.urls import path

from . import views

app_name = "ligapp"
urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
    path("season/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
    path(
        "season/<int:pk>/ranking",
        views.SeasonRankingView.as_view(),
        name="season-ranking",
    ),
    path(
        "season/<int:pk>/match-history",
        views.SeasonMatchHistoryView.as_view(),
        name="season-match-history",
    ),
    path("add-season/", views.CreateSeasonView.as_view(), name="add-season"),
    path("match/<int:pk>/", views.MatchDetailView.as_view(), name="match-detail"),
    path(
        "match/<int:match>/record-results/",
        views.CompletePlannedMatchView.as_view(),
        name="match-complete",
    ),
    path(
        "season/<int:season>/plan-match/",
        views.NewPlannedMatchView.as_view(),
        name="plan-match",
    ),
    path("season/<int:season>/new-match", views.NewMatchView.as_view(), name="new-match"),
    path(
        "season/<int:season>/new-match/as-player/<int:player>",
        views.NewPlayerMatchView.as_view(),
        name="new-match-as-player",
    ),
    path(
        "season/<int:season>/add-player",
        views.AddPlayerView.as_view(),
        name="add-player",
    ),
    path(
        "head2head/<int:first>/<int:second>",
        views.Head2HeadView.as_view(),
        name="head2head",
    ),
    path(
        "season/<int:season>/new-sparring-day",
        views.NewSparringDayView.as_view(),
        name="new-sparring-day",
    ),
]
