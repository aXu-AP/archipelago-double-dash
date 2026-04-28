import asyncio
import os
import time
import traceback
from typing import TYPE_CHECKING, Any, Optional

import Utils
from CommonClient import get_base_parser, gui_enabled, logger, server_loop
from NetUtils import ClientStatus, NetworkItem

import dolphin_memory_engine as dolphin

from . import game_data, game_state, items, locations, patches, mem_addresses, ar_codes, version, options
from .items import ItemType, MkddItemData
from .command_processor import MkddCommandProcessor, DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE
from .ut_common_client_importer import CommonContext, tracker_loaded, UT_VERSION

if TYPE_CHECKING:
    import kvui


CONNECTION_REFUSED_GAME_STATUS = "Dolphin failed to connect. Please load a ROM for Mario Kart Double Dash (USA). Trying again in 5 seconds..."
CONNECTION_LOST_STATUS = "Dolphin connection was lost. Please restart your emulator and make sure Mario Kart Double Dash is running."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."


class MkddContext(CommonContext):
    """
    The context for Mario Kart Double Dash client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Mario Kart Double Dash.
    """

    command_processor = MkddCommandProcessor
    game: str = version.get_game_name()
    compatible_version: str = "v0.3"
    items_handling: int = 0b111

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the Mkdd context.

        :param server_address: Address of the Archipelago server.
        :param password: Password for server authentication.
        """
        super().__init__(server_address, password)
        # Client data.
        self.items_received_2: list[tuple[NetworkItem, int]] = []
        self.last_item_handled: int = -1
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.last_rcvd_index: int = -1
        self.locations_checked: set[int] = set()
        self.has_send_death: bool = False
        self.victory_sent: bool = False
        self.victory: bool = False

        self.memory_addresses = mem_addresses.MkddMemAddressesUsa

        # Options.
        self.options: options.MkddOptions = options.init_options()

        # Game data.
        self.game_state: game_state.MkddGameState = game_state.MkddGameState(mem_addresses.MkddMemAddressesUsa)
        self.game_state.options = self.options
        self.trophies: int = 0 # Trophies aren't anything ingame, so it isn't part of game state.


    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        self.game_state = game_state.MkddGameState(mem_addresses.MkddMemAddressesUsa)
        self.game_state.options = self.options
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
        match cmd:
            case "Connected":
                self.items_received_2 = []
                self.last_rcvd_index = -1
                slot_data: dict = args.get("slot_data")
                host_version : str = slot_data.get("version")
                if not host_version.startswith(self.compatible_version):
                    self.gui_error("Incompatible seed/client",
                        f"The seed was generated using version {host_version} of MKDDAP.\n" +
                        f"Client's version: {version.get_version()}"
                    )
                    self.disconnect()
                    return
                
                if "death_link" in slot_data:
                    Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))

                if self.ui:
                    self.ui.update_trophies(self.trophies, self.options.trophy_requirement)
                    self.ui.update_characters([])
                    self.ui.update_cc(0)
                    self.ui.update_cups([])
                    self.ui.update_speed_upgrades(0, 3)
                    self.ui.update_karts([])
                
                self.options.update_from_slot_data(slot_data)
                self.game_state.cups_courses = slot_data["cups_courses"]

                self.game_state.character_item_total_weights = slot_data.get("character_item_total_weights")
                self.game_state.global_items_total_weights = slot_data.get("global_items_total_weights")

                self.locations_checked = set(args.get("checked_locations"))
                if self.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    self.game_state.sync_state()
            case "ReceivedItems":
                if args["index"] >= self.last_rcvd_index:
                    self.last_rcvd_index = args["index"]
                    for item in args["items"]:
                        self.items_received_2.append((item, self.last_rcvd_index))
                        self.last_rcvd_index += 1
                self.items_received_2.sort(key=lambda v: v[1])
            case "RoomUpdate":
                self.locations_checked.update(args.get("checked_locations", set()))
            case "PrintJSON":
                if args.get("type") == "ItemSend":
                    to_player: int = args["receiving"]
                    nw_item: NetworkItem = args["item"]
                    from_player: int = nw_item.player
                    item_name: str = self.item_names.lookup_in_slot(nw_item.item, to_player)
                    if to_player == self.slot and from_player == self.slot:
                        self.game_state.queue_ingame_message(f"You found your\n{item_name}")
                    elif to_player == self.slot:
                        from_player_name: str = self.player_names[from_player]
                        self.game_state.queue_ingame_message(f"{from_player_name} found your\n{item_name}")
                    elif from_player == self.slot:
                        to_player_name: str = self.player_names[to_player]
                        self.game_state.queue_ingame_message(f"You found {to_player_name}'s\n{item_name}")
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
        # Late importing so that kvui doesn't create window before it's time.
        from kvui import GameManager
        from . import gui
        base_class: type = GameManager
        ut_title: str = ""
        # Use Universal Tracker gui only if it's recent enough version.
        if tracker_loaded and UT_VERSION >= "v0.2.12":
            base_class = super().make_gui()
            ut_title = f" | Universal Tracker {UT_VERSION}"
        return gui.make_gui(base_class, ut_title)


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


def apply_patch():
    _apply_dict_patch(patches.patch)
    _apply_ar_code(ar_codes.lap_modifier)
    _apply_ar_code(ar_codes.gp_course_selection)
    _apply_ar_code(ar_codes.fireball_limit)
    _apply_ar_code(ar_codes.disable_reverse_lakitu)
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
    if item.item_type == ItemType.CHARACTER:
        dolphin.write_byte(ctx.memory_addresses.available_characters_bx + item.address, 1)
        ctx.game_state.unlocked_characters.append(item.address)
        if ctx.ui:
            ctx.ui.update_characters(ctx.game_state.unlocked_characters)

    elif item.item_type == ItemType.KART:
        kart = game_data.KARTS[item.address]
        dolphin.write_byte(ctx.memory_addresses.available_karts_bx + kart.unlock_id, 1)
        ctx.game_state.unlocked_karts.append(item.address)
        if ctx.ui:
            ctx.ui.update_karts(ctx.game_state.unlocked_karts)
    
    elif item.item_type == ItemType.KART_UPGRADE:
        ctx.game_state.kart_upgrades[item.address].append(item.meta)
    
    elif item.name == items.PROGRESSIVE_ENGINE:
        ctx.game_state.engine_upgrade_level += 1
        if ctx.ui:
            ctx.ui.update_speed_upgrades(ctx.game_state.engine_upgrade_level, 3)
    
    elif item.item_type == ItemType.CUP:
        ctx.game_state.unlocked_cups.append(item.address)
        if ctx.ui:
            ctx.ui.update_cups(ctx.game_state.unlocked_cups)
    
    elif item.item_type == ItemType.TT_COURSE:
        ctx.game_state.unlocked_courses.append(item.address)
    
    elif item.name == items.PROGRESSIVE_CLASS:
        ctx.game_state.unlocked_vehicle_class = min(ctx.game_state.unlocked_vehicle_class + 1, 3)
        dolphin.write_word(ctx.memory_addresses.max_vehicle_class_w, ctx.game_state.unlocked_vehicle_class)
        if ctx.ui:
            ctx.ui.update_cc(ctx.game_state.unlocked_vehicle_class)

    elif item.name == items.PROGRESSIVE_CUP_SKIP:
        ctx.game_state.unlocked_cup_skips = min(ctx.game_state.unlocked_cup_skips + 1, 3)
    
    elif item.name == items.PROGRESSIVE_TIME_TRIAL_ITEM:
        ctx.game_state.time_trial_items = min(ctx.game_state.time_trial_items + 1, len(game_data.TT_ITEM_TABLE) - 1)
        dolphin.write_bytes(ctx.memory_addresses.tt_items_bx, game_data.TT_ITEM_TABLE[ctx.game_state.time_trial_items])
    
    elif item.item_type == ItemType.ITEM_UNLOCK:
        if item.meta["character"] == None:
            ctx.game_state.global_items.append(item.meta["item"])
        else:
            ctx.game_state.character_items[item.meta["character"]].append(item.meta["item"])

    elif item.name == items.TROPHY:
        ctx.trophies += 1
        if ctx.ui:
            ctx.ui.update_trophies(ctx.trophies, ctx.options.trophy_requirement)
    
    elif item.name == items.VICTORY:
        ctx.victory = True
    
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

    if ctx.trophies >= ctx.options.trophy_requirement:
        new_location_names.add(locations.TROPHY_GOAL)
    
    new_location_names |= ctx.game_state.check_item_box_locations()
    new_location_names |= ctx.game_state.check_finish_course_locations()
    new_location_names |= ctx.game_state.check_take_lead_locations()
    new_location_names |= ctx.game_state.check_gp_race_locations()
    new_location_names |= ctx.game_state.check_gp_cup_locations()
    new_location_names |= ctx.game_state.check_all_cup_tour_locations()
    new_location_names |= ctx.game_state.check_tt_locations()

    new_locations = {locations.name_to_id.get(loc_name) for loc_name in new_location_names}
    new_locations.discard(None)
    ctx.locations_checked.update(new_locations)
    # Send the list of newly-checked locations to the server.
    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])


def update_game(ctx: MkddContext) -> None:
    """
    Update game state such as controlling character selection.

    :param ctx: Mario Kart Double Dash client context.
    """
    _apply_ar_code(ar_codes.unlock_everything)
    ctx.game_state.handle_character_menu()
    ctx.game_state.apply_shuffled_courses()
    ctx.game_state.apply_item_box_items()
    ctx.game_state.update_item_box_visuals(ctx.locations_checked)
    ctx.game_state.apply_lap_counts()
    ctx.game_state.handle_all_cup_tour()
    ctx.game_state.apply_course_availability()
    ctx.game_state.apply_200cc()
    ctx.game_state.apply_kart_stats()
    ctx.game_state.flush_ingame_text()


async def check_current_course_changed(ctx: MkddContext) -> None:
    """
    Check if the player has moved to a new stage.
    If so, update all trackers with the new stage name.

    :param ctx: Mario Kart Double Dash client context.
    """
    if ctx.game_state.check_current_course_changed():
        # Send a Bounced message containing the new stage name to all trackers connected to the current slot.
        data_to_send = {"mkdd_course_name": ctx.game_state.current_course.name}
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
        dolphin_name = os.getenv(DME_DOLPHIN_PROCESS_NAME_ENV_VARIABLE) or "Dolphin"
        try:
            if dolphin.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if ctx.ui:
                    ctx.ui.show_launch_button(False)
                if ctx.slot is not None:
                    if "DeathLink" in ctx.tags:
                        await check_death(ctx)
                    await give_items(ctx)

                    ctx.game_state.update()
                    await check_current_course_changed(ctx)
                    await check_locations(ctx)
                    update_game(ctx)

                    if ctx.victory and not ctx.victory_sent:
                        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                        ctx.victory_sent = True
                else:
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                if dolphin.read_bytes(0x80000000, 6) != b"GM4E01":
                    logger.info(f"Connection to {dolphin_name} lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                await asyncio.sleep(0.1)
            else:
                if ctx.ui:
                    ctx.ui.set_launch_func(ctx.command_processor._cmd_launch)
                    ctx.ui.show_launch_button(True)
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info(f"Connection to {dolphin_name} lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info(f"Attempting to connect to {dolphin_name}...")
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
                        apply_patch()
                        ctx.game_state.sync_state()
                        await give_items(ctx)
                else:
                    logger.info(f"Connection to {dolphin_name} failed, attempting again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await asyncio.sleep(5)
                    continue
        except Exception:
            dolphin.un_hook()
            logger.info(f"Connection to {dolphin_name} failed, attempting again in 5 seconds...")
            logger.warning(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await asyncio.sleep(5)
            continue


def main(*args) -> None:
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

    parser = get_base_parser(description="Mario Kart Double Dash Client.")
    parser.add_argument('--name', default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    args = parser.parse_args(args)

    from CommonClient import handle_url_arg
    args = handle_url_arg(args, parser=parser)

    import colorama

    colorama.init()
    asyncio.run(_main(args.connect, args.password))
    colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args)
