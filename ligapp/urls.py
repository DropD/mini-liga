"""Ligapp url configuration."""
from django.urls import path

from . import views

app_name = "ligapp"
urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
    path("seasons/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
    path("add-season/", views.CreateSeasonView.as_view(), name="add-season"),
    path("match/<int:pk>/", views.MatchDetailView.as_view(), name="match-detail"),
    path("add-player/", views.SeasonListView.as_view(), name="add-player"),
    path("add-match/<int:season>", views.CreateMatchView.as_view(), name="add-match"),
    path("add-match/", views.CreateMatchView.as_view(), name="add-match"),
    path("new-match/<int:season>", views.NewMatchView.as_view(), name="new-match"),
]
