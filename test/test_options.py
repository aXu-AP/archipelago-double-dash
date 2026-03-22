"""
Tests that various option combinations generate valid worlds without errors.
WorldTestBase automatically runs generation and checks that it completes.
"""
from . import MkddTestBase


# --- Goal options ---

class TestGoalTrophies(MkddTestBase):
    options = {"goal": "trophies"}


class TestGoalAllCupTour(MkddTestBase):
    options = {"goal": "all_cup_tour"}


# --- Trophy options ---

class TestTrophiesNoGrandPrix(MkddTestBase):
    options = {
        "grand_prix_trophies": False,
        "shuffle_extra_trophies": 10,
        "trophy_requirement": 10,
    }


class TestTrophiesHighRequirement(MkddTestBase):
    options = {
        "grand_prix_trophies": True,
        "shuffle_extra_trophies": 0,
        "trophy_requirement": 32,  # should be clamped to 16
    }


class TestTrophiesZeroRequirement(MkddTestBase):
    options = {
        "goal": "trophies",
        "trophy_requirement": 0,
        "grand_prix_trophies": False,
        "shuffle_extra_trophies": 0,
    }


# --- Time trial options ---

class TestTimeTrialsDisabled(MkddTestBase):
    options = {"time_trials": "disable"}


class TestTimeTrialsBasic(MkddTestBase):
    options = {"time_trials": "basic"}


class TestTimeTrialsStaffGhosts(MkddTestBase):
    options = {"time_trials": "include_staff_ghosts"}


# --- Course shuffle options ---

class TestCourseShuffleVanilla(MkddTestBase):
    options = {"course_shuffle": "vanilla"}


class TestCourseShuffleOnce(MkddTestBase):
    options = {"course_shuffle": "shuffle_once"}


# --- Logic difficulty options ---

class TestLogicDifficultyBaby(MkddTestBase):
    options = {"logic_difficulty": -50}


class TestLogicDifficultyNormal(MkddTestBase):
    options = {"logic_difficulty": 0}


class TestLogicDifficultyHard(MkddTestBase):
    options = {"logic_difficulty": 50}


class TestLogicDifficultyUnrestricted(MkddTestBase):
    options = {"logic_difficulty": 100}


# --- Speed / engine upgrade options ---

class TestSpeedUpgradesEnabled(MkddTestBase):
    options = {"speed_upgrades": True}


class TestSpeedUpgradesDisabled(MkddTestBase):
    options = {"speed_upgrades": False}


# --- Kart upgrade options ---

class TestKartUpgradesNone(MkddTestBase):
    options = {"kart_upgrades": 0}


class TestKartUpgradesMany(MkddTestBase):
    options = {"kart_upgrades": 40}


# --- Item box locations ---

class TestItemBoxLocationsDisabled(MkddTestBase):
    options = {"item_boxes_as_locations": "disabled"}


class TestItemBoxLocationsEnabled(MkddTestBase):
    options = {"item_boxes_as_locations": "interesting_locations"}


# --- All Cup Tour length ---

class TestAllCupTourShort(MkddTestBase):
    options = {
        "goal": "all_cup_tour",
        "all_cup_tour_length": 2,
    }


class TestAllCupTourFull(MkddTestBase):
    options = {
        "goal": "all_cup_tour",
        "all_cup_tour_length": 16,
    }


# --- Combined option tests ---

class TestMinimalOptions(MkddTestBase):
    options = {
        "goal": "trophies",
        "trophy_requirement": 0,
        "grand_prix_trophies": False,
        "shuffle_extra_trophies": 0,
        "time_trials": "disable",
        "kart_upgrades": 0,
        "speed_upgrades": False,
        "items_for_everybody": 0,
        "items_per_character": 0,
        "start_items_per_character": 0,
        "item_boxes_as_locations": "disabled",
    }


class TestMaximalOptions(MkddTestBase):
    options = {
        "goal": "all_cup_tour",
        "trophy_requirement": 16,
        "grand_prix_trophies": True,
        "shuffle_extra_trophies": 16,
        "time_trials": "include_staff_ghosts",
        "course_shuffle": "shuffle_once",
        "kart_upgrades": 40,
        "speed_upgrades": True,
        "items_for_everybody": 4,
        "items_per_character": 3,
        "start_items_per_character": 1,
        "logic_difficulty": 0,
    }
