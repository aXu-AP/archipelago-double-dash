from enum import IntEnum
from typing import NamedTuple


class Character(NamedTuple):
    name: str
    weight: int

CHARACTERS = [
    Character("Mario", 1),          # 00
    Character("Luigi", 1),          # 01
    Character("Peach", 1),          # 02
    Character("Daisy", 1),          # 03
    Character("Yoshi", 1),          # 04
    Character("Birdo", 1),          # 05
    Character("Baby Mario", 0),     # 06
    Character("Baby Luigi", 0),     # 07
    Character("Toad", 0),           # 08
    Character("Toadette", 0),       # 09
    Character("Koopa", 0),          # 10
    Character("Paratroopa", 0),     # 11
    Character("Donkey Kong", 2),    # 12
    Character("Diddy Kong", 0),     # 13
    Character("Bowser", 2),         # 14
    Character("Bowser Jr.", 0),     # 15
    Character("Wario", 2),          # 16
    Character("Waluigi", 1),        # 17
    Character("Petey Piranha", 2),  # 18
    Character("King Boo", 2),       # 19
]

class Kart(NamedTuple):
    name: str
    weight: int
    unlock_id: int

KARTS = [
    Kart("Goo-Goo Buggy", 0, 5),    # 00
    Kart("Rattle Buggy", 0, 13),    # 01
    Kart("Koopa Dasher", 0, 3),     # 02
    Kart("Para-Wing", 0, 11),       # 03
    Kart("Barrel Train", 0, 9),     # 04
    Kart("Bullet Blaster", 0, 15),  # 05
    Kart("Toad Kart", 0, 16),       # 06
    Kart("Toadette Kart", 0, 17),   # 07
    Kart("Red Fire", 1, 0),         # 08
    Kart("Green Fire", 1, 8),       # 09
    Kart("Heart Coach", 1, 4),      # 10
    Kart("Bloom Coach", 1, 12),     # 11
    Kart("Turbo Yoshi", 1, 2),      # 12
    Kart("Turbo Birdo", 1, 10),     # 13
    Kart("Waluigi Racer", 1, 14),   # 14
    Kart("Wario Car", 2, 6),        # 15
    Kart("DK Jumbo", 2, 1),         # 16
    Kart("Koopa King", 2, 7),       # 17
    Kart("Piranha Pipes", 2, 19),   # 18
    Kart("Boo Pipes", 2, 18),       # 19
    Kart("Parade Kart", -1, 20),    # 20
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
    laps: int = 3


COURSES = [
    # Race courses:
    Course("Luigi Circuit", 0x24),
    Course("Peach Beach", 0x22),
    Course("Baby Park", 0x21, laps = 7),
    Course("Dry Dry Desert", 0x32),
    Course("Mushroom Bridge", 0x28),
    Course("Mario Circuit", 0x25),
    Course("Daisy Cruiser", 0x23),
    Course("Waluigi Stadium", 0x2a),
    Course("Sherbet Land", 0x33),
    Course("Mushroom City", 0x29),
    Course("Yoshi Circuit", 0x26),
    Course("DK Mountain", 0x2d),
    Course("Wario Colosseum", 0x2b, laps = 2),
    Course("Dino Dino Jungle", 0x2c),
    Course("Bowser's Castle", 0x2f),
    Course("Rainbow Road", 0x31),
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
