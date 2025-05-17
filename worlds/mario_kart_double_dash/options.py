from dataclasses import dataclass
from Options import Choice, OptionCounter, OptionDict, Range, Toggle, PerGameCommonOptions, StartInventoryPool

class AllCupTourLength(Range):
    """How many courses are in the All Cup Tour? 0 = disable, 16 = vanilla. Default 8."""
    display_name = "All Cup Tour Length"
    range_start = 0
    range_end = 16
    default = 8

class ShorterCourses(Toggle):
    """Makes most courses 2 laps long. Might make the flow of the game better."""
    display_name = "Shorter Courses"

class CustomLapCounts(OptionCounter):
    """Set custom amount of laps on each course."""
    display_name = "Custom Lap Counts"
    default = {"Luigi Circuit": 3}
    

@dataclass
class MkddOptions(PerGameCommonOptions):
    all_cup_tour_length: AllCupTourLength

    shorter_courses: ShorterCourses
    custom_lap_counts: CustomLapCounts
    
    start_inventory_from_pool: StartInventoryPool
