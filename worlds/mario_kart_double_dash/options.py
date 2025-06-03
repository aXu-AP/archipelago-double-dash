from dataclasses import dataclass
from Options import Choice, NamedRange, OptionDict, PerGameCommonOptions, Range, StartInventoryPool, Toggle, Visibility

class Goal(Choice):
    """Victory condition for the game.
    All Cup Tour: Collect set amount of gold trophies to unlock All Cup Tour. Get gold in All Cup Tour to win.
    Trophies: Collect set amount of gold trophies to win."""
    display_name = "Goal"
    option_all_cup_tour = 0
    option_trophies = 1

class TrophyAmount(Range):
    """How many gold trophies are needed for goal completion.
    Recommended: 9-12 if you aim to complete the game on 150cc. 13-16 if you aim to complete the game on Mirror."""
    display_name = "Trophy Amount"
    range_start = 0
    range_end = 16
    default = 10

class LogicDifficulty(NamedRange):
    """Balances the difficulty modeling, how many upgrades you are presumed to have to win races.
    Use normal (0) if you can comfortably win 100cc races.
    Unrestricted places locations in logic as soon as they are technically possible."""
    display_name = "Logic Difficulty."  
    range_start = -50
    range_end = 100
    default = 0
    special_range_names = {
        "baby": -50,
        "easy": -25,
        "normal": 0,
        "hard": 50,
        "unrestricted": 100,
    }

class TrackerUnrestrictedLogic(Toggle):
    """If enabled, the Universal Tracker will show all locations that are techically accessible (as if Logic Difficulty was set to unrestricted)."""
    display_name = "Tracker Unrestricted Logic"
    visibility = Visibility.complex_ui | Visibility.template | Visibility.spoiler

class TimeTrials(Choice):
    """Are time trials in logic? If enabled, item pool has course unlocks for time trials.
    Basic adds locations for beating certain times.
    Include Staff Ghosts enables staff ghosts into logic. For experts only!"""
    display_name = "Time Trials"
    option_disable = 0
    option_basic = 1
    option_include_staff_ghosts = 2
    default = 1

class CourseShuffle(Choice):
    """How the courses are shuffled in cups."""
    display_name = "Course Shuffle"
    option_vanilla = 0
    option_shuffle_once = 1
    #option_shuffle_per_class = 2
    default = 1

class AllCupTourLength(Range):
    """How many races are in the All Cup Tour? 16 = vanilla. Default 8."""
    display_name = "All Cup Tour Length"
    range_start = 2
    range_end = 16
    default = 8

class Mirror200cc(Toggle):
    """Mirror mode is 200cc if enabled."""
    display_name = "Mirror is 200cc"

class ShorterCourses(Toggle):
    """Makes most courses 2 laps long. Might make the flow of the game better."""
    display_name = "Shorter Courses"

class CustomLapCounts(OptionDict):
    """Set custom amount of laps on each course.
    Write each course on its own line, followed by : and number of laps."""
    display_name = "Custom Lap Counts"
    default = {"Wario Colosseum": 2}
    
class ItemsForEverybody(Range):
    """How many global item unlocks there are."""
    display_name = "Items for Everybody"
    range_start = 0
    range_end = 19
    default = 4

class ItemsPerCharacter(Range):
    """How many item unlocks there are per character.
    Note: this setting raises the amount of items in item pool considerably, and might cause the generation to fail."""
    display_name = "Items per Character"
    range_start = 0
    range_end = 4
    default = 3

class KartUpgrades(Range):
    """How many random kart stat upgrades there are total.
    Unlike progressive engine upgrades, these upgrades are tied to certain vehicles."""
    display_name = "Kart Upgrades"
    range_start = 0
    range_end = 40
    default = 10

@dataclass
class MkddOptions(PerGameCommonOptions):
    goal: Goal
    trophy_amount: TrophyAmount
    logic_difficulty: LogicDifficulty
    tracker_unrestricted_logic: TrackerUnrestrictedLogic
    time_trials: TimeTrials

    course_shuffle: CourseShuffle
    all_cup_tour_length: AllCupTourLength

    mirror_200cc: Mirror200cc
    shorter_courses: ShorterCourses
    custom_lap_counts: CustomLapCounts

    items_for_everybody: ItemsForEverybody
    items_per_character: ItemsPerCharacter

    kart_upgrades: KartUpgrades

    start_inventory_from_pool: StartInventoryPool
