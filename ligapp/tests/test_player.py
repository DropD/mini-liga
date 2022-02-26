import pytest

from .model_fixtures import player


@pytest.mark.django_db
def test_str(player):
    assert str(player) == "Test Player"
