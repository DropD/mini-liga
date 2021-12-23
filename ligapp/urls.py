"""Ligapp url configuration."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
    path("seasons/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
]
