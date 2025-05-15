from typing import Callable, Dict, List, NamedTuple, Optional, TYPE_CHECKING
from enum import Enum

from BaseClasses import Item, ItemClassification
from . import game_data

if TYPE_CHECKING:
    from . import MkddWorld

PROG = ItemClassification.progression
FILL = ItemClassification.filler
USEF = ItemClassification.useful
SKIP = ItemClassification.progression_skip_balancing
TRAP = ItemClassification.trap

class ItemType(Enum):
    OTHER = 0
    CHARACTER = 1
    CUP = 2

class MkddItem(Item):
    game = "Mario Kart Double Dash"


class MkddItemData():
    def __init__(self, name: str, classification: int, item_type: ItemType = ItemType.OTHER, address: int = 0, count: int = 1):
        self.name: str = name
        self.item_type: ItemType = item_type
        self.address: int = address
        self.classification: int = classification
        self.count = count

data_table: List[MkddItemData] = [
    MkddItemData("Progressive Class", PROG, count = 3),
    MkddItemData("Random Item", FILL),
    MkddItemData("Victory", PROG, count = 0),
]
data_table.extend([MkddItemData(char.name, PROG, ItemType.CHARACTER, id) for id, char in enumerate(game_data.CHARACTERS)])
data_table.extend([MkddItemData(kart.name, PROG, count = 2) for kart in game_data.KARTS])
data_table.extend([MkddItemData(name, PROG) for name in game_data.CUPS])
data_table.extend([MkddItemData(f"{course.name} Time Trial", PROG) for course in game_data.COURSES if course.type == game_data.CourseType.RACE])

name_to_id: Dict[str, int] = {item.name:id for (id, item) in enumerate(data_table)}