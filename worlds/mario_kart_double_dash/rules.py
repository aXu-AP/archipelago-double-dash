from typing import TYPE_CHECKING

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
            if len(location.required_items) > 0:
                self.add_loc_rule(location.name,
                        lambda state, items = location.required_items: state.has_all_counts(items, self.player))

        for cup in game_data.CUPS:
            # Exclude All Cup Tour
            if cup == "All Cup Tour" and self.world.options.all_cup_tour_length == 0:
                continue
            self.set_ent_rule(f"Menu -> {cup}",
                    lambda state, cup = cup: state.has(cup, self.player))

        for course in game_data.COURSES:
            self.set_ent_rule(f"Menu -> {course.name} TT",
                    lambda state, course = course.name: state.has(f"{course} Time Trial", self.player))
        
        for course in [course for course in game_data.COURSES if len(course.owners) > 0]:
            owners: list[str] = [game_data.CHARACTERS[character].name for character in course.owners]
            self.add_loc_rule(locations.get_loc_name_win_course_char(course),
                    lambda state, owners = owners: state.has_any(owners, self.player))

        # Locations which require certain karts to be playable.
        light_kart_locs = [locations.GOLD_LIGHT]
        medium_kart_locs = [locations.GOLD_MEDIUM]
        heavy_kart_locs = [locations.GOLD_HEAVY]
        for character in game_data.CHARACTERS:
            kart = game_data.KARTS[character.default_kart]
            if kart.weight == 0:
                light_kart_locs.append(locations.get_loc_name_win_char_kart(character.name, kart.name))
            elif kart.weight == 1:
                medium_kart_locs.append(locations.get_loc_name_win_char_kart(character.name, kart.name))
            elif kart.weight == 2:
                heavy_kart_locs.append(locations.get_loc_name_win_char_kart(character.name, kart.name))
        
        # Has at least 2 light characters.
        for loc in light_kart_locs:
            self.add_loc_rule(loc,
                    lambda state: state.has_from_list([character.name for character in game_data.CHARACTERS if character.weight == 0], self.player, 2))
        
        # Has at least 1 medium character and another medium or light character.
        for loc in medium_kart_locs:
            self.add_loc_rule(loc,
                    lambda state:
                        (state.has_any([character.name for character in game_data.CHARACTERS if character.weight == 1], self.player) and
                        state.has_any([character.name for character in game_data.CHARACTERS if character.weight == 0], self.player)) or \
                        state.has_from_list([character.name for character in game_data.CHARACTERS if character.weight == 1], self.player, 2)
            )
        
        # Has at least 1 heavy character.
        for loc in heavy_kart_locs:
            self.add_loc_rule(loc,
                    lambda state: state.has_any([character.name for character in game_data.CHARACTERS if character.weight == 2], self.player))
