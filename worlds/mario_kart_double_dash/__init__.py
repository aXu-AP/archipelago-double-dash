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
from .locations import MkddLocation, MkddLocationData
from .options import MkddOptions
from .regions import MkddRegionData
from .rules import MkddRules
from . import game_data, version

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
    location_name_groups = locations.groups    

    ut_can_gen_without_yaml = True

    def __init__(self, world, player):
        self.current_locations: list[MkddLocationData] = []
        self.current_regions: dict[str, MkddRegionData] = {}
        self.current_entrances: set[str] = set()
        
        self.cups_courses: list[list[int]] = []
        self.character_item_total_weights: dict[str, list[int]] = {}
        self.global_items_total_weights: list[int] = []
        super(MkddWorld, self).__init__(world, player)

    def generate_early(self):
        if hasattr(self.multiworld, "re_gen_passthrough"):
            slot_data = self.multiworld.re_gen_passthrough["Mario Kart Double Dash"]
            self.options.logic_difficulty = slot_data["logic_difficulty"]

    def create_regions(self) -> None:
        # Course shuffle (entrance rando). If using Universal Tracker, get shuffled tracks from slot data.
        # Course order is kept in a list[list[int]], where first index is cup, and second index points to a course inside that cup.
        if hasattr(self.multiworld, "re_gen_passthrough"):
            slot_data = self.multiworld.re_gen_passthrough["Mario Kart Double Dash"]
            self.cups_courses = slot_data["cups_courses"]
        else:
            all_courses: list[int] = list(range(16))
            if self.options.course_shuffle == options.CourseShuffle.option_shuffle_once:
                self.random.shuffle(all_courses)
            self.cups_courses: list[list[int]] = []
            for i in range(0, 16, 4):
                self.cups_courses.append([
                    all_courses[i],
                    all_courses[i + 1],
                    all_courses[i + 2],
                    all_courses[i + 3],
                ])

        # Create regions.
        for region_name, region_data in regions.data_table.items():
            if self.options.goal == options.Goal.option_trophies and region_name == game_data.CUPS[game_data.CUP_ALL_CUP_TOUR]:
                continue
            region = Region(region_name, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            self.current_regions[region_name] = region_data

        for region_name, region_data in self.current_regions.items():
            # Connect regions.
            region = self.get_region(region_name)
            region.add_exits([exit for exit in region_data.connecting_regions if exit in self.current_regions.keys()])
            if region_name in game_data.NORMAL_CUPS:
                cup_no = game_data.CUPS.index(region_name)
                region.add_exits([game_data.RACE_COURSES[self.cups_courses[cup_no][i]].name + " GP" for i in range(4)])
            if region_name == game_data.CUPS[game_data.CUP_ALL_CUP_TOUR]:
                region.add_exits([c.name + " GP" for c in game_data.RACE_COURSES])
            self.current_entrances.update([e.name for e in region.exits])

            # Create locations.
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
        
        # Locked items.
        for cup in game_data.NORMAL_CUPS:
            for vehicle_class in range(4):
                self.get_location(locations.get_loc_name_trophy(cup, vehicle_class))\
                    .place_locked_item(self.create_item(items.TROPHY))
        if self.options.goal == options.Goal.option_all_cup_tour:
            self.get_location(locations.TROPHY_GOAL).place_locked_item(self.create_item(game_data.CUPS[game_data.CUP_ALL_CUP_TOUR]))
            self.get_location(locations.WIN_ALL_CUP_TOUR).place_locked_item(self.create_item("Victory"))
        elif self.options.goal == options.Goal.option_trophies:
            self.get_location(locations.TROPHY_GOAL).place_locked_item(self.create_item("Victory"))
        
    
    def create_items(self) -> None:
        # (item_name, count)
        precollected: list[str] = []
        # Give 1 cup, can't be All Star Cup.
        precollected.append(self.random.choice(game_data.NORMAL_CUPS))
        # Give 2 random characters to begin.
        precollected_characters = 0
        while precollected_characters < 2:
            character_name: str = self.random.choice(game_data.CHARACTERS).name
            if not character_name in precollected:
                precollected.append(character_name)
                precollected_characters += 1
        # Give 1 kart in each weight class.
        for weight in range(3):
            karts: list[str] = [kart.name for kart in game_data.KARTS if kart.weight == weight]
            precollected.append(self.random.choice(karts))
        for item in precollected:
            self.multiworld.push_precollected(self.create_item(item))

        # Generic items by predetermined counts.
        item_pool: list[MkddItem] = []
        for item in items.data_table:
            if item.classification != ItemClassification.filler:
                count = item.count
                count -= precollected.count(item.name)
                for i in range(count):
                    item_pool.append(self.create_item(item.name))
        
        # Kart upgrades generation.
        kart_weights = [5 for _ in game_data.KARTS]
        upgrade_weights = [math.ceil(self.options.kart_upgrades / len(game_data.KART_UPGRADES)) for _ in game_data.KART_UPGRADES]
        up_karts = self.random.sample(game_data.KARTS, self.options.kart_upgrades, counts = kart_weights)
        upgrades = self.random.sample(game_data.KART_UPGRADES, self.options.kart_upgrades, counts = upgrade_weights)
        for i in range(self.options.kart_upgrades):
            item_pool.append(self.create_item(items.get_item_name_kart_upgrade(upgrades[i].name, up_karts[i].name)))

        # Item box item generation.
        # Give mostly bad items as global items.
        items_left: list[game_data.Item] = [item for item in game_data.ITEMS if item != game_data.ITEM_NONE]
        weights: list[str] = [1000 - item.usefulness ** 3 for item in game_data.ITEMS if item != game_data.ITEM_NONE]
        global_items: list[game_data.Item] = []
        for i in range(self.options.items_for_everybody):
            item = self.random.sample(items_left, 1, counts = weights)[0]
            item_pool.append(self.create_item(items.get_item_name_character_item(None, item.name)))
            global_items.append(item)
            id = items_left.index(item)
            items_left.pop(id)
            weights.pop(id)

        # Ensure that every item is in pool at least once.
        items_left_characters_pool = items_left.copy()
        weights = [1 for _ in items_left]
        items_per_character: dict[game_data.Character, list[game_data.Item]] = {character:[] for character in game_data.CHARACTERS}
        for i in range(self.options.items_per_character):
            for character in game_data.CHARACTERS:
                # Try rolling for unique items.
                for j in range(50):
                    item = self.random.sample(items_left, 1, counts = weights)[0]
                    if not item in items_per_character[character]:
                        break
                    # If item hasn't been found after 10 tries, try refilling the pool.
                    elif j == 10:
                        items_left = items_left_characters_pool.copy()
                        weights = [10 - item.usefulness for item in items_left]

                items_per_character[character].append(item)
                item_pool.append(self.create_item(items.get_item_name_character_item(character.name, item.name)))
                id = items_left.index(item)
                weights[id] -= 1
                if weights[id] == 0:
                    items_left.pop(id)
                    weights.pop(id)
                if len(items_left) == 0:
                    # Refill the pool with some balancing.
                    items_left = items_left_characters_pool.copy()
                    weights = [10 - item.usefulness for item in items_left]

        self.character_item_total_weights = {character.name:[] for character in game_data.CHARACTERS}
        for i in range(8):
            self.global_items_total_weights.append(sum([item.weight_table[i] for item in global_items]))
            for character in game_data.CHARACTERS:
                self.character_item_total_weights[character.name].append(
                    sum([item.weight_table[i] for item in items_per_character[character]])
                )

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
        return items.RANDOM_ITEM
    
    def set_rules(self) -> None:
        rules = MkddRules(self)
        rules.set_rules()
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
    
    def collect(self, state, item) -> bool:
        change = super().collect(state, item)
        if change:
            rules.add_item(state, self.player, item)
        return change

    def remove(self, state, item) -> bool:
        change = super().remove(state, item)
        if change:
            rules.add_item(state, self.player, item, -1)
        return change

    def fill_slot_data(self) -> dict[str, Any]:
        lap_counts = {course.name:course.laps for course in game_data.RACE_COURSES}
        if self.options.shorter_courses:
            for course, laps in lap_counts.items():
                lap_counts[course] = int(math.ceil(laps * 2 / 3))
        for course, laps in self.options.custom_lap_counts.items():
            if laps > 0:
                lap_counts[course] = laps
        return {
            "version": version.get_str(),
            "trophy_amount": int(self.options.trophy_amount),
            "logic_difficulty": int(self.options.logic_difficulty) if not self.options.tracker_unrestricted_logic else 100,
            "cups_courses": self.cups_courses,
            "all_cup_tour_length": int(self.options.all_cup_tour_length),
            "mirror_200cc": int(self.options.mirror_200cc),
            "lap_counts": lap_counts,
            "character_item_total_weights": self.character_item_total_weights,
            "global_items_total_weights": self.global_items_total_weights,
        }
    
    # Rerun Universal Tracker with received options.
    @staticmethod
    def interpret_slot_data(slot_data: dict[str:Any]) -> dict[str:Any]:
        return slot_data


def launch_client():
    from .mkdd_client import main
    launch_subprocess(main, name="MKDD Client")


def add_client_to_launcher() -> None:
    found = False
    for c in components:
        if c.display_name == "Mario Kart Double Dash Client":
            found = True
            if getattr(c, "version", 0) < version.get_str():
                c.version = version.get_str()
                c.func = launch_client
                return
    if not found:
        components.append(Component("Mario Kart Double Dash Client", "MKDDClient", func=launch_client))


add_client_to_launcher()
