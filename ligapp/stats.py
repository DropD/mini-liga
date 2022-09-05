"""Player stats utilities."""
import collections
import dataclasses

from django.contrib.auth.models import User

from . import models


@dataclasses.dataclass
class Head2Head:
    """Player vs Player statistics."""

    first: models.Player
    second: models.Player
    user: User

    @property
    def matches(self):
        pair = [self.first, self.second]
        return models.Match.objects.filter(
            first_player__in=pair,
            second_player__in=pair,
            completed=True,
            season__admins=self.user,
        )

    def count_wins(self, matches) -> collections.Counter[models.Player]:
        win_counter: collections.Counter[models.Player] = collections.Counter()
        for match in matches:
            win_counter.update(match.winner)
        return win_counter

    def count_sets(self, matches) -> collections.Counter[models.Player]:
        won_sets: collections.Counter[models.Player] = collections.Counter()
        for match in matches:
            for set in match.sets.all():
                won_sets.update(set.winner)
        return won_sets

    def count_points(self, matches) -> collections.Counter[models.Player]:
        won_points: collections.Counter[models.Player] = collections.Counter()
        for set in models.Set.objects.all():
            won_points.update({set.first_player: set.first_score})
            won_points.update({set.second_player: set.second_score})
        return won_points

    @property
    def season_stats(self):
        seasons = (
            models.Season.objects.filter(admins=self.user)
            .filter(participants=self.first.pk)
            .filter(participants=self.second.pk)
        )
        return [
            (
                season,
                models.Rank.objects.get(season=season, player=self.first).rank,
                models.Rank.objects.get(season=season, player=self.second).rank,
            )
            for season in seasons
        ]

    @property
    def stats(self):
        matches = self.matches
        wins = self.count_wins(matches)
        sets = self.count_sets(matches)
        points = self.count_points(matches)

        def make_stat_line(name, stat):
            total = sum(stat)
            if total == 0:
                return [name, [(stat[0],), (stat[1],)]]
            return (name, [(stat_i, stat_i / total * 100) for stat_i in stat])

        if not matches:
            return [
                ("Matches", [(0,), (0,)]),
                ("Sets", [(0,), (0,)]),
                (
                    "Points",
                    [(0,), (0,)],
                ),
            ]

        stats = [
            make_stat_line("Matches", (wins[self.first], wins[self.second])),
            make_stat_line("Sets", (sets[self.first], sets[self.second])),
            make_stat_line("Points", (points[self.first], points[self.second])),
        ]
        print(stats)
        return stats

    def matches_by_date(self):
        result = {}
        for match in self.matches.order_by("-date_played"):
            result.setdefault(match.date_played, []).append(match)
        return result.items()
