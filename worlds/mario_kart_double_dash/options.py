from dataclasses import dataclass
from Options import Choice, Range, Toggle, PerGameCommonOptions, StartInventoryPool

class AllCupTourLength(Range):
    """How many courses are in the All Cup Tour? 0 = disable, 16 = vanilla. Default 8."""
    display_name = "All Cup Tour Length"
    range_start = 0
    range_end = 16
    default = 8

@dataclass
class MkddOptions(PerGameCommonOptions):
    all_cup_tour_length: AllCupTourLength
    start_inventory_from_pool: StartInventoryPool
