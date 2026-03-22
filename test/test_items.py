"""
Tests for item pool composition and counts.
"""
from . import MkddTestBase
from worlds.mario_kart_double_dash import game_data, items as mkdd_items

BASE_OPTIONS = {
    "goal": "trophies",
    "trophy_requirement": 0,
    "grand_prix_trophies": False,
    "shuffle_extra_trophies": 0,
    "kart_upgrades": 0,
    "items_for_everybody": 0,
    "items_per_character": 0,
    "start_items_per_character": 0,
    "item_boxes_as_locations": "disabled",
}


def _count(pool, name: str) -> int:
    return sum(1 for item in pool if item.name == name)


def _count_any(pool, names) -> int:
    return sum(1 for item in pool if item.name in names)


class TestItemPoolCounts(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "speed_upgrades": True}

    def test_character_count(self) -> None:
        character_names = {c.name for c in game_data.CHARACTERS}
        in_pool = _count_any(self.multiworld.itempool, character_names)
        self.assertEqual(in_pool, 18)

    def test_kart_count(self) -> None:
        kart_names = {k.name for k in game_data.KARTS}
        in_pool = _count_any(self.multiworld.itempool, kart_names)
        self.assertEqual(in_pool, 18)

    def test_normal_cup_count(self) -> None:
        cup_names = set(game_data.NORMAL_CUPS)
        in_pool = _count_any(self.multiworld.itempool, cup_names)
        self.assertEqual(in_pool, 3)

    def test_progressive_cc_count(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.PROGRESSIVE_CLASS)
        self.assertEqual(in_pool, 3)

    def test_no_all_cup_tour_in_pool(self) -> None:
        in_pool = _count(self.multiworld.itempool, game_data.CUPS[game_data.CUP_ALL_CUP_TOUR])
        self.assertEqual(in_pool, 0)


class TestSpeedUpgradesEnabled(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "speed_upgrades": True}

    def test_three_speed_upgrades_in_pool(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.PROGRESSIVE_ENGINE)
        self.assertEqual(in_pool, 3)


class TestSpeedUpgradesDisabled(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "speed_upgrades": False}

    def test_no_speed_upgrades_in_pool(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.PROGRESSIVE_ENGINE)
        self.assertEqual(in_pool, 0)


class TestKartUpgradesPresent(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "kart_upgrades": 10}

    def test_kart_upgrade_count(self) -> None:
        upgrade_names = {
            mkdd_items.get_item_name_kart_upgrade(upgrade.name, kart.name)
            for upgrade in game_data.KART_UPGRADES
            for kart in game_data.KARTS
        }
        in_pool = _count_any(self.multiworld.itempool, upgrade_names)
        self.assertEqual(in_pool, 10)


class TestKartUpgradesAbsent(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "kart_upgrades": 0}

    def test_no_kart_upgrades_in_pool(self) -> None:
        upgrade_names = {
            mkdd_items.get_item_name_kart_upgrade(upgrade.name, kart.name)
            for upgrade in game_data.KART_UPGRADES
            for kart in game_data.KARTS
        }
        in_pool = _count_any(self.multiworld.itempool, upgrade_names)
        self.assertEqual(in_pool, 0)


class TestTTItemsEnabled(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "basic", "speed_upgrades": True}

    def test_tt_course_items_in_pool(self) -> None:
        tt_names = { mkdd_items.get_item_name_tt_course(c.name) for c in game_data.RACE_COURSES }
        in_pool = _count_any(self.multiworld.itempool, tt_names)
        self.assertEqual(in_pool, 15)

    def test_progressive_tt_item_in_pool(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.PROGRESSIVE_TIME_TRIAL_ITEM)
        self.assertEqual(in_pool, 3)


class TestTTItemsDisabled(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "speed_upgrades": True}

    def test_no_tt_course_items_in_pool(self) -> None:
        tt_names = { mkdd_items.get_item_name_tt_course(c.name) for c in game_data.RACE_COURSES }
        in_pool = _count_any(self.multiworld.itempool, tt_names)
        self.assertEqual(in_pool, 0)

    def test_no_progressive_tt_item_in_pool(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.PROGRESSIVE_TIME_TRIAL_ITEM)
        self.assertEqual(in_pool, 0)


class TestExtraTrophiesInPool(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable", "shuffle_extra_trophies": 7}

    def test_extra_trophy_count(self) -> None:
        in_pool = _count(self.multiworld.itempool, mkdd_items.TROPHY)
        self.assertEqual(in_pool, 7)
