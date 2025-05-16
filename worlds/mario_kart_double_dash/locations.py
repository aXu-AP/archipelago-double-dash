from typing import TYPE_CHECKING

from BaseClasses import Location
from . import game_data

if TYPE_CHECKING:
    from . import MkddWorld


class MkddLocation(Location):
    game = "Mario Kart Double Dash"


class MkddLocationData():
    def __init__(self, name:str, difficulty: int, region: str = "Menu", required_items: dict[str, int] = {}, locked_item: str = "", no_id: bool = False):
        self.name: str = name
        self.difficulty: int = difficulty
        self.region: str = region
        self.required_items: dict[str, int] = required_items
        self.locked_item: str = locked_item

def get_loc_name_cup(cup: str, ranking: int, vehicle_class: int):
    try:
        rank_name = ["Gold", "Silver", "Bronze"][ranking]
        class_name = ["50cc", "100cc", "150cc", "Mirror"][vehicle_class]
        return f"{cup} {rank_name} {class_name}"
    except:
        return ""

def get_loc_name_perfect(cup: str):
    return f"{cup} Perfect"

def get_loc_name_finish(course_or_cup: str):
    return f"{course_or_cup} Finish"

def get_loc_name_lead(course: str):
    return f"{course} Take The Lead"

def get_loc_name_first(course: str):
    return f"{course} 1st"

def get_loc_name_ghost(course: str):
    return f"{course} Defeat Staff Ghost"


data_table: list[MkddLocationData] = [MkddLocationData("", 0)] # Id 0 is reserved.

for cup in game_data.CUPS:
    data_table.append(MkddLocationData(get_loc_name_finish(cup), 0, cup))
    data_table.append(MkddLocationData(get_loc_name_perfect(cup), 5, cup))
    # 50cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 0),  0, cup))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 0),  1, cup))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 0),  2, cup))
    # 100cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 1),  0, cup, {"Progressive Class":1}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 1),  1, cup, {"Progressive Class":1}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 1),  5, cup, {"Progressive Class":1}))
    # 150cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 2),  3, cup, {"Progressive Class":2}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 2),  8, cup, {"Progressive Class":2}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 2), 10, cup, {"Progressive Class":2}))
    # Mirror
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 3),  7, cup, {"Progressive Class":3}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 3), 10, cup, {"Progressive Class":3}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 3), 15, cup, {"Progressive Class":3}))

for course in game_data.COURSES:
    if course.type == game_data.CourseType.RACE:
        data_table.append(MkddLocationData(get_loc_name_finish(course.name), 0, course.name))
        data_table.append(MkddLocationData(get_loc_name_lead(course.name), 1, course.name + " GP"))
        data_table.append(MkddLocationData(get_loc_name_first(course.name), 2, course.name + " GP"))
        data_table.append(MkddLocationData(get_loc_name_ghost(course.name), 10, course.name + " TT"))

name_to_id: dict[str, int] = {data.name:id for (id, data) in enumerate(data_table) if id > 0}
