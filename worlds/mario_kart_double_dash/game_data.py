from enum import IntEnum
from typing import NamedTuple


class Character(NamedTuple):
    name: str
    weight: int
    default_kart: int

CHARACTERS = [
    Character("Mario", 1, 8),           # 00
    Character("Luigi", 1, 9),           # 01
    Character("Peach", 1, 10),          # 02
    Character("Daisy", 1, 11),          # 03
    Character("Yoshi", 1, 12),          # 04
    Character("Birdo", 1, 13),          # 05
    Character("Baby Mario", 0, 0),      # 06
    Character("Baby Luigi", 0, 1),      # 07
    Character("Toad", 0, 6),            # 08
    Character("Toadette", 0, 7),        # 09
    Character("Koopa", 0, 2),           # 10
    Character("Paratroopa", 0, 3),      # 11
    Character("Donkey Kong", 2, 16),    # 12
    Character("Diddy Kong", 0, 4),      # 13
    Character("Bowser", 2, 17),         # 14
    Character("Bowser Jr.", 0, 5),      # 15
    Character("Wario", 2, 15),          # 16
    Character("Waluigi", 1, 14),        # 17
    Character("Petey Piranha", 2, 18),  # 18
    Character("King Boo", 2, 19),       # 19
]

class Kart(NamedTuple):
    name: str
    weight: int
    unlock_id: int

KARTS = [
    Kart("Goo-Goo Buggy", 0, 5),        # 00
    Kart("Rattle Buggy", 0, 13),        # 01
    Kart("Koopa Dasher", 0, 3),         # 02
    Kart("Para-Wing", 0, 11),           # 03
    Kart("Barrel Train", 0, 9),         # 04
    Kart("Bullet Blaster", 0, 15),      # 05
    Kart("Toad Kart", 0, 16),           # 06
    Kart("Toadette Kart", 0, 17),       # 07
    Kart("Red Fire", 1, 0),             # 08
    Kart("Green Fire", 1, 8),           # 09
    Kart("Heart Coach", 1, 4),          # 10
    Kart("Bloom Coach", 1, 12),         # 11
    Kart("Turbo Yoshi", 1, 2),          # 12
    Kart("Turbo Birdo", 1, 10),         # 13
    Kart("Waluigi Racer", 1, 14),       # 14
    Kart("Wario Car", 2, 6),            # 15
    Kart("DK Jumbo", 2, 1),             # 16
    Kart("Koopa King", 2, 7),           # 17
    Kart("Piranha Pipes", 2, 19),       # 18
    Kart("Boo Pipes", 2, 18),           # 19
    Kart("Parade Kart", -1, 20),        # 20
]

CUPS = [
    "Mushroom Cup",
    "Flower Cup",
    "Star Cup",
    "Special Cup",
    "All Cup Tour",
]

class CourseType(IntEnum):
    RACE = 0
    BATTLE = 1
    CEREMONY = 2

class Course(NamedTuple):
    name: str = ""
    id: int = -1
    type: CourseType = CourseType.RACE
    staff_time: float = 0
    good_time: float = 0
    owners: list[int] = []
    laps: int = 3


COURSES = [
    # Race courses:
    Course("Luigi Circuit",     0x24, staff_time =  86.277, good_time = 95, owners = [1]),
    Course("Peach Beach",       0x22, staff_time =  80.404, good_time = 90, owners = [2]),
    Course("Baby Park",         0x21, staff_time =  71.108, good_time = 80, owners = [6, 7], laps = 7),
    Course("Dry Dry Desert",    0x32, staff_time = 110.755, good_time = 120),
    Course("Mushroom Bridge",   0x28, staff_time =  91.458, good_time = 100),
    Course("Mario Circuit",     0x25, staff_time = 101.384, good_time = 115, owners = [0]),
    Course("Daisy Cruiser",     0x23, staff_time = 112.207, good_time = 120, owners = [3]),
    Course("Waluigi Stadium",   0x2a, staff_time = 119.658, good_time = 130, owners = [17]),
    Course("Sherbet Land",      0x33, staff_time =  85.904, good_time = 100),
    Course("Mushroom City",     0x29, staff_time = 110.663, good_time = 120),
    Course("Yoshi Circuit",     0x26, staff_time = 119.866, good_time = 135, owners = [4]),
    Course("DK Mountain",       0x2d, staff_time = 132.639, good_time = 140, owners = [12]),
    Course("Wario Colosseum",   0x2b, staff_time = 141.106, good_time = 155, owners = [16], laps = 2),
    Course("Dino Dino Jungle",  0x2c, staff_time = 120.908, good_time = 140),
    Course("Bowser's Castle",   0x2f, staff_time = 164.690, good_time = 185, owners = [14]),
    Course("Rainbow Road",      0x31, staff_time = 196.476, good_time = 210),
    # Battle courses:
    Course("Cookie Land", 0x3a, CourseType.BATTLE),
    Course("Pipe Plaza", 0x3b, CourseType.BATTLE),
    Course("Block City", 0x36, CourseType.BATTLE),
    Course("Nintendo Gamecube", 0x35, CourseType.BATTLE),
    Course("Luigi's Mansion", 0x34, CourseType.BATTLE),
    Course("Tilt-A-Kart", 0x38, CourseType.BATTLE),
    # Award Ceremony
    Course("Award Ceremony", 0x44, CourseType.CEREMONY),
]

class Modes(IntEnum):
    TIMETRIAL = 1
    GRANDPRIX = 2
    VERSUS = 3
    BATTLE_BALLOON = 4
    BATTLE_SHINE = 7
    BATTLE_BOMB = 6
    CEREMONY = 8

class Item(NamedTuple):
    id: int
    name: str
    usefulness: int = 0

ITEMS = [
    Item(0, "Green Shell"),
    Item(1, "Bowser's Shell"),
    Item(2, "Red Shell"),
    Item(3, "Banana"),
    Item(4, "Giant Banana"),
    Item(5, "Mushroom"),
    Item(6, "Star"),
    Item(7, "Chain Chomp"),
    Item(8, "Bob-omb"),
    Item(9, "Fireball"),
    Item(10, "Lightning"),
    Item(11, "Yoshi Egg"),
    Item(12, "Golden Mushroom"),
    Item(13, "Spiny Shell"),
    Item(14, "Heart"),
    Item(15, "Fake Item"),
    Item(17, "Triple Green Shells"),
    Item(18, "Triple Mushrooms"),
    Item(19, "Triple Red Shells"),
    Item(21, "Fireballs"),
    Item(16, "None"),
]

ITEM_GREEN_SHELL = ITEMS[0]
ITEM_BOWSER_SHELL = ITEMS[1]
ITEM_RED_SHELL = ITEMS[2]
ITEM_BANANA = ITEMS[3]
ITEM_GIANT_BANANA = ITEMS[4]
ITEM_MUSHROOM = ITEMS[5]
ITEM_STAR = ITEMS[6]
ITEM_CHAIN_CHOMP = ITEMS[7]
ITEM_BOBOMB = ITEMS[8]
ITEM_FIREBALL = ITEMS[9]
ITEM_LIGHTNING = ITEMS[10]
ITEM_YOSHI_EGG = ITEMS[11]
ITEM_GOLDEN_MUSHROOM = ITEMS[12]
ITEM_SPINY_SHELL = ITEMS[13]
ITEM_HEART = ITEMS[14]
ITEM_FAKE_ITEM = ITEMS[15]
ITEM_TRIPLE_GREEN_SHELLS = ITEMS[16]
ITEM_TRIPLE_MUSHROOMS = ITEMS[17]
ITEM_TRIPLE_RED_SHELLS = ITEMS[18]
ITEM_FIREBALLS = ITEMS[19]
ITEM_NONE = ITEMS[20]

TT_ITEM_TABLE = [
    bytes([ITEM_NONE.id, ITEM_MUSHROOM.id]),
    bytes([ITEM_MUSHROOM.id, ITEM_MUSHROOM.id]),
    bytes([ITEM_NONE.id, ITEM_TRIPLE_MUSHROOMS.id]),
    bytes([ITEM_STAR.id, ITEM_TRIPLE_MUSHROOMS.id]),
]