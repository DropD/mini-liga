def save_n(n):
    def save_n_(sets):
        for i in range(n):
            sets[i].save()

    return save_n_


class SetsMatchStrs:
    def case_no_sets(self):
        return save_n(0), "2000-01-02: Test Player vs Other Player; --"

    def case_one_set(self):
        return save_n(1), "2000-01-02: Test Player vs Other Player; 17 : 9"

    def case_two_sets(self):
        return save_n(2), "2000-01-02: Test Player vs Other Player; 17 : 9, 17 : 21"

    def case_three_sets(self):
        return (
            save_n(3),
            "2000-01-02: Test Player vs Other Player; 17 : 9, 17 : 21, 14 : 19",
        )


class SetsMatchWinners:
    def case_no_sets(self):
        return save_n(0), lambda match: None

    def case_one_set(self):
        return save_n(1), lambda match: match.first_player

    def case_two_sets(self):
        return save_n(2), lambda match: None

    def case_three_sets(self):
        return save_n(3), lambda match: match.second_player
