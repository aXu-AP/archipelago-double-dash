"""
Tests for location / region access rules.

Verifies that specific item requirements (Progressive CC, TT course unlocks) still gate the expected locations.
"""
from . import MkddTestBase

from worlds.mario_kart_double_dash import locations


BASE_OPTIONS = {
    "goal": "trophies",
    "trophy_requirement": 0,
    "grand_prix_trophies": False,
    "shuffle_extra_trophies": 0,
    "logic_difficulty": 100, # unrestricted – difficulty never blocks
    "kart_upgrades": 0,
    "items_for_everybody": 0,
    "items_per_character": 0,
    "start_items_per_character": 0,
    "item_boxes_as_locations": "disabled",
}


class TestProgressiveCC(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable"}

    def test_50cc_accessible_without_progressive_cc(self) -> None:
        self.collect_all_but("Progressive CC")
        self.assertTrue(self.can_reach_location(
            locations.get_loc_name_cup("Mushroom Cup", 0, 0)
        ))

    def test_100cc_requires_one_progressive_cc(self) -> None:
        self.collect_all_but("Progressive CC")
        location_100_cc = locations.get_loc_name_cup("Mushroom Cup", 0, 1)

        self.assertFalse(self.can_reach_location(location_100_cc))

        progressive_cc = self.get_items_by_name("Progressive CC")
        self.collect(progressive_cc[:1])
        self.assertTrue(self.can_reach_location(location_100_cc))

    def test_150cc_requires_two_progressive_cc(self) -> None:
        self.collect_all_but("Progressive CC")
        location_150_cc = locations.get_loc_name_cup("Mushroom Cup", 0, 2)

        self.assertFalse(self.can_reach_location(location_150_cc))

        progressive_cc = self.get_items_by_name("Progressive CC")
        self.collect(progressive_cc[:1])
        self.assertFalse(self.can_reach_location(location_150_cc))

        self.collect(progressive_cc[1:2])
        self.assertTrue(self.can_reach_location(location_150_cc))

    def test_mirror_requires_three_progressive_cc(self) -> None:
        self.collect_all_but("Progressive CC")
        location_mirror = locations.get_loc_name_cup("Mushroom Cup", 0, 3)

        self.assertFalse(self.can_reach_location(location_mirror))

        progressive_cc = self.get_items_by_name("Progressive CC")
        self.collect(progressive_cc[:2])
        self.assertFalse(self.can_reach_location(location_mirror))

        self.collect(progressive_cc[2:3])
        self.assertTrue(self.can_reach_location(location_mirror))


class TestTimeTrialAccess(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "basic"}

    _LUIGI_TT = "Luigi Circuit Time Trial in 1:35"
    _PEACH_TT = "Peach Beach Time Trial in 1:30"

    def test_tt_location_blocked_without_unlock(self) -> None:
        self.collect_all_but("Luigi Circuit Time Trial")

        self.assertTrue(self.can_reach_location(self._PEACH_TT))

        if not self.multiworld.state.has("Luigi Circuit Time Trial", self.player):
            self.assertFalse(self.can_reach_location(self._LUIGI_TT))

    def test_tt_location_accessible_with_unlock(self) -> None:
        self.collect_all_but("Luigi Circuit Time Trial")
        self.collect_by_name("Luigi Circuit Time Trial")
        self.assertTrue(self.can_reach_location(self._LUIGI_TT))


class TestCupAccess(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable"}

    def test_mushroom_cup_blocked_without_unlock(self) -> None:
        self.collect_all_but("Mushroom Cup")

        if not self.multiworld.state.has("Mushroom Cup", self.player):
            self.assertFalse(self.can_reach_location("Mushroom Cup Finish"))

    def test_mushroom_cup_accessible_with_unlock(self) -> None:
        mushroom_cup = self.world.create_item("Mushroom Cup")
        self.multiworld.state.collect(mushroom_cup)
        self.assertTrue(self.can_reach_location("Mushroom Cup Finish"))

    def test_flower_cup_blocked_without_unlock(self) -> None:
        self.collect_all_but("Flower Cup")

        if not self.multiworld.state.has("Flower Cup", self.player):
            self.assertFalse(self.can_reach_location("Flower Cup Finish"))

    def test_flower_cup_accessible_with_unlock(self) -> None:
        flower_cup = self.world.create_item("Flower Cup")
        self.multiworld.state.collect(flower_cup)
        self.assertTrue(self.can_reach_location("Flower Cup Finish"))

    def test_star_cup_blocked_without_unlock(self) -> None:
        self.collect_all_but("Star Cup")

        if not self.multiworld.state.has("Star Cup", self.player):
            self.assertFalse(self.can_reach_location("Star Cup Finish"))

    def test_star_cup_accessible_with_unlock(self) -> None:
        star_cup = self.world.create_item("Star Cup")
        self.multiworld.state.collect(star_cup)
        self.assertTrue(self.can_reach_location("Star Cup Finish"))

    def test_special_cup_blocked_without_unlock(self) -> None:
        self.collect_all_but("Special Cup")

        if not self.multiworld.state.has("Special Cup", self.player):
            self.assertFalse(self.can_reach_location("Special Cup Finish"))

    def test_special_cup_accessible_with_unlock(self) -> None:
        special_cup = self.world.create_item("Special Cup")
        self.multiworld.state.collect(special_cup)
        self.assertTrue(self.can_reach_location("Special Cup Finish"))
