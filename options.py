from dataclasses import dataclass
from Options import Choice, DefaultOnToggle, NamedRange, OptionDict, PerGameCommonOptions, Range, StartInventoryPool, Toggle, Visibility
from schema import And, Schema

class Goal(Choice):
    """Victory condition for the game.
    All Cup Tour: Collect set amount of gold trophies to unlock All Cup Tour. Get gold in All Cup Tour to win.
    Trophies: Collect set amount of gold trophies to win."""
    display_name = "Goal"
    option_all_cup_tour = 0
    option_trophies = 1

class TrophyRequirement(Range):
    """How many gold trophies are needed for goal completion.
    Recommended: 9-12 if you aim to complete the game on 150cc. 13-16 if you aim to complete the game on Mirror.
    Value will be limited to the number of trophies in the pool."""
    display_name = "Trophy Requirement"
    range_start = 0
    range_end = 32
    default = 10

class GrandPrixTrophies(DefaultOnToggle):
    """Does getting gold in cups earn you trophies."""
    display_name = "Grand Prix Trophies"

class ShuffleExtraTrophies(Range):
    """How many trophies are added in the pool in addition to predetermined trophy locations.
    These trophies can appear in other players' worlds."""
    display_name = "Shuffle Extra Trophies"
    range_start = 0
    range_end = 16
    default = 0

class LogicDifficulty(NamedRange):
    """Balances the difficulty modeling, how many upgrades you are presumed to have to win races.
    Use normal (0) if you can comfortably win 100cc races.
    Unrestricted places locations in logic as soon as they are technically possible."""
    display_name = "Logic Difficulty"  
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
    # TODO: option_shuffle_per_class = 2
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

class Faster50cc100cc(Toggle):
    """Makes 50cc as fast as 100cc and 100cc closer to 150cc."""
    display_name = "Faster 50cc and 100cc"

class ShorterCourses(Toggle):
    """Makes most courses 2 laps long. Might make the flow of the game better."""
    display_name = "Shorter Courses"

class CustomLapCounts(OptionDict):
    """Set custom amount of laps on each course.
    Write each course on its own line, followed by : and number of laps(max 9)."""
    display_name = "Custom Lap Counts"
    default = {"Wario Colosseum": 2}
    schema = Schema({
        str: And(int, lambda n: 1 <= n <= 9)
    })
    
class ItemsForEverybody(Range):
    """How many global item unlocks there are."""
    display_name = "Items for Everybody"
    range_start = 0
    range_end = 19
    default = 4

class ItemsPerCharacter(Range):
    """How many item unlocks there are per character."""
    display_name = "Items per Character"
    range_start = 0
    range_end = 5
    default = 3

class StartItemsPerCharacter(Range):
    """Unlocks some items for the characters straight away."""
    display_name = "Start Items per Character"
    range_start = 0
    range_end = 5
    default = 1

class FranticItems(Range):
    """Changes the item distribution to give all items evenly regardless of current position."""
    display_name = "Frantic Items"
    range_start = 0
    range_end = 100
    default = 0
    special_range_names = {
        "vanilla": 0,
        "medium": 50,
        "frantic": 100,
    }

class GuaranteedItems(DefaultOnToggle):
    """Guarantees getting unlocked items if they are appropriate for your position.
    For example, if your character has mushroom unlocked, you cannot get blank item at 4th or worse place."""
    display_name = "Guaranteed Items"

class KartUpgrades(Range):
    """How many random kart stat upgrades there are total.
    Unlike progressive engine upgrades, these upgrades are tied to certain vehicles."""
    display_name = "Kart Upgrades"
    range_start = 0
    range_end = 100
    default = 20

class SpeedUpgrades(DefaultOnToggle):
    """Adds 3 Progressive Speed Upgrades to the pool.
    You start at a slight disadvantage (90 % speed) and collecting all the speed upgrades gets you to 110 % speed.
    Disabling this sets logic difficulty on hard if it's lower."""
    display_name = "Speed Upgrades"

class ItemBoxesAsLocations(Choice):
    """Makes some item boxes count as checks.
    Interesting locations adds 1-3 checks per course.
    Box Groups grants you checks by touching any box in a row/group.
    Boxsanity adds checks to every box individually."""
    display_name = "Item Boxes as Locations"
    option_disabled = 0
    option_interesting_locations = 1
    option_box_groups = 2
    option_boxsanity = 3
    default = 1

class AddCustomItemBoxes(DefaultOnToggle):
    """Moves some item boxes to interesting places, like shortcuts."""
    display_name = "Add Custom Item Boxes"

class ShortcutsAsLocations(DefaultOnToggle):
    """Grants checks from completing shortcuts. Some shortcuts require items like mushrooms."""
    display_name = "Shortcuts as Locations"

class TrapChance(Range):
    """Percentage of how many filler items are converted into traps."""
    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 5


@dataclass
class MkddOptions(PerGameCommonOptions):
    goal: Goal
    trophy_requirement: TrophyRequirement
    grand_prix_trophies: GrandPrixTrophies
    shuffle_extra_trophies: ShuffleExtraTrophies
    logic_difficulty: LogicDifficulty
    time_trials: TimeTrials

    course_shuffle: CourseShuffle
    all_cup_tour_length: AllCupTourLength

    mirror_200cc: Mirror200cc
    faster_50cc_100cc: Faster50cc100cc
    shorter_courses: ShorterCourses
    custom_lap_counts: CustomLapCounts

    items_for_everybody: ItemsForEverybody
    items_per_character: ItemsPerCharacter
    start_items_per_character: StartItemsPerCharacter
    frantic_items: FranticItems
    guaranteed_items: GuaranteedItems

    kart_upgrades: KartUpgrades
    speed_upgrades: SpeedUpgrades

    item_boxes_as_locations: ItemBoxesAsLocations
    add_custom_item_boxes: AddCustomItemBoxes
    shortcuts_as_locations: ShortcutsAsLocations
    
    trap_chance: TrapChance

    start_inventory_from_pool: StartInventoryPool

    def to_slot_data(self) -> dict[str, any]:
        """Returns dict of relevant options for UT or the client."""
        return self.as_dict(
            "trophy_requirement",
            "logic_difficulty",
            "time_trials",
            "all_cup_tour_length",
            "custom_lap_counts",
            "mirror_200cc",
            "faster_50cc_100cc",
            "frantic_items",
            "guaranteed_items",
            "item_boxes_as_locations",
            "add_custom_item_boxes",
            "shortcuts_as_locations",
        )

    def update_from_slot_data(self, slot_data: dict[str, any]) -> None:
        """Sets options that are relayed in slot data."""
        for key, val in slot_data.items():
            if key in MkddOptions.type_hints: # Filter non-option data.
                setattr(self, key, val)

def init_options() -> MkddOptions:
    """Initializes options object with default values."""
    return MkddOptions(**{key: val.default for key, val in MkddOptions.type_hints.items()})
