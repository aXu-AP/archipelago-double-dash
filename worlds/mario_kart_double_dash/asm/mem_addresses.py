class MkddMemAddresses():
    """
    Collection of memory addresses of relevant data.
    Inherit this class to specify addresses for different versions.

    Property suffixes tell the data type (b = byte, h = half word, w = word, x = table).
    """
    # Vanilla addresses:
    mode_w: int
    """Current game mode. Updated after select character screen. See game_data.Modes for values."""
    cup_w: int
    """Cup selection. 0 Mushroom Cup - 4 All Cup Tour."""
    menu_course_w: int
    """Currently selected course inside a cup. Doesn't update in midst of a gp. 0-3."""
    vehicle_class_w: int
    """Currently selected class. Updated after select character screen. 0 = 50cc, 3 = Mirror."""
    current_course_w: int
    """Currently loaded course. For values see game_data.COURSES"""
    current_lap_wx: int
    """Table of players' current lap from 1st player to 4th. 0 = 1st lap."""
    in_race_placement_wx: int
    """Table of player placements from 1st player to 4th. 1 = 1st place. -1 for unused player slots."""
    current_course_ranking_w: int
    total_ranking_w: int
    """Player's placement in the current cup. 0 = 1st place."""
    total_points_wx: int
    """Players' and cpus' points in a table."""
    game_ticks_w: int
    """Frames since game startup. 60 per second."""

    # Custom addresses:
    available_characters_bx: int
    """Table of available characters from Mario to Petey (size 20). 1 = unlocked."""
    available_karts_bx: int
    """Table of available karts from Goo-Goo Buggy to Parade Kart (size 21). 1 = unlocked."""
    race_counter_w: int
    """Increased each time the player finishes."""

class MkddMemAddressesUsa(MkddMemAddresses):
    # Vanilla addresses:
    mode_w = 0x803b1464
    cup_w = 0x803cb7a8
    menu_course_w = 0x803cb7ac
    vehicle_class_w = 0x803b146c
    current_course_w = 0x803cbd44
    current_lap_wx = 0x8037ff60
    in_race_placement_wx = 0x8037ffa0
    current_course_ranking_w = 0x803b0f3b
    total_ranking_w = 0x803b1260
    total_points_wx = 0x803b11cc
    game_ticks_w = 0x803b0754

    # Custom addresses:
    available_characters_bx = 0x80001000
    available_karts_bx = 0x80001014
    race_counter_w = 0x8000102c
