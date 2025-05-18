from typing import TYPE_CHECKING
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
    KART = 2
    CUP = 3
    TT_COURSE = 4

class MkddItem(Item):
    game = "Mario Kart Double Dash"


class MkddItemData():
    def __init__(self, name: str, classification: int, item_type: ItemType = ItemType.OTHER, address: int = 0, count: int = 1):
        self.name: str = name
        self.item_type: ItemType = item_type
        self.address: int = address
        self.classification: int = classification
        self.count = count

PROGRESSIVE_CLASS = "Progressive Class"
PROGRESSIVE_CUP_SKIP = "Progressive Cup Skip"
RANDOM_ITEM = "Random Item"
VICTORY = "Victory"

def get_item_name_tt_course(course: str):
    return f"{course} Time Trial"


data_table: list[MkddItemData] = [
    MkddItemData("", 0, count = 0), # Id 0 is reserved
    MkddItemData(PROGRESSIVE_CLASS, PROG, count = 3),
    MkddItemData(PROGRESSIVE_CUP_SKIP, USEF, count = 2),
    MkddItemData(RANDOM_ITEM, FILL),
    MkddItemData(VICTORY, PROG, count = 0),
]
data_table.extend([MkddItemData(char.name, PROG, ItemType.CHARACTER, id) for id, char in enumerate(game_data.CHARACTERS)])
data_table.extend([MkddItemData(kart.name, PROG, ItemType.KART, id, 2) for id, kart in enumerate(game_data.KARTS)])
data_table.extend([MkddItemData(name, PROG, ItemType.CUP, id) for id, name in enumerate(game_data.CUPS)])
data_table.extend([MkddItemData(get_item_name_tt_course(course.name), PROG, ItemType.TT_COURSE, id) for id, course in enumerate(game_data.COURSES) if course.type == game_data.CourseType.RACE])

name_to_id: dict[str, int] = {item.name:id for (id, item) in enumerate(data_table) if id > 0}
