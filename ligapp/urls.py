"""Ligapp url configuration."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.SeasonListView.as_view(), name="index"),
]
