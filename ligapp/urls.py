"""Ligapp url configuration."""
from django.urls import path

from . import views

app_name = "ligapp"
urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
    path("season/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
    path("add-season/", views.CreateSeasonView.as_view(), name="add-season"),
    path("match/<int:pk>/", views.MatchDetailView.as_view(), name="match-detail"),
    path("add-player/", views.SeasonListView.as_view(), name="add-player"),
    path(
        "season/<int:season>/add-match/",
        views.CreateMatchView.as_view(),
        name="add-match",
    ),
    path(
        "season/<int:season>/new-match", views.NewMatchView.as_view(), name="new-match"
    ),
]
