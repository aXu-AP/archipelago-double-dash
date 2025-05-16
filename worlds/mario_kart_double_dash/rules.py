from typing import Callable, TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule, CollectionRule
from . import locations, items, regions, game_data

if TYPE_CHECKING:
    from . import MkddWorld


class MkddRules:
    def __init__(self, world: "MkddWorld") -> None:
        self.player = world.player
        self.world = world
    
    def set_loc_rule(self, location_name: str, rule: CollectionRule) -> None:
        location = self.world.multiworld.get_location(location_name, self.player)
        set_rule(location, rule)

    def add_loc_rule(self, location_name: str, rule: CollectionRule, combine: str = "and") -> None:
        location = self.world.multiworld.get_location(location_name, self.player)
        add_rule(location, rule, combine)

    def set_ent_rule(self, entrance_name: str, rule: CollectionRule) -> None:
        entrance = self.world.multiworld.get_entrance(entrance_name, self.player)
        set_rule(entrance, rule)

    def set_rules(self) -> None:
        for location in self.world.current_locations:
            for item, count in location.required_items.items():
                self.add_loc_rule(location.name, lambda state, item = item, count = count: state.has(item, self.player, count))

        for cup in game_data.CUPS:
            # Exclude All Cup Tour
            if cup == "All Cup Tour" and self.world.options.all_cup_tour_length == 0:
                continue
            self.set_ent_rule(f"Menu -> {cup}", lambda state, cup = cup: state.has(cup, self.player))

        for course in game_data.COURSES:
            self.set_ent_rule(f"Menu -> {course.name} TT", lambda state, course = course.name: state.has(f"{course} Time Trial", self.player))
