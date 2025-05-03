from typing import Callable, Dict, NamedTuple, Optional, TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from . import game_data 

if TYPE_CHECKING:
    from . import MkddWorld




PROG = ItemClassification.progression
FILL = ItemClassification.filler
USEF = ItemClassification.useful
SKIP = ItemClassification.progression_skip_balancing
TRAP = ItemClassification.trap
EVENT = -1

class MkddItem(Item):
    game = "Mario Kart Double Dash"


class MkddItemData():
    id_iterator = 1000
    def __init__(self, classification: int, count: int = 1):
        if classification == EVENT:
            self.id: int = 0
            self.classification: int = FILL
        else:
            self.id: int = MkddItemData.id_iterator
            self.classification: int = classification
            self.count = count
            MkddItemData.id_iterator += 1

item_data_table: Dict[str, MkddItemData] = {
    "Progressive Mode": MkddItemData(PROG, 3),
    "Random Item": MkddItemData(FILL),
    "Victory": MkddItemData(PROG, 0),
}
item_data_table.update({char.name:MkddItemData(PROG) for char in game_data.CHARACTERS})
item_data_table.update({kart.name:MkddItemData(PROG, 2) for kart in game_data.KARTS})
item_data_table.update({name:MkddItemData(PROG) for name in game_data.CUPS})
item_data_table.update({f"{name} Time Trial":MkddItemData(PROG) for name in game_data.COURSES})

item_id_table: Dict[str, int] = {name:data.id for (name, data) in item_data_table.items() if data.id != 0}
