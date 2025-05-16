from typing import Dict, List, NamedTuple
from . import game_data

class MkddRegionData(NamedTuple):
    connecting_regions: List[str] = []

data_table: Dict[str, MkddRegionData] = {}

cup_regions: Dict[str, MkddRegionData] = {cup:MkddRegionData() for cup in game_data.CUPS}

course_regions: Dict[str, MkddRegionData] = {}
course_gp_regions: Dict[str, MkddRegionData] = {}
course_tt_regions: Dict[str, MkddRegionData] = {}
for course in game_data.COURSES:
    course_regions[course.name] = MkddRegionData()
    course_gp_regions[course.name + " GP"] = MkddRegionData([course.name])
    course_tt_regions[course.name + " TT"] = MkddRegionData([course.name])

data_table = {
    "Menu": MkddRegionData([region for region in {**cup_regions, **course_tt_regions}]),
    **cup_regions,
    **course_regions,
    **course_gp_regions,
    **course_tt_regions,
}