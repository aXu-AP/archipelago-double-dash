import asyncio
import random
import time
import traceback
from typing import TYPE_CHECKING, Any, Optional

import dolphin_memory_engine as dolphin

import Utils
from CommonClient import get_base_parser, gui_enabled, logger, server_loop
from NetUtils import ClientStatus, NetworkItem

from . import game_data, items, locations, patches, mem_addresses, ar_codes
from .locations import MkddLocationData
from .items import ItemType, MkddItemData

tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import (TrackerCommandProcessor as ClientCommandProcessor,
                                              TrackerGameContext as CommonContext, UT_VERSION)
    tracker_loaded = True
except ImportError:
    from CommonClient import ClientCommandProcessor, CommonContext


if TYPE_CHECKING:
    import kvui

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a ROM for Mario Kart Double Dash (USA). Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Mario Kart Double Dash is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

class MkddCommandProcessor(ClientCommandProcessor):
    """
    Command Processor for Mario Kart Double Dash client commands.

    This class handles commands specific to Mario Kart Double Dash.
    """

    def __init__(self, ctx: CommonContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_dolphin(self) -> None:
        """Display the current Dolphin emulator connection status."""
        if isinstance(self.ctx, MkddContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")
    
    def _cmd_unlocked(self) -> None:
        """Show list of unlocked items."""
        if isinstance(self.ctx, MkddContext):
            logger.info(f"Unlocked characters: {", ".join([game_data.CHARACTERS[c].name for c in self.ctx.unlocked_characters])}")
            logger.info(f"Unlocked karts: {", ".join([game_data.KARTS[c].name for c in self.ctx.unlocked_karts])}")
            logger.info(f"Max vehicle class: {["50cc", "100cc", "150cc", "Mirror"][self.ctx.unlocked_vehicle_class]}")
            logger.info(f"Unlocked cups: {", ".join([game_data.CUPS[c] for c in self.ctx.unlocked_cups])}")
            logger.info(f"Unlocked time trial courses: {", ".join([game_data.COURSES[c].name for c in self.ctx.unlocked_courses])}")
            logger.info("Unlocked item box items:")
            if len(self.ctx.global_items) > 0:
                logger.info(f"Everybody: {", ".join([item.name for item in self.ctx.global_items])}")
            for character, items in self.ctx.character_items.items():
                if len(items) > 0:
                   logger.info(f"{character.name}: {", ".join([item.name for item in items])}")


class MkddContext(CommonContext):
    """
    The context for Mario Kart Double Dash client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Mario Kart Double Dash.
    """

    command_processor = MkddCommandProcessor
    game: str = "Mario Kart Double Dash"
    items_handling: int = 0b111

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the Mkdd context.

        :param server_address: Address of the Archipelago server.
        :param password: Password for server authentication.
        """

        super().__init__(server_address, password)
        self.items_received_2: list[tuple[NetworkItem, int]] = []
        self.last_item_handled: int = -1
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.last_rcvd_index: int = -1
        self.has_send_death: bool = False

        self.memory_addresses = mem_addresses.MkddMemAddressesUsa

        self.last_race_timer: int = 0
        self.last_in_game: bool = False

        self.race_counter: int = 0
        self.course_changed_time: int = 0

        self.unlocked_vehicle_class: int = 0
        self.last_selected_vehicle_class: int = 0

        self.unlocked_characters: list[int] = []
        self.last_selected_character: int = 0

        self.unlocked_karts: list[int] = []
        self.last_selected_kart: int = 0

        self.unlocked_cups: list[int] = []
        self.last_selected_cup: int = 0

        self.unlocked_cup_skips: int = 0
        
        self.unlocked_courses: list[int] = []
        self.last_selected_course: int = 0
        
        self.time_trial_items: int = 0

        self.lap_counts: dict[str, int]

        self.active_characters: list[game_data.Character] = [game_data.CHARACTERS[0], game_data.CHARACTERS[0]]
        self.active_kart: game_data.Kart = game_data.KARTS[0]
        
        self.character_item_total_weights: dict[str, list[int]] = {}
        self.global_items_total_weights: list[int] = []
        self.character_items: dict[game_data.Character, list[game_data.Item]] = {character:[] for character in game_data.CHARACTERS}
        self.global_items: list[game_data.Item] = []

        # Name of the current stage as read from the game's memory. Sent to trackers whenever its value changes to
        # facilitate automatically switching to the map of the current stage.
        self.current_course: game_data.Course = game_data.Course()

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        self.current_course = game_data.Course()
        await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        :param password_requested: Whether the server requires a password. Defaults to `False`.
        """
        if password_requested and not self.password:
            await super(MkddContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        """
        Handle incoming packages from the server.

        :param cmd: The command received from the server.
        :param args: The command arguments.
        """
        if cmd == "Connected":
            self.items_received_2 = []
            self.last_rcvd_index = -1
            slot_data = args.get("slot_data")
            if "death_link" in slot_data:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))
            self.lap_counts = slot_data.get("lap_counts")
            self.character_item_total_weights = slot_data.get("character_item_total_weights")
            self.global_items_total_weights = slot_data.get("global_items_total_weights")
            sync_state(self)
        elif cmd == "ReceivedItems":
            if args["index"] >= self.last_rcvd_index:
                self.last_rcvd_index = args["index"]
                for item in args["items"]:
                    self.items_received_2.append((item, self.last_rcvd_index))
                    self.last_rcvd_index += 1
            self.items_received_2.sort(key=lambda v: v[1])
        elif cmd == "Retrieved":
            requested_keys_dict = args["keys"]
        # Relay packages to the tracker also.
        super().on_package(cmd, args)

    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.

        :param data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        _give_death(self)

    def make_gui(self) -> type["kvui.GameManager"]:
        """
        Initialize the GUI for Mario Kart Double Dash client.

        :return: The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = "Archipelago Mario Kart Double Dash Client"
        return ui
    
    def run_gui(self):
        from kvui import GameManager

        class MkddManager(GameManager):
            source = ""
            logging_pairs = [("Client", "Archipelago")]
            base_title = "Mario Kart: Double Dash!! Client"
            if tracker_loaded:
                base_title += f" | Universal Tracker v{UT_VERSION}"
            base_title +=  " | Archipelago v"

            def build(self):
                container = super().build()
                if tracker_loaded:
                    self.ctx.build_gui(self)
                else:
                    logger.info("To enable a tracker, install Universal Tracker")

                return container

        self.ui = MkddManager(self)
        if tracker_loaded:
            self.load_kv()
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


###### Dolphin connection ######
def _apply_ar_code(code: list[int]):
    for i in range(0, len(code), 2):
        command = (code[i] & 0xFE00_0000) >> 24
        address = (code[i] & 0x01FF_FFFF) | 0x8000_0000
        if command == 0x04:
            dolphin.write_word(address, code[i + 1])


def _apply_dict_patch(code: dict[int, list[int]]):
    for start_address, rows in code.items():
        address = start_address
        for row in rows:
            dolphin.write_word(address, row)
            address += 4


def apply_patch(ctx: MkddContext):
    _apply_dict_patch(patches.patch)
    _apply_ar_code(ar_codes.lap_modifier)
    _apply_ar_code(ar_codes.gp_course_selection)
    logger.info("Patch Applied.")


def sync_state(ctx: MkddContext) -> None:
    """
    Sets game state to match client data about unlocks.

    :param ctx: Mario Kart Double Dash client context.
    """
    for character in range(len(game_data.CHARACTERS)):
        dolphin.write_byte(
            ctx.memory_addresses.available_characters_bx + character,
            int(character in ctx.unlocked_characters)
        )
    for k in range(len(game_data.KARTS)):
        kart = game_data.KARTS[k]
        dolphin.write_byte(
            ctx.memory_addresses.available_karts_bx + kart.unlock_id,
            int(k in ctx.unlocked_karts)
        )
    dolphin.write_word(ctx.memory_addresses.max_vehicle_class_w, ctx.unlocked_vehicle_class)
    dolphin.write_bytes(ctx.memory_addresses.tt_items_bx, game_data.TT_ITEM_TABLE[ctx.time_trial_items])


def _give_death(ctx: MkddContext) -> None:
    """
    Trigger the player's death in-game by setting their current health to zero.

    :param ctx: Mario Kart Double Dash client context.
    """
    if (
        ctx.slot is not None
        and dolphin.is_hooked()
        and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS
        and check_ingame()
    ):
        ctx.has_send_death = True
        # TODO: Add death link.


def _give_item(ctx: MkddContext, item: MkddItemData) -> bool:
    """
    Give an item to the player in-game.

    :param ctx: Mario Kart Double Dash client context.
    :param item_name: Name of the item to give.
    :return: Whether the item was successfully given.
    """
    if item.item_type == ItemType.CHARACTER:
        dolphin.write_byte(ctx.memory_addresses.available_characters_bx + item.address, 1)
        ctx.unlocked_characters.append(item.address)
    
    elif item.item_type == ItemType.KART:
        kart = game_data.KARTS[item.address]
        dolphin.write_byte(ctx.memory_addresses.available_karts_bx + kart.unlock_id, 1)
        ctx.unlocked_karts.append(item.address)
    
    elif item.item_type == ItemType.CUP:
        ctx.unlocked_cups.append(item.address)
    
    elif item.item_type == ItemType.TT_COURSE:
        ctx.unlocked_courses.append(item.address)
    
    elif item.name == items.PROGRESSIVE_CLASS:
        ctx.unlocked_vehicle_class = min(ctx.unlocked_vehicle_class + 1, 3)
        dolphin.write_word(ctx.memory_addresses.max_vehicle_class_w, ctx.unlocked_vehicle_class)
    
    elif item.name == items.PROGRESSIVE_CUP_SKIP:
        ctx.unlocked_cup_skips = min(ctx.unlocked_cup_skips + 1, 3)
    
    elif item.name == items.PROGRESSIVE_TIME_TRIAL_ITEM:
        ctx.time_trial_items = min(ctx.time_trial_items + 1, len(game_data.TT_ITEM_TABLE) - 1)
        dolphin.write_bytes(ctx.memory_addresses.tt_items_bx, game_data.TT_ITEM_TABLE[ctx.time_trial_items])
    
    elif item.item_type == ItemType.ITEM_UNLOCK:
        if item.meta["character"] == None:
            ctx.global_items.append(item.meta["item"])
        else:
            ctx.character_items[item.meta["character"]].append(item.meta["item"])
    
    return True


async def give_items(ctx: MkddContext) -> None:
    """
    Give the player all outstanding items they have yet to receive.

    :param ctx: Mario Kart Double Dash client context.
    """
    # Loop through items to give.
    for item, idx in ctx.items_received_2:
        # If the item's index is greater than the player's expected index, give the player the item.
        if ctx.last_item_handled < idx:
            # Attempt to give the item and increment the expected index.
            while not _give_item(ctx, items.data_table[item.item]):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            ctx.last_item_handled = idx


async def check_locations(ctx: MkddContext) -> None:
    """
    Iterate through all locations and check whether the player has checked each location.

    Update the server with all newly checked locations since the last update. If the player has completed the goal,
    notify the server.

    :param ctx: Mario Kart Double Dash client context.
    """
    new_location_names: set[str] = set()

    mode: int = dolphin.read_word(ctx.memory_addresses.mode_w)
    cup: str = game_data.CUPS[dolphin.read_word(ctx.memory_addresses.cup_w)]
    menu_course: int = dolphin.read_word(ctx.memory_addresses.menu_course_w)
    vehicle_class: int = dolphin.read_word(ctx.memory_addresses.vehicle_class_w)
    current_lap: int = dolphin.read_word(ctx.memory_addresses.current_lap_wx)
    # Get placement and modify it to be 0-based for less confusion (rankings are also 0-based).
    in_race_placement: int = dolphin.read_word(ctx.memory_addresses.in_race_placement_wx) - 1
    current_course_ranking: int = dolphin.read_word(ctx.memory_addresses.current_course_ranking_w)
    total_ranking: int = dolphin.read_word(ctx.memory_addresses.total_ranking_w)
    total_points: int = dolphin.read_word(ctx.memory_addresses.total_points_wx)
    game_ticks: int = dolphin.read_word(ctx.memory_addresses.game_ticks_w)
    race_timer: int = dolphin.read_word(ctx.memory_addresses.race_timer_w)
    # Remove 181 frame headstart and convert to seconds.
    # Close enough (to 1/10th of a second), altough probably exact formula should be investigated.
    race_timer_s: float = (race_timer - 181) / 60

    # Some ways to check what state is the game in. In game in particular has to have one frame
    # leeway in case we read finishing state after the last frame advance has happened.
    new_in_game: bool = race_timer - ctx.last_race_timer > 0 # From countdown to finish.
    in_game: bool = new_in_game or ctx.last_in_game
    ctx.last_in_game = new_in_game
    course_loaded: bool = game_ticks > ctx.course_changed_time + 60 # Don't give checks in menus etc.
    ctx.last_race_timer = race_timer

    # Course finishing related locations.
    # For Time Trials check against default lap counts.
    if in_game and current_lap >= ctx.current_course.laps:
        if mode == game_data.Modes.TIMETRIAL:
            new_location_names.add(locations.get_loc_name_finish(ctx.current_course.name))
            logger.info(f"{race_timer_s} / {race_timer}")
            if race_timer_s < ctx.current_course.good_time:
                new_location_names.add(locations.get_loc_name_good_time(ctx.current_course))
            if race_timer_s < ctx.current_course.staff_time:
                new_location_names.add(locations.get_loc_name_ghost(ctx.current_course.name))

    # For Grand Prix use possible custom lap counts.
    if in_game and current_lap >= ctx.lap_counts.get(ctx.current_course.name, 3):
        if mode == game_data.Modes.GRANDPRIX:
            new_location_names.add(locations.get_loc_name_finish(ctx.current_course.name))
            if in_race_placement == 0:
                new_location_names.add(locations.get_loc_name_first(ctx.current_course.name))
            
                # Win with default character + kart combination.
                for character in ctx.active_characters:
                    kart = game_data.KARTS[character.default_kart]
                    if ctx.active_kart == kart:
                        new_location_names.add(locations.get_loc_name_win_char_kart(character.name, kart.name))
                
                # Win with course owner.
                for character in ctx.current_course.owners:
                    if game_data.CHARACTERS[character] in ctx.active_characters:
                        new_location_names.add(locations.get_loc_name_win_course_char(ctx.current_course))
            
    if mode == game_data.Modes.GRANDPRIX and current_lap > 0 and in_race_placement == 0 and in_game:
        new_location_names.add(locations.get_loc_name_lead(ctx.current_course.name))

    # Cup related locations.
    if mode == game_data.Modes.CEREMONY:
        new_location_names.add(locations.get_loc_name_finish(cup))
        # Bronze or better. Add all variants that are considered easier than current (ie. 50 bronze for 150 gold finish).
        if total_ranking <= 2:
            for r in range(2, total_ranking - 1, -1):
                for c in range(vehicle_class + 1):
                    new_location_names.add(locations.get_loc_name_cup(cup, r, c))
        # Gold for various vehicles.
        if total_ranking == 0:
            if ctx.active_kart.weight == 0:
                new_location_names.add(locations.GOLD_LIGHT)
            elif ctx.active_kart.weight == 1:
                new_location_names.add(locations.GOLD_MEDIUM)
            elif ctx.active_kart.weight == 2:
                new_location_names.add(locations.GOLD_HEAVY)
            elif ctx.active_kart.weight == -1:
                new_location_names.add(locations.GOLD_PARADE)
        
        if total_points == 40:
            new_location_names.add(locations.get_loc_name_perfect(cup))
        
    new_locations = {locations.name_to_id.get(loc_name) for loc_name in new_location_names}
    new_locations.discard(None)
    ctx.locations_checked.update(new_locations)
    # Send the list of newly-checked locations to the server.
    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])


def check_finished(ctx: MkddContext) -> bool:
    current_race: int = dolphin.read_word(ctx.memory_addresses.race_counter_w)
    if current_race > ctx.race_counter:
        ctx.race_counter = current_race
        return True
    else:
        return False


def update_game(ctx: MkddContext) -> None:
    """
    Update game state such as controlling character selection.

    :param ctx: Mario Kart Double Dash client context.
    """
    _apply_ar_code(ar_codes.unlock_everything)

    # Force character and kart selection.
    # The game is modded to do this autonomically to some degree, but some edge cases is handled by client.
    # TODO: Handle the rest of the cases in-game:
    #       - Default character is still Mario
    #       - Default kart is chosen from the character
    #       - Random choice kart
    menu_pointer = dolphin.read_word(ctx.memory_addresses.menu_pointer)
    if menu_pointer != 0:
        driver = dolphin.read_word(menu_pointer + ctx.memory_addresses.menu_driver_w_offset)
        rider = dolphin.read_word(menu_pointer + ctx.memory_addresses.menu_rider_w_offset)
        character: int = int(dolphin.read_word(menu_pointer + ctx.memory_addresses.menu_character_w_offset))
        kart: int = int(dolphin.read_word(menu_pointer + ctx.memory_addresses.menu_kart_w_offset))
        
        # Save selections for later use (when menu pointer becomes invalid).
        if driver >= 0 and driver < len(game_data.CHARACTERS):
            ctx.active_characters[0] = game_data.CHARACTERS[driver]
        if rider >= 0 and rider < len(game_data.CHARACTERS):
            ctx.active_characters[1] = game_data.CHARACTERS[rider]
        if kart >= 0 and kart < len(game_data.KARTS):
            ctx.active_kart = game_data.KARTS[kart]

        if character >= 0 and character < len(game_data.CHARACTERS) and not character in ctx.unlocked_characters:
            direction: int = character - ctx.last_selected_character
            direction = 1 if direction == 0 else int(direction / abs(direction))
            while not character in ctx.unlocked_characters:
                character = wrap(character + direction, len(game_data.CHARACTERS))
                if character == ctx.last_selected_character:
                    break
            dolphin.write_word(menu_pointer + ctx.memory_addresses.menu_character_w_offset, character)
        ctx.last_selected_character = character

        if kart >= 0 and kart < len(game_data.KARTS) and not kart in ctx.unlocked_karts:
            weight = max(ctx.active_characters[0].weight, ctx.active_characters[1].weight)
            # weight = game_data.KARTS[kart].weight
            direction: int = kart - ctx.last_selected_kart
            direction = 1 if direction == 0 else int(direction / abs(direction))
            while (game_data.KARTS[kart].weight != -1 and game_data.KARTS[kart].weight != weight) or not kart in ctx.unlocked_karts:
                kart = wrap(kart + direction, len(game_data.KARTS))
                if kart == ctx.last_selected_kart:
                    break
            dolphin.write_word(menu_pointer + ctx.memory_addresses.menu_kart_w_offset, kart)
        ctx.last_selected_kart = kart

    # Force cup and course selection.
    mode: int = int(dolphin.read_word(ctx.memory_addresses.mode_w))
    available_cups_courses: dict[int, set[int]] = {}
    if mode == game_data.Modes.TIMETRIAL:
        course_order: list[list[int]] = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]
        for cu in range(4):
            for c in ctx.unlocked_courses:
                if c in course_order[cu]:
                    if not cu in available_cups_courses:
                        available_cups_courses[cu] = set()
                    available_cups_courses[cu].add(c - cu * 4)
        if len(available_cups_courses) == 0:
            # Failsafe if no tt tracks are unlocked.
            logger.info("No Time Trials unlocked yet! Changed mode to Grand Prix.")
            mode = int(game_data.Modes.GRANDPRIX)
            dolphin.write_word(ctx.memory_addresses.mode_w, mode)

        # Use vanilla lap counts in time trials.
        for c in [c for c in game_data.COURSES if c.type == game_data.CourseType.RACE]:
            dolphin.write_byte(ctx.memory_addresses.lap_count_bx + c.id, c.laps)

    
    if mode == game_data.Modes.GRANDPRIX:
        # Give option to skip x first courses.
        courses = [c for c in range(ctx.unlocked_cup_skips + 1)]
        for cup in ctx.unlocked_cups:
            available_cups_courses[cup] = courses

        # Use custom lap counts in grand prix.
        for c in [c for c in game_data.COURSES if c.type == game_data.CourseType.RACE]:
            dolphin.write_byte(ctx.memory_addresses.lap_count_bx + c.id, ctx.lap_counts[c.name])

        # Item selection.
        in_race_placement: int = max(0, min(7, dolphin.read_word(ctx.memory_addresses.in_race_placement_wx) - 1))
        item_adr: list[int] = [
            ctx.memory_addresses.gp_next_items_bx + ctx.active_characters[0].item_offset,
            ctx.memory_addresses.gp_next_items_bx + ctx.active_characters[1].item_offset,
        ]
        total_weight = ctx.global_items_total_weights[in_race_placement]
        total_weight += ctx.character_item_total_weights[ctx.active_characters[0].name][in_race_placement]
        item_pool = ctx.global_items + ctx.character_items[ctx.active_characters[0]]
        if item_adr[0] != item_adr[1]:
            item_weights = [item.weight_table[in_race_placement] for item in item_pool]
            # Yet to be unlocked items still count towards item weights.
            weight_gap = total_weight - sum(item_weights)
            if weight_gap > 0:
                item_pool.append(game_data.ITEM_NONE)
                item_weights.append(weight_gap)
            rand_item = random.sample(item_pool, 1, counts = item_weights)[0]
            dolphin.write_byte(item_adr[0], rand_item.id)

            # Reset pool for second player only if they aren't synced.
            total_weight = ctx.global_items_total_weights[in_race_placement]
            item_pool = ctx.global_items
        total_weight += ctx.character_item_total_weights[ctx.active_characters[1].name][in_race_placement]
        item_pool += ctx.character_items[ctx.active_characters[1]]
        item_weights = [item.weight_table[in_race_placement] for item in item_pool]
        # Yet to be unlocked items still count towards item weights.
        weight_gap = total_weight - sum(item_weights)
        if weight_gap > 0:
            item_pool.append(game_data.ITEM_NONE)
            item_weights.append(weight_gap)
        rand_item = random.sample(item_pool, 1, counts = item_weights)[0]
        dolphin.write_byte(item_adr[1], rand_item.id)
        

    if len(available_cups_courses) > 0:
        for c in range(len(game_data.CUPS)):
            dolphin.write_byte(ctx.memory_addresses.available_cups_bx + c, int(c in ctx.unlocked_cups))
            cup: int = int(dolphin.read_word(ctx.memory_addresses.cup_w))
            if not cup in available_cups_courses:
                direction: int = cup - ctx.last_selected_cup
                direction = 1 if direction == 0 else int(direction / abs(direction))
                while not cup in available_cups_courses:
                    cup = wrap(cup + direction, len(game_data.CUPS))
                    if cup == ctx.last_selected_cup:
                        break
                dolphin.write_word(ctx.memory_addresses.cup_w, cup)
                ctx.last_selected_cup = cup

            for c in range(len(game_data.CUPS)):
                dolphin.write_byte(ctx.memory_addresses.available_cups_bx + c, int(c in available_cups_courses))

            course: int = int(dolphin.read_word(ctx.memory_addresses.menu_course_w))
            if not course in available_cups_courses[cup]:
                direction: int = cup - ctx.last_selected_course
                direction = 1 if direction == 0 else int(direction / abs(direction))
                while not course in available_cups_courses[cup]:
                    course = wrap(course + direction, 4)
                    if course == ctx.last_selected_course:
                        break
                dolphin.write_word(ctx.memory_addresses.menu_course_w, course)
                ctx.last_selected_course = course

def wrap(value: int, max_value: int) -> int:
    if value < 0:
        return max_value - 1
    if value >= max_value:
        return 0
    return value


async def check_current_course_changed(ctx: MkddContext) -> None:
    """
    Check if the player has moved to a new stage.
    If so, update all trackers with the new stage name.
    If the stage has never been visited, additionally update the server.

    :param ctx: Mario Kart Double Dash client context.
    """
    course_id = dolphin.read_word(ctx.memory_addresses.current_course_w)
    courses: list[game_data.Course] = [c for c in game_data.COURSES if c.id == course_id]
    if len(courses) > 0:
        new_course = courses[0]
        if new_course != ctx.current_course:
            ctx.course_changed_time = dolphin.read_word(ctx.memory_addresses.game_ticks_w)
            ctx.current_course = new_course
            # Send a Bounced message containing the new stage name to all trackers connected to the current slot.
            data_to_send = {"mkdd_course_name": new_course.name}
            message = {
                "cmd": "Bounce",
                "slots": [ctx.slot],
                "data": data_to_send,
            }
            await ctx.send_msgs([message])



async def check_death(ctx: MkddContext) -> None:
    """
    Check if the player is currently dead in-game.
    If DeathLink is on, notify the server of the player's death.

    :return: `True` if the player is dead, otherwise `False`.
    """
    # TODO: Check for Lakitu.
    if ctx.slot is not None and check_ingame():
        is_dead = False
        if is_dead:
            if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
                ctx.has_send_death = True
                await ctx.send_death(ctx.player_names[ctx.slot] + " fell off a track.")
        else:
            ctx.has_send_death = False


def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """
    # TODO: Check if a race is on.
    return True


async def dolphin_sync_task(ctx: MkddContext) -> None:
    """
    The task loop for managing the connection to Dolphin.

    While connected, read the emulator's memory to look for any relevant changes made by the player in the game.

    :param ctx: Mario Kart Double Dash client context.
    """
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")
    while not ctx.exit_event.is_set():
        try:
            if dolphin.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if ctx.slot is not None:
                    if "DeathLink" in ctx.tags:
                        await check_death(ctx)
                    await give_items(ctx)
                    await check_current_course_changed(ctx)
                    await check_locations(ctx)
                    update_game(ctx)
                else:
                    # if not ctx.auth:
                    #     ctx.auth = read_string(SLOT_NAME_ADDR, 0x40)
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                if dolphin.read_bytes(0x80000000, 6) != b"GM4E01":
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                await asyncio.sleep(0.1)
            else:
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info("Attempting to connect to Dolphin...")
                dolphin.hook()
                if dolphin.is_hooked():
                    if dolphin.read_bytes(0x80000000, 6) != b"GM4E01":
                        logger.info(CONNECTION_REFUSED_GAME_STATUS)
                        ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                        dolphin.un_hook()
                        await asyncio.sleep(5)
                    else:
                        logger.info(CONNECTION_CONNECTED_STATUS)
                        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                        apply_patch(ctx)
                        sync_state(ctx)
                        ctx.last_item_handled = -1
                        give_items(ctx)
                        ctx.locations_checked = set()
                else:
                    logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await ctx.disconnect()
                    await asyncio.sleep(5)
                    continue
        except Exception:
            dolphin.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await ctx.disconnect()
            await asyncio.sleep(5)
            continue


def main(connect: Optional[str] = None, password: Optional[str] = None) -> None:
    """
    Run the main async loop for Mario Kart Double Dash client.

    :param connect: Address of the Archipelago server.
    :param password: Password for server authentication.
    """
    Utils.init_logging("Mario Kart Double Dash Client")

    async def _main(connect: Optional[str], password: Optional[str]) -> None:
        ctx = MkddContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

        # Runs Universal Tracker's internal generator
        if tracker_loaded:
            ctx.run_generator()
            ctx.tags.remove("Tracker")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await asyncio.sleep(1)

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await asyncio.sleep(3)
            await ctx.dolphin_sync_task

    import colorama

    colorama.init()
    asyncio.run(_main(connect, password))
    colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args.connect, args.password)
