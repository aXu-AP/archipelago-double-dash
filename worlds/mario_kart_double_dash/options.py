from dataclasses import dataclass
from Options import Choice, Toggle, PerGameCommonOptions, StartInventoryPool

@dataclass
class MkddOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
