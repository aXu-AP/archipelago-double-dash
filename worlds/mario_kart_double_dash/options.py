from dataclasses import dataclass
from Options import Choice, OptionDict, Range, Toggle, PerGameCommonOptions, StartInventoryPool

class AllCupTourLength(Range):
    """How many courses are in the All Cup Tour? 0 = disable, 16 = vanilla. Default 8."""
    display_name = "All Cup Tour Length"
    range_start = 0
    range_end = 16
    default = 8

class ShorterCourses(Toggle):
    """Makes most courses 2 laps long. Might make the flow of the game better."""
    display_name = "Shorter Courses"

class CustomLapCounts(OptionDict):
    """Set custom amount of laps on each course."""
    display_name = "Custom Lap Counts"
    default = {"Luigi Circuit": 3}
    
class ItemsForEverybody(Range):
    """How many global item unlocks there are."""
    display_name = "Items for Everybody"
    range_start = 0
    range_end = 19
    default = 4

class ItemsPerCharacter(Range):
    """How many item unlocks there are per character.
    Note: this setting raises the amount of items considerably and will be automatically lowered if there is not enough locations."""
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
    all_cup_tour_length: AllCupTourLength

    shorter_courses: ShorterCourses
    custom_lap_counts: CustomLapCounts

    items_for_everybody: ItemsForEverybody
    items_per_character: ItemsPerCharacter

    kart_upgrades: KartUpgrades

    start_inventory_from_pool: StartInventoryPool
