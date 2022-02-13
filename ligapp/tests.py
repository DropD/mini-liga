"""Ligapp Tests."""
from django.test import TestCase
from django.utils import timezone

from . import models


class PlayerTestCase(TestCase):
    """Test suite for the Player model."""

    def setUp(self):
        self.player = models.Player(name="Test Player")
        self.player.save()

    def test_str(self):
        """Test tthe string representation."""
        assert str(self.player) == "Test Player"


class SeasonTestCase(TestCase):
    """Test suite for the Season model."""

    def setUp(self):
        self.season = models.Season(name="Test Season", start_date=timezone.now())
        self.season.save()
        participant = models.Player(name="Test Player")
        participant.save()
        self.season.participants.add(participant)

    def test_str(self):
        """Test tthe string representation."""
        assert str(self.season) == "Test Season"


class TimedMatchTestCase(TestCase):
    """Test suite for TimedMatch."""

    def setUp(self):
        player_1 = models.Player(name="Test Player 1")
        player_1.save()
        player_2 = models.Player(name="Test Player 2")
        player_2.save()
        season = models.Season(
            name="Test Season",
            start_date=timezone.make_aware(timezone.datetime(2000, 1, 1)),
        )
        season.save()
        season.participants.add(player_1, player_2)
        self.match = models.TimedMatch(
            date_played=timezone.make_aware(timezone.datetime(2000, 1, 2)),
            minutes_played=10,
            first_player=player_1,
            second_player=player_2,
            season=season,
        )
        self.match.save()
        score = models.Set(first_score=17, second_score=9, match=self.match, order=1)
        score.save()

    def test_str(self):
        """Test tthe string representation."""
        assert str(self.match) == (
            "2000-01-02 00:00:00+00:00: Test Player 1 vs Test Player 2; 17 : 9; 10'"
        )

    def test_winner(self):
        """The winner property should find the winning player."""
        assert self.match.winner == self.match.first_player


class MultiSetMatchTestCase(TestCase):
    """Test suite for MultiSetMatch."""

    def setUp(self):
        player_1 = models.Player(name="Test Player 1")
        player_1.save()
        player_2 = models.Player(name="Test Player 2")
        player_2.save()
        season = models.Season(
            name="Test Season",
            start_date=timezone.make_aware(timezone.datetime(2000, 1, 1)),
        )
        season.save()
        season.participants.add(player_1, player_2)
        self.match = models.MultiSetMatch(
            date_played=timezone.make_aware(timezone.datetime(2000, 1, 2)),
            first_player=player_1,
            second_player=player_2,
            season=season,
        )
        self.match.save()
        models.Set(first_score=21, second_score=19, match=self.match, order=1).save()
        models.Set(first_score=30, second_score=29, match=self.match, order=3).save()
        models.Set(first_score=17, second_score=21, match=self.match, order=2).save()

    def test_str(self):
        """Test tthe string representation."""
        assert str(self.match) == (
            "2000-01-02 00:00:00+00:00: Test Player 1 vs Test Player 2; 21 : 19, 17 : 21, 30 : 29"
        )

    def test_winner(self):
        """The winner property should correctly find the winning player."""
        assert self.match.winner == self.match.first_player
        set_4 = models.Set(first_score=0, second_score=1, match=self.match, order=4)
        assert self.match.winner == self.match.first_player
        set_4.save()
        assert self.match.winner is None
        models.Set(first_score=1, second_score=1, match=self.match, order=5).save()
        assert self.match.winner is None
        models.Set(first_score=1, second_score=2, match=self.match, order=5).save()
        assert self.match.winner == self.match.second_player


class SetTestCase(TestCase):
    """Test suite for Set."""

    def setUp(self):
        player_1 = models.Player(name="Test Player 1")
        player_1.save()
        player_2 = models.Player(name="Test Player 2")
        player_2.save()
        season = models.Season(
            name="Test Season",
            start_date=timezone.make_aware(timezone.datetime(2000, 1, 1)),
        )
        season.save()
        season.participants.add(player_1, player_2)
        self.match = models.MultiSetMatch(
            date_played=timezone.make_aware(timezone.datetime(2000, 1, 2)),
            first_player=player_1,
            second_player=player_2,
            season=season,
        )
        self.match.save()
        self.set_1 = models.Set(
            first_score=21, second_score=19, match=self.match, order=1
        )
        self.set_1.save()
        self.set_2 = models.Set(
            first_score=5, second_score=21, match=self.match, order=2
        )
        self.set_2.save()

    def test_str(self):
        """Test tthe string representation."""
        assert str(self.set_1) == "21 : 19"

    def test_winner(self):
        """The winner property should return the winner of the match."""
        assert self.set_1.winner == self.set_1.match.first_player
        assert self.set_2.winner == self.set_2.match.second_player
        set_3 = models.Set(first_score=6, second_score=6, match=self.match)
        assert set_3.winner is None
