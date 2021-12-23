"""Ligapp url configuration."""
from django.urls import path

from . import views

app_name = "ligapp"
urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
    path("seasons/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
    path("match/<int:pk>/", views.MatchDetailView.as_view(), name="match-detail"),
    path("add_player/", views.SeasonListView.as_view(), name="add-player"),
]
