from typing import Dict, List, NamedTuple
from . import game_data

class MkddRegionData(NamedTuple):
    connecting_regions: List[str] = []

region_data_table: Dict[str, MkddRegionData] = {}

# for cup in game_data.CUPS:
#     region_data_table[cup] = MkddRegionData()
cup_regions: Dict[str, MkddRegionData] = {cup:MkddRegionData() for cup in game_data.CUPS}

course_regions: Dict[str, MkddRegionData] = {}
course_gp_regions: Dict[str, MkddRegionData] = {}
course_tt_regions: Dict[str, MkddRegionData] = {}
for course in game_data.COURSES:
    course_regions[course] = MkddRegionData()
    course_gp_regions[course + " GP"] = MkddRegionData([course])
    course_tt_regions[course + " TT"] = MkddRegionData([course])

region_data_table = {
    "Menu": MkddRegionData([region for region in {**cup_regions, **course_tt_regions}]),
    **cup_regions,
    **course_regions,
    **course_gp_regions,
    **course_tt_regions,
}