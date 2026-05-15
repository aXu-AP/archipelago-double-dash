from typing import NamedTuple, TYPE_CHECKING

from BaseClasses import Location
from . import game_data, items, version
from .locations_routes import ROUTE_LOCATIONS, get_loc_name_route

if TYPE_CHECKING:
    from . import MkddWorld


TAG_CUP_PERFECT = "Perfect Cup"
TAG_CUP_GOLD = "Gold Cup"
TAG_CUP_SILVER = "Silver Cup"
TAG_CUP_BRONZE = "Bronze Cup"
TAG_CUP_FINISH = "Finish Cup"
TAG_CUP_TROPHY = "Cup Trophy"
TAG_COURSE_FIRST = "Finish First"
TAG_COURSE_LEAD = "Take The Lead"
TAG_COURSE_FINISH = "Finish Course"
TAG_WIN_COMBO = "Win With Certain Characters"
TAG_TT = "Time Trial"
TAG_TT_GOOD = "Time Trial Good Time"
TAG_TT_GHOST = "Time Trial Staff Ghost"
TAG_ITEM_BOX = "Item Box"
TAG_SHORTCUT = "Shortcut"
TAG_ITEM_BOX_INTERESTING = "*Interesting Item Box" # Tags starting with * are for gen purposes only, not user facing.
TAG_ITEM_BOX_GROUP = "*Item Box Group"
TAG_ITEM_BOX_SANITY = "*Boxsanity Item Box"
TAG_ITEM_BOX_CUSTOM = "*Custom Item Box"
TAG_ITEM_BOX_REPLACEABLE = "*Replaceable Item Box"
TAG_REQUIRES_BOOST = "*Requires Boost"
TAG_CHAIN_CHOMP = "*Requires Chain Chomp"


class MkddLocation(Location):
    game = version.get_game_name()


class MkddLocationData(NamedTuple):
    name: str
    difficulty: int = 0
    region: str = "Menu"
    required_items: dict[str, int] = {}
    tags: set[str] = set()


def get_loc_name_cup(cup: str, ranking: int, vehicle_class: int) -> str:
    rank_name = ["Gold", "Silver", "Bronze"][ranking]
    class_name = ["50cc", "100cc", "150cc", "Mirror"][vehicle_class]
    return f"{cup} {rank_name} {class_name}"

def get_loc_name_trophy(cup: str, vehicle_class: int) -> str:
    class_name = ["50cc", "100cc", "150cc", "Mirror"][vehicle_class]
    return f"{cup} Gold {class_name} (Trophy)"

def get_loc_name_perfect(cup: str) -> str:
    return f"{cup} Perfect"

def get_loc_name_finish(course_or_cup: str) -> str:
    return f"{course_or_cup} Finish"

def get_loc_name_lead(course: str) -> str:
    return f"{course} Take The Lead"

def get_loc_name_first(course: str) -> str:
    return f"{course} 1st"

def get_loc_name_good_time(course: game_data.Course) -> str:
    seconds = course.good_time
    minutes = int(seconds / 60)
    seconds -= minutes * 60
    return f"{course.name} Time Trial in {minutes}:{seconds:02d}"

def get_loc_name_ghost(course: str) -> str:
    return f"{course} Defeat Staff Ghost"

def get_loc_name_win_char_kart(character: str, kart: str) -> str:
    return f"Win With {character} Driving {kart}"

def get_loc_name_win_characters(character1: str, character2: str) -> str:
    return f"Win With {character1} and {character2}"

def get_loc_name_win_course_char(course: game_data.Course) -> str:
    characters = [game_data.CHARACTERS[character].name for character in course.owners]
    if len(characters) == 1:
        return f"Win in {course.name} With {characters[0]}"
    else:
        return f"Win in {course.name} With {characters[0]} and {characters[1]}"


class ItemBoxGroup(NamedTuple):
    name: str
    count: int
    tags: set[str] = set()
    required_items: dict[str, int] = {}

BOX_NAMES: dict[str, list[ItemBoxGroup]] = {
    "Luigi Circuit": [
        ItemBoxGroup("First U-turn", 7),
        ItemBoxGroup("Last Turn", 5),
        ItemBoxGroup("50cc First Straight", 4),
        ItemBoxGroup("50cc Second Straight", 4),
        ItemBoxGroup("100cc Center", 4, required_items={items.PROGRESSIVE_CLASS:1}),
        ItemBoxGroup("100cc Chomp Shortcut", 2, {TAG_ITEM_BOX_INTERESTING}, {items.PROGRESSIVE_CLASS:1}),
        ItemBoxGroup("100cc Last Turn Shortcut", 2, {TAG_ITEM_BOX_INTERESTING}, {items.PROGRESSIVE_CLASS:1}),
    ],
    "Peach Beach": [
        ItemBoxGroup("Hidden Pipe", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("First Turn", 5),
        ItemBoxGroup("Beach Jump", 2, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Under Arc", 6),
        ItemBoxGroup("Ramp", 6),
        ItemBoxGroup("Fountain", 2, {TAG_ITEM_BOX_INTERESTING}),
    ],
    "Baby Park": [
        ItemBoxGroup("First Turn", 7),
        ItemBoxGroup("Second Turn", 7),
    ],
    "Dry Dry Desert": [
        ItemBoxGroup("Start", 4),
        ItemBoxGroup("First Turn", 5),
        ItemBoxGroup("Before Sand Pit", 4),
        ItemBoxGroup("After Sand Pit", 4),
        ItemBoxGroup("Between Pokeys", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Sand Hills", 5),
        ItemBoxGroup("Last Pokeys", 4),
    ],
    "Mushroom Bridge": [
        ItemBoxGroup("Left Lane", 2),
        ItemBoxGroup("Right Lane", 2),
        ItemBoxGroup("Pipe", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("First Tunnel", 3),
        ItemBoxGroup("Sidewalk", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Second Tunnel", 3),
        ItemBoxGroup("Bridge", 3),
        ItemBoxGroup("Bridge Top", 2, {TAG_ITEM_BOX_INTERESTING}),
    ],
    "Mario Circuit": [
        ItemBoxGroup("Start", 5),
        ItemBoxGroup("Before Tunnel", 4),
        ItemBoxGroup("Near Goombas", 6),
    ],
    "Daisy Cruiser": [
        ItemBoxGroup("First", 5),
        ItemBoxGroup("Dining Hall", 8),
        ItemBoxGroup("Cargo Hatch", 2),
        ItemBoxGroup("Cargo Area", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Deck", 5),
    ],
    "Waluigi Stadium": [
        ItemBoxGroup("Start", 4),
        ItemBoxGroup("First Jump", 1),
        ItemBoxGroup("Second Jump", 1),
        ItemBoxGroup("Near Big Puddle", 4),
        ItemBoxGroup("First Piranha", 4),
        ItemBoxGroup("Second Piranha", 4),
        ItemBoxGroup("After Piranhas", 4),
        ItemBoxGroup("Last Jump", 1, {TAG_ITEM_BOX_INTERESTING}),
    ],
    "Sherbet Land": [
        ItemBoxGroup("Start", 4),
        ItemBoxGroup("Tunnel Beginning", 3),
        ItemBoxGroup("Tunnel End", 3),
        ItemBoxGroup("After Tunnel", 3),
        ItemBoxGroup("Before Ice", 5),
        ItemBoxGroup("On Ice", 4),
    ],
    "Mushroom City": [
        ItemBoxGroup("Outer Route", 2),
        ItemBoxGroup("First Block", 1),
        ItemBoxGroup("Last Straight Left Lane", 2),
        ItemBoxGroup("Last Straight Right Lane", 3),
        ItemBoxGroup("Start", 4),
        ItemBoxGroup("Alley", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Crossroad", 1),
        ItemBoxGroup("After City", 4),
        ItemBoxGroup("Ramp", 3),
    ],
    "Yoshi Circuit": [
        ItemBoxGroup("First Turn", 4),
        ItemBoxGroup("Before Tunnel", 4),
        ItemBoxGroup("After Tunnel", 4),
        ItemBoxGroup("Before U-turn", 4),
        ItemBoxGroup("Tunnel Shortcut", 2, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Last Straight", 5),
    ],
    "DK Mountain": [
        ItemBoxGroup("Start", 4),
        ItemBoxGroup("Mountain Top", 4),
        ItemBoxGroup("Cliff U-turn", 4),
        ItemBoxGroup("Hairpin Turn", 5),
    ],
    "Wario Colosseum": [
        ItemBoxGroup("First Jump", 1),
        ItemBoxGroup("Second Jump", 1),
        ItemBoxGroup("Before Big Jump", 5),
        ItemBoxGroup("After Spiral", 4),
        ItemBoxGroup("Wide Curve", 5),
        ItemBoxGroup("Before Pit", 4),
        ItemBoxGroup("Pit Left", 2),
        ItemBoxGroup("Pit Jump", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Pit Right", 2),
        ItemBoxGroup("After Pit", 6),
        ItemBoxGroup("Last Jump", 4),
    ],
    "Dino Dino Jungle": [
        ItemBoxGroup("First Turn", 4),
        ItemBoxGroup("Over Logs", 2, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Under Dino", 4),
        ItemBoxGroup("Bridge", 2, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("Cave", 3),
        ItemBoxGroup("Cave Shortcut", 1, {TAG_ITEM_BOX_INTERESTING}),
        ItemBoxGroup("After Cave", 4),
        ItemBoxGroup("Last Straight", 4),
    ],
    "Bowser's Castle": [
        ItemBoxGroup("Entrance", 4),
        ItemBoxGroup("Lava Room Left", 2),
        ItemBoxGroup("Lava Room Right", 2),
        ItemBoxGroup("Spinning Fire", 4),
        ItemBoxGroup("Balcon", 4),
        ItemBoxGroup("Cannon Room First", 3),
        ItemBoxGroup("Cannon Room Second", 3),
    ],
    "Rainbow Road": [
        ItemBoxGroup("Downhill", 4),
        ItemBoxGroup("U-turn", 5),
        ItemBoxGroup("Spiral", 4),
        ItemBoxGroup("After Spiral", 4),
        ItemBoxGroup("Big Pipe", 5),
        ItemBoxGroup("Last Jump", 4),
    ],
}

def get_loc_name_item_box(course: str, group: int, number: int = -1) -> str:
    """Returns box name if number is defined. If no number, then returns group name."""
    group: ItemBoxGroup = BOX_NAMES[course][group]
    if group.count == 1:
        return f"{course} - {group.name} Box"
    elif number == -1:
        return f"{course} - {group.name} Boxes"
    else:
        return f"{course} - {group.name} Box {number + 1}"


class CustomItemBox(NamedTuple):
    name: str
    replaces_group: str
    replaces_number: int
    position: tuple[float, float, float]
    tags: set[str] = set()

CUSTOM_BOXES: dict[str, list[CustomItemBox]] = {
    "Peach Beach": [
        CustomItemBox("Behind Cargo", "Under Arc", 5, (-10870, 1360, 26570))
    ],
    "Yoshi Circuit": [
        CustomItemBox("Jump Shortcut", "Last Straight", 2, (-8000, 13400, 12100), {TAG_REQUIRES_BOOST})
    ],
}

def get_loc_name_custom_box(course: str, number: int) -> str:
    """Returns custom box name."""
    box: ItemBoxGroup = CUSTOM_BOXES[course][number]
    return f"{course} - {box.name} Box"


data_table: list[MkddLocationData] = [MkddLocationData("", 0)] # Id 0 is reserved.

# Cup related locations.
for cup in game_data.NORMAL_CUPS:
    data_table.append(MkddLocationData(get_loc_name_finish(cup), 0, cup, tags = {cup, TAG_CUP_FINISH}))
    data_table.append(MkddLocationData(get_loc_name_perfect(cup), 70, cup, tags = {cup, TAG_CUP_PERFECT}))
    # 50cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 0), 10, cup, tags = {cup, TAG_CUP_BRONZE}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 0), 20, cup, tags = {cup, TAG_CUP_SILVER}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 0), 40, cup, tags = {cup, TAG_CUP_GOLD}))
    data_table.append(MkddLocationData(get_loc_name_trophy(cup, 0), 40, cup, tags = {TAG_CUP_TROPHY}))
    # 100cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 1), 40, cup, {items.PROGRESSIVE_CLASS:1}, {cup, TAG_CUP_BRONZE}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 1), 60, cup, {items.PROGRESSIVE_CLASS:1}, {cup, TAG_CUP_SILVER}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 1), 70, cup, {items.PROGRESSIVE_CLASS:1}, {cup, TAG_CUP_GOLD}))
    data_table.append(MkddLocationData(get_loc_name_trophy(cup, 1), 70, cup, {items.PROGRESSIVE_CLASS:1}, {TAG_CUP_TROPHY}))
    # 150cc
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 2), 60, cup, {items.PROGRESSIVE_CLASS:2}, {cup, TAG_CUP_BRONZE}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 2), 80, cup, {items.PROGRESSIVE_CLASS:2}, {cup, TAG_CUP_SILVER}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 2), 90, cup, {items.PROGRESSIVE_CLASS:2}, {cup, TAG_CUP_GOLD}))
    data_table.append(MkddLocationData(get_loc_name_trophy(cup, 2), 90, cup, {items.PROGRESSIVE_CLASS:2}, {TAG_CUP_TROPHY}))
    # Mirror
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 2, 3), 70, cup, {items.PROGRESSIVE_CLASS:3}, {cup, TAG_CUP_BRONZE}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 1, 3), 90, cup, {items.PROGRESSIVE_CLASS:3}, {cup, TAG_CUP_SILVER}))
    data_table.append(MkddLocationData(get_loc_name_cup(cup, 0, 3), 100, cup, {items.PROGRESSIVE_CLASS:3}, {cup, TAG_CUP_GOLD}))
    data_table.append(MkddLocationData(get_loc_name_trophy(cup, 3), 100, cup, {items.PROGRESSIVE_CLASS:3}, {TAG_CUP_TROPHY}))

# Course related locations.
for course in game_data.RACE_COURSES:
    data_table.append(MkddLocationData(get_loc_name_finish(course.name), 0, course.name, tags = {course.name, TAG_COURSE_FINISH}))
    data_table.append(MkddLocationData(get_loc_name_lead(course.name), 30, course.name + " GP", tags = {course.name, TAG_COURSE_LEAD}))
    data_table.append(MkddLocationData(get_loc_name_first(course.name), 40, course.name + " GP", tags = {course.name, TAG_COURSE_FIRST}))
    data_table.append(MkddLocationData(get_loc_name_good_time(course), 70, course.name + " TT", tags = {course.name, TAG_TT, TAG_TT_GOOD}))
    data_table.append(MkddLocationData(get_loc_name_ghost(course.name), 120, course.name + " TT", tags = {course.name, TAG_TT, TAG_TT_GHOST}))

# Win with default character pairs.
for character_id in range(0, len(game_data.CHARACTERS), 2):
    character1 = game_data.CHARACTERS[character_id]
    character2 = game_data.CHARACTERS[character_id + 1]
    data_table.append(MkddLocationData(get_loc_name_win_characters(character1.name, character2.name), 40, "Menu", {character1.name:1, character2.name:1}, {TAG_WIN_COMBO}))

# Win with a default kart + character combination.
for character in game_data.CHARACTERS:
    kart = game_data.KARTS[character.default_kart]
    data_table.append(MkddLocationData(get_loc_name_win_char_kart(character.name, kart.name), 40, "Menu", {character.name:1, kart.name:1}, {TAG_WIN_COMBO}))

# Win courses with certain characters.
for course in [course for course in game_data.RACE_COURSES if len(course.owners) > 0]:
    data_table.append(MkddLocationData(get_loc_name_win_course_char(course), 40, course.name + " GP", {game_data.CHARACTERS[o].name:1 for o in course.owners}, {course.name, TAG_WIN_COMBO}))

# Misc locations.
GOLD_LIGHT = "Win Gold With a Light Kart"
GOLD_MEDIUM = "Win Gold With a Medium Kart"
GOLD_HEAVY = "Win Gold With a Heavy Kart"
GOLD_PARADE = "Win Gold With Parade Kart"
TROPHY_GOAL = "Trophy Goal Completed"
WIN_ALL_CUP_TOUR = "All Cup Tour Gold"

# Don't define difficulty here, it will be handled by rules.
data_table.append(MkddLocationData(GOLD_LIGHT, 0))
data_table.append(MkddLocationData(GOLD_MEDIUM, 0))
data_table.append(MkddLocationData(GOLD_HEAVY, 0))
data_table.append(MkddLocationData(GOLD_PARADE, 40, required_items = {"Parade Kart":1}))
data_table.append(MkddLocationData(TROPHY_GOAL, 0))
data_table.append(MkddLocationData(WIN_ALL_CUP_TOUR, 0, game_data.CUPS[game_data.CUP_ALL_CUP_TOUR]))

# Item Box locations.
for course, box_groups in BOX_NAMES.items():
    custom_boxes = CUSTOM_BOXES.get(course, [])
    for i, group in enumerate(box_groups):
        tags: set[str] = {course, TAG_ITEM_BOX}
        if group.count > 1: # Don't add group and box separately if it's just one.
            for j in range(group.count):
                box_tags = tags.copy() | {TAG_ITEM_BOX_SANITY}
                if any(cb.replaces_group == group.name and cb.replaces_number == j for cb in custom_boxes):
                    box_tags.add(TAG_ITEM_BOX_REPLACEABLE)
                data_table.append(MkddLocationData(get_loc_name_item_box(course, i, j), 0, f"{course} GP", group.required_items, tags=box_tags))
        else:
            tags.add(TAG_ITEM_BOX_SANITY) # Just add one location with both tags.
        data_table.append(MkddLocationData(get_loc_name_item_box(course, i), 0, f"{course} GP", group.required_items, tags=tags | group.tags | {TAG_ITEM_BOX_GROUP}))
    for idx, box in enumerate(custom_boxes):
        data_table.append(MkddLocationData(
                get_loc_name_custom_box(course, idx), 0, f"{course} GP",
                tags={course, TAG_ITEM_BOX, TAG_ITEM_BOX_GROUP, TAG_ITEM_BOX_INTERESTING, TAG_ITEM_BOX_SANITY, TAG_ITEM_BOX_CUSTOM} | box.tags))

for course, routes in ROUTE_LOCATIONS.items():
    for route in routes:
        data_table.append(MkddLocationData(get_loc_name_route(course, route), 0, course, tags={course, TAG_SHORTCUT} | route.tags))

name_to_id: dict[str, int] = {data.name:id for (id, data) in enumerate(data_table) if id > 0}

group_names: set[str] = set()
for data in data_table:
    group_names.update({tag for tag in data.tags if not tag.startswith("*")})
groups: dict[str: set[str]] = {
    group:{data.name for data in data_table if group in data.tags} 
    for group in group_names
}