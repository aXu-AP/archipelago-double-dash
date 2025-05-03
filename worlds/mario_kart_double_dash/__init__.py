"""
Archipelago init file for Mario Kart Double Dash!!
"""
import random
from typing import List, Dict, Any

from BaseClasses import Region, ItemClassification
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, components, launch_subprocess
import warnings

from .items import MkddItem, item_data_table, item_id_table
from .locations import MkddLocation, location_data_table, location_id_table, locked_locations
from .options import MkddOptions
from .regions import region_data_table
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

    item_name_to_id = item_id_table
    location_name_to_id = location_id_table

    def create_regions(self) -> None:
        # Create regions.
        for region_name in region_data_table.keys():
            region = Region(region_name, self.player, self.multiworld)
            self.multiworld.regions.append(region)

        # Create locations.
        for region_name, region_data in region_data_table.items():
            region = self.get_region(region_name)
            region.add_locations({
                location_name: location_data.id for location_name, location_data in location_data_table.items()
                if location_data.region == region_name
            }, MkddLocation)
            region.add_exits(region_data_table[region_name].connecting_regions)
            if region_name in game_data.CUPS:
                cup_no = game_data.CUPS.index(region_name)
                if cup_no < 4: # Exclude All Cup Tour.
                    region.add_exits([game_data.COURSES[cup_no * 4 + i] + " GP" for i in range(4)])

        # Place locked locations.
        for location_name, location_data in locked_locations.items():
            locked_item = self.create_item(location_data.locked_item)
            self.get_location(location_name).place_locked_item(locked_item)
        
        self.get_location("Special Cup Gold 150cc").place_locked_item(self.create_item("Victory"))
        
    
    def create_items(self) -> None:
        item_pool: List[MkddItem] = []
        for name, item in item_data_table.items():
            if item.id and item.classification != ItemClassification.filler:
                count = item.count
                for (loc_name, loc_data) in locked_locations.items():
                    if loc_data.locked_item == name:
                        count -= 1
                for i in range(count):
                    item_pool.append(self.create_item(name))
        
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        if len(item_pool) > total_locations:
            warnings.warn("Number of total available items exceeds the number of locations, likely there is a bug in the generation.")

        item_pool += [self.create_item(self.get_filler_item_name()) for _ in range(total_locations - len(item_pool))]
        
        self.multiworld.itempool += item_pool
        self.multiworld.push_precollected(self.create_item("Mushroom Cup"))

    def create_item(self, name: str) -> MkddItem:
        item_data = item_data_table[name]
        return MkddItem(name, item_data.classification, item_data.id, self.player)

    def get_filler_item_name(self) -> str:
        return "Random Item"
    
    def set_rules(self) -> None:
        rules = MkddRules(self)
        rules.set_rules()
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")

# def launch_client():
#     from .MkddClient import main
#     launch_subprocess(main, name="MKDD client")


# def add_client_to_launcher() -> None:
#     version = "0.2.0"
#     found = False
#     for c in components:
#         if c.display_name == "Mario Kart Double Dash Client":
#             found = True
#             if getattr(c, "version", 0) < version:
#                 c.version = version
#                 c.func = launch_client
#                 return
#     if not found:
#         components.append(Component("Mario Kart Double Dash Client", "MKDDClient",
#                                     func=launch_client))


# add_client_to_launcher()
