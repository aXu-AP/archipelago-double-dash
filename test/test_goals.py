"""
Tests for goal / victory conditions.
"""
from . import MkddTestBase


BASE_OPTIONS = {
    "grand_prix_trophies": False,
    "shuffle_extra_trophies": 5,
    "trophy_requirement": 5,
    "time_trials": "disable",
    "logic_difficulty": 100,
    "kart_upgrades": 0,
    "items_for_everybody": 0,
    "items_per_character": 0,
    "start_items_per_character": 0,
}


class TestGoalTrophies(MkddTestBase):
    options = {**BASE_OPTIONS, "goal": "trophies"}

    def test_requires_exact_trophy_count(self) -> None:
        self.collect_all_but(["Trophy", "Victory"])

        expected_trophy_pool(self)


class TestGoalAllCupTour(MkddTestBase):
    options = {**BASE_OPTIONS, "goal": "all_cup_tour"}

    def test_requires_trophies_then_all_cup_tour(self) -> None:
        self.collect_all_but(["Trophy", "Victory", "All Cup Tour"])

        expected_trophy_pool(self)


class TestGoalTrophiesZeroRequirement(MkddTestBase):
    options = {
        **BASE_OPTIONS,
        "goal": "trophies",
        "trophy_requirement": 0,
        "shuffle_extra_trophies": 0,
    }

    def test_immediately_beatable(self) -> None:
        self.assertBeatable(True)


def expected_trophy_pool(self):
    trophies = self.get_items_by_name("Trophy")
    self.assertEqual(len(trophies), 5, "Expected 5 trophies in pool")

    self.assertBeatable(False)

    self.collect(trophies[:4])
    self.assertBeatable(False)

    self.collect(trophies[4:5])
    self.assertBeatable(True)
