"""
Tests that the correct locations are generated depending on options.
"""
from . import MkddTestBase
from worlds.mario_kart_double_dash import locations as mkdd_locs, game_data


def _location_names(test_base) -> set:
    return {loc.name for loc in test_base.multiworld.get_locations(test_base.player)}


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


class TestTTLocationsDisabled(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable"}

    def test_no_good_time_locations(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertNotIn(mkdd_locs.get_loc_name_good_time(course), location_names)

    def test_no_staff_ghost_locations(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertNotIn(mkdd_locs.get_loc_name_ghost(course.name), location_names)


class TestTTLocationsBasic(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "basic"}

    def test_all_good_time_locations_exist(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertIn(mkdd_locs.get_loc_name_good_time(course), location_names)

    def test_no_staff_ghost_locations(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertNotIn(mkdd_locs.get_loc_name_ghost(course.name), location_names)


class TestTTLocationsStaffGhosts(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "include_staff_ghosts"}

    def test_all_good_time_locations_exist(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertIn(mkdd_locs.get_loc_name_good_time(course), location_names)

    def test_all_staff_ghost_locations_exist(self) -> None:
        location_names = _location_names(self)
        for course in game_data.RACE_COURSES:
            self.assertIn(mkdd_locs.get_loc_name_ghost(course.name), location_names)


class TestGrandPrixTrophyLocations(MkddTestBase):
    options = {**BASE_OPTIONS, "grand_prix_trophies": True, "time_trials": "disable"}

    def test_all_trophy_locations_exist(self) -> None:
        location_names = _location_names(self)
        for cup in game_data.NORMAL_CUPS:
            for vehicle_class in range(4):
                name = mkdd_locs.get_loc_name_trophy(cup, vehicle_class)
                self.assertIn(name, location_names)


class TestNoGrandPrixTrophyLocations(MkddTestBase):
    options = {**BASE_OPTIONS, "grand_prix_trophies": False, "time_trials": "disable"}

    def test_no_trophy_locations(self) -> None:
        location_names = _location_names(self)
        for cup in game_data.NORMAL_CUPS:
            for vehicle_class in range(4):
                name = mkdd_locs.get_loc_name_trophy(cup, vehicle_class)
                self.assertNotIn(name, location_names)


class TestAllCupTourGoalLocation(MkddTestBase):
    options = {**BASE_OPTIONS, "goal": "all_cup_tour", "time_trials": "disable"}

    def test_win_all_cup_tour_location_exists(self) -> None:
        location_names = _location_names(self)
        self.assertIn(mkdd_locs.WIN_ALL_CUP_TOUR, location_names)


class TestTrophiesGoalNoAllCupTourLocation(MkddTestBase):
    options = {**BASE_OPTIONS, "goal": "trophies", "time_trials": "disable"}

    def test_win_all_cup_tour_location_absent(self) -> None:
        location_names = _location_names(self)
        self.assertNotIn(mkdd_locs.WIN_ALL_CUP_TOUR, location_names)


class TestCupLocationsAlwaysPresent(MkddTestBase):
    options = {**BASE_OPTIONS, "time_trials": "disable"}

    def test_all_cup_finish_locations_exist(self) -> None:
        location_names = _location_names(self)
        for cup in game_data.NORMAL_CUPS:
            self.assertIn(mkdd_locs.get_loc_name_finish(cup), location_names)

    def test_all_cup_gold_50cc_locations_exist(self) -> None:
        location_names = _location_names(self)
        for cup in game_data.NORMAL_CUPS:
            self.assertIn(mkdd_locs.get_loc_name_cup(cup, 0, 0), location_names)
