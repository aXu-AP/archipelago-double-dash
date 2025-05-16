import asyncio
import time
import traceback
from typing import TYPE_CHECKING, Any, Optional

import dolphin_memory_engine as dolphin

import Utils
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, gui_enabled, logger, server_loop
from NetUtils import ClientStatus, NetworkItem

from . import game_data, items, locations
from .locations import MkddLocationData
from .items import ItemType, MkddItemData
from .asm import patches, mem_addresses

if TYPE_CHECKING:
    import kvui

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a randomized ROM for Mario Kart Double Dash. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
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
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, MkddContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")


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
        self.last_item_handled: int = 0
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.last_rcvd_index: int = -1
        self.has_send_death: bool = False
        self.memory_addresses = mem_addresses.MkddMemAddressesUsa
        self.race_counter: int = 0
        self.course_changed_time: int = 0

        # Name of the current stage as read from the game's memory. Sent to trackers whenever its value changes to
        # facilitate automatically switching to the map of the current stage.
        self.current_course: game_data.Course = game_data.Course()

        # Length of the item get array in memory.
        self.len_give_item_array: int = 0x10

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        self.salvage_locations_map = {}
        self.current_course = game_data.Course()
        self.visited_stage_names = None
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
            if "death_link" in args["slot_data"]:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))
        elif cmd == "ReceivedItems":
            if args["index"] >= self.last_rcvd_index:
                self.last_rcvd_index = args["index"]
                for item in args["items"]:
                    self.items_received_2.append((item, self.last_rcvd_index))
                    self.last_rcvd_index += 1
            self.items_received_2.sort(key=lambda v: v[1])
        elif cmd == "Retrieved":
            requested_keys_dict = args["keys"]

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


###### Dolphin connecton ######
def _apply_ar_code(ctx: MkddContext, code: list[int]):
    for i in range(0, len(code), 2):
        command = (code[i] & 0xFE00_0000) >> 24
        address = (code[i] & 0x01FF_FFFF) | 0x8000_0000
        logger.info(f"({command:02x}) {address:08x}: {code[i + 1]:08x} ({i/2}/{len(code)/2})")
        if command == 0x04:
            dolphin.write_word(address, code[i + 1])


def _apply_dict_patch(ctx: MkddContext, code: dict[int, list[int]]):
    for start_address, rows in code.items():
        address = start_address
        for row in rows:
            dolphin.write_word(address, row)
            address += 4


def _apply_patch(ctx: MkddContext):
    _apply_dict_patch(ctx, patches.character_selection)
    logger.info("Patch Applied.")


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
    logger.info(f"Got item: {item.name}")
    if item.item_type == ItemType.CHARACTER:
        dolphin.write_byte(ctx.memory_addresses.available_characters_bx + item.address, 1)
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
    # Course finishing related locations.
    if check_finished(ctx):
        await check_current_course_changed(ctx) # In case the client was reconnected during rankings screen.
        new_location_names.add(locations.get_loc_name_finish(ctx.current_course.name))
        logger.info(f"Finished {ctx.current_course.name} in place: {in_race_placement}. Mode: {mode}, class: {vehicle_class}.")
        if mode == game_data.Modes.GRANDPRIX:
            if in_race_placement == 0:
                new_location_names.add(locations.get_loc_name_first(ctx.current_course.name))

    if mode == game_data.Modes.GRANDPRIX and current_lap > 0 and in_race_placement == 0 and game_ticks > ctx.course_changed_time + 600:
        new_location_names.add(locations.get_loc_name_lead(ctx.current_course.name))

    # Cup related locations.
    if mode == game_data.Modes.CEREMONY:
        new_location_names.add(locations.get_loc_name_finish(cup))
        # Bronze or better. Add all variants that are considered easier than current (ie. 50 bronze for 150 gold finish).
        if total_ranking <= 2:
            for r in range(2, total_ranking - 1, -1):
                for c in range(vehicle_class + 1):
                    new_location_names.add(locations.get_loc_name_cup(cup, r, c))
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
                if not check_ingame():
                    # Reset the give item array while not in the game.
                    #dolphin.write_bytes(GIVE_ITEM_ARRAY_ADDR, bytes([0xFF] * ctx.len_give_item_array))
                    await asyncio.sleep(0.2)
                    continue
                if ctx.slot is not None:
                    if "DeathLink" in ctx.tags:
                        await check_death(ctx)
                    await give_items(ctx)
                    await check_locations(ctx)
                    await check_current_course_changed(ctx)
                else:
                    # if not ctx.auth:
                    #     ctx.auth = read_string(SLOT_NAME_ADDR, 0x40)
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                if dolphin.read_bytes(0x80000000, 6) != b"GM4E01":
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                await asyncio.sleep(0.2)
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
                        _apply_patch(ctx)
                        ctx.last_item_handled = 0
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
