from typing import NamedTuple

MENU_CHAR_ADR = 0x812C1BFB
"""Player 1 cursor for character selection. 0 Mario - 19 King Boo"""
MENU_KART_ADR = 0x812C1C0F
"""Player 1 cursor for kart selection. 0 Goo-Goo Buggy - 20 Parade Kart"""
MENU_CUP_ADR = 0x803CB7AB
"""Cup selection. 0 Mushroom Cup - 4 All Cup Tour"""
MENU_COURSE_ADR = 0x803CB7AF
"""Course selection within the selected cup. 0-3"""

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

KARTS = [
    Kart("Goo-Goo Buggy", 0),       # 00
    Kart("Rattle Buggy", 0),        # 01
    Kart("Koopa Dasher", 0),        # 02
    Kart("Para-Wing", 0),           # 03
    Kart("Barrel Train", 0),        # 04
    Kart("Bullet Blaster", 0),      # 05
    Kart("Toad Kart", 0),           # 06
    Kart("Toadette Kart", 0),       # 07
    Kart("Red Fire", 1),            # 08
    Kart("Green Fire", 1),          # 09
    Kart("Heart Coach", 1),         # 10
    Kart("Bloom Coach", 1),         # 11
    Kart("Turbo Yoshi", 1),         # 12
    Kart("Turbo Birdo", 1),         # 13
    Kart("Waluigi Racer", 1),       # 14
    Kart("Wario Car", 2),           # 15
    Kart("DK Jumbo", 2),            # 16
    Kart("Koopa King", 2),          # 17
    Kart("Piranha Pipes", 2),       # 18
    Kart("Boo Pipes", 2),           # 19
    Kart("Parade Kart", -1),        # 20
]

CUPS = [
    "Mushroom Cup",
    "Flower Cup",
    "Star Cup",
    "Special Cup",
    "All Cup Tour",
]

COURSES = [
    "Luigi Circuit",
    "Peach Beach",
    "Baby Park",
    "Dry Dry Desert",
    "Mushroom Bridge",
    "Mario Circuit",
    "Daisy Cruiser",
    "Waluigi Stadium",
    "Sherbet Land",
    "Mushroom City",
    "Yoshi Circuit",
    "DK Mountain",
    "Wario Colosseum",
    "Dino Dino Jungle",
    "Bowser's Castle",
    "Rainbow Road",
]