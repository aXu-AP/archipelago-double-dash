"""
Archipelago init file for Mario Kart Double Dash!!
"""
import random
import math
from typing import Any

from BaseClasses import Region, ItemClassification
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, components, launch_subprocess
import warnings

from . import locations, items, regions
from .items import MkddItem
from .locations import MkddLocation
from .options import MkddOptions
from .regions import MkddRegionData
from .rules import MkddRules
from . import game_data

class MkddWebWorld(WebWorld):
    theme = "ocean"


class MkddWorld(World):
    """
    The fourth entry in Mario Kart series, Double Dash shakes up the gameplay by introducing 2 drivers per vehicle.
    """
    game = "Mario Kart Double Dash"
    web = MkddWebWorld()

    options_dataclass = MkddOptions
    options: MkddOptions

    item_name_to_id = items.name_to_id
    location_name_to_id = locations.name_to_id
    
    ut_can_gen_without_yaml = True

    def __init__(self, world, player):
        self.current_locations: list[MkddLocation] = []
        self.current_regions: dict[str, MkddRegionData] = {}
        super(MkddWorld, self).__init__(world, player)

    def create_regions(self) -> None:
        
        # Create regions.
        for region_name, region_data in regions.data_table.items():
            if region_name == "All Cup Tour" and self.options.all_cup_tour_length == 0:
                continue
            region = Region(region_name, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            self.current_regions[region_name] = region_data

        # Create locations.
        for region_name, region_data in self.current_regions.items():
            region = self.get_region(region_name)
            region.add_locations({
                location_data.name: id
                for id, location_data in enumerate(locations.data_table)
                if id > 0 and location_data.region == region_name
            }, MkddLocation)
            self.current_locations.extend([
                location_data
                for id, location_data in enumerate(locations.data_table)
                if id > 0 and location_data.region == region_name
            ])

            region.add_exits([exit for exit in region_data.connecting_regions if exit in self.current_regions.keys()])
            if region_name in game_data.CUPS:
                cup_no = game_data.CUPS.index(region_name)
                if cup_no < 4:
                    region.add_exits([game_data.COURSES[cup_no * 4 + i].name + " GP" for i in range(4)])
                else: # All Cup Tour
                    region.add_exits([c.name + " GP" for c in game_data.COURSES])

        self.get_location("Special Cup Gold 150cc").place_locked_item(self.create_item("Victory"))
        
    
    def create_items(self) -> None:
        # (item_name, count)
        precollected: list[str] = []
        # Give 1 cup, can't be All Star Cup.
        precollected.append(game_data.CUPS[self.random.randrange(4)])
        # Give 2 random characters to begin.
        precollected_characters = 0
        while precollected_characters < 2:
            character: str = game_data.CHARACTERS[self.random.randrange(len(game_data.CHARACTERS))].name
            if not character in precollected:
                precollected.append(character)
                precollected_characters += 1
        # Give 1 kart in each weight class.
        for weight in range(3):
            karts: list[str] = [kart.name for kart in game_data.KARTS if kart.weight == weight]
            precollected.append(karts[self.random.randrange(len(karts))])
        for item in precollected:
            self.multiworld.push_precollected(self.create_item(item))

        item_pool: list[MkddItem] = []
        for item in items.data_table:
            if item.classification != ItemClassification.filler:
                count = item.count
                count -= precollected.count(item.name)
                for i in range(count):
                    item_pool.append(self.create_item(item.name))
        
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        if len(item_pool) > total_locations:
            warnings.warn("Number of total available items exceeds the number of locations, likely there is a bug in the generation.")

        item_pool += [self.create_item(self.get_filler_item_name()) for _ in range(total_locations - len(item_pool))]
        
        self.multiworld.itempool += item_pool

    def create_item(self, name: str) -> MkddItem:
        id = items.name_to_id[name]
        item_data = items.data_table[id]
        return MkddItem(name, item_data.classification, id, self.player)

    def get_filler_item_name(self) -> str:
        return "Random Item"
    
    def set_rules(self) -> None:
        rules = MkddRules(self)
        rules.set_rules()
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")
    
    def fill_slot_data(self) -> dict[str, Any]:
        lap_counts = {course.name:course.laps for course in game_data.COURSES if course.type == game_data.CourseType.RACE}
        if self.options.shorter_courses:
            for course, laps in lap_counts.items():
                lap_counts[course] = int(math.ceil(laps * 2 / 3))
        for course, laps in self.options.custom_lap_counts.items():
            if laps > 0:
                lap_counts[course] = laps
        return {
            "lap_counts": lap_counts
        }


def launch_client():
    from .mkdd_client import main
    launch_subprocess(main, name="MKDD Client")


def add_client_to_launcher() -> None:
    version = "0.0.1"
    found = False
    for c in components:
        if c.display_name == "Mario Kart Double Dash Client":
            found = True
            if getattr(c, "version", 0) < version:
                c.version = version
                c.func = launch_client
                return
    if not found:
        components.append(Component("Mario Kart Double Dash Client", "MKDDClient", func=launch_client))


add_client_to_launcher()
