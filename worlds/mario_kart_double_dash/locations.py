from typing import Callable, Dict, List, NamedTuple, Optional, TYPE_CHECKING

from BaseClasses import Location
from . import game_data

if TYPE_CHECKING:
    from . import CliqueWorld


class MkddLocation(Location):
    game = "Mario Kart Double Dash"


class MkddLocationData():
    id_iterator = 2000
    def __init__(self, difficulty: int, region: str = "Menu", required_items: Dict[str, int] = {}, locked_item: str = "", no_id: bool = False):
        if no_id:
            self.id: int = 0
        else:
            self.id: int = MkddLocationData.id_iterator
            MkddLocationData.id_iterator += 1
        self.difficulty: int = difficulty
        self.region: str = region
        self.required_items: Dict[str, int] = required_items
        self.locked_item: str = locked_item

location_data_table: Dict[str, MkddLocationData] = {}

for cup in game_data.CUPS:
    location_data_table[cup + " Bronze"]        = MkddLocationData(0, cup)
    location_data_table[cup + " Silver"]        = MkddLocationData(1, cup)
    location_data_table[cup + " Gold 50cc"]     = MkddLocationData(2, cup)
    location_data_table[cup + " Gold 100cc"]    = MkddLocationData(5, cup, {"Progressive Mode":1})
    location_data_table[cup + " Gold 150cc"]    = MkddLocationData(10, cup, {"Progressive Mode":2})
    location_data_table[cup + " Gold Mirror"]   = MkddLocationData(10, cup, {"Progressive Mode":3})
    location_data_table[cup + " Perfect"]       = MkddLocationData(5, cup)

for course in game_data.COURSES:
    location_data_table[course + " 1st"]                = MkddLocationData(2, course + " GP")
    location_data_table[course + " Take The Lead"]      = MkddLocationData(1, course + " GP")
    location_data_table[course + " Defeat Staff Ghost"] = MkddLocationData(10, course + " TT")
    location_data_table[course + " Item Box"]           = MkddLocationData(0, course)

location_id_table: Dict[str, int] = {name:data.id for (name, data) in location_data_table.items() if data.id != 0}
locked_locations: Dict[str, MkddLocationData] = {name: data for name, data in location_data_table.items() if data.locked_item}
