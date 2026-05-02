import dolphin_memory_engine as dolphin
import random
from . import game_data, locations, mem_addresses, options
from CommonClient import logger


class MkddGameState():
    """
    Class to handle the connection to Dolphin running MKDD.
    """
    def __init__(self, memory_addresses: mem_addresses.MkddMemAddresses):
        # Unlocks and other data from server.
        self.options: options.MkddOptions
        self.memory_addresses: mem_addresses.MkddMemAddresses = memory_addresses
        self.unlocked_vehicle_class: int = 0
        self.unlocked_characters: list[int] = []
        self.unlocked_karts: list[int] = []
        self.unlocked_cups: list[int] = []
        self.engine_upgrade_level = 0
        self.kart_upgrades: dict[int, list[game_data.KartUpgrade]] = {i:[] for i, _ in enumerate(game_data.KARTS)}
        self.unlocked_cup_skips: int = 0
        self.unlocked_courses: list[int] = []
        self.time_trial_items: int = 0
        self.cups_courses: list[list[int]]
        self.character_item_total_weights: dict[str, list[int]] = {}
        self.global_items_total_weights: list[int] = []
        self.character_items: dict[game_data.Character, list[game_data.Item]] = {character:[] for character in game_data.CHARACTERS}
        self.global_items: list[game_data.Item] = []
        self.starting_position: int = 7
        self.overlapping_start_traps: int = 0

        # Menu-level data.
        self.menu_pointer: int = 0
        self.mode: int = 0
        self.vehicle_class: int = 0
        self.active_characters: list[game_data.Character] = [game_data.CHARACTERS[0], game_data.CHARACTERS[0]]
        self.active_kart: game_data.Kart = game_data.KARTS[0]
        self.selected_cup: int = 0
        self.selected_course: int = 0
        # Course-level data.
        self.current_course: game_data.Course = game_data.Course()
        self.course_changed: bool = False
        self.total_ranking: int = 0
        self.total_points: int = 0
        self.current_starting_position: int = 0
        # Race-level data.
        self.in_game: bool = False
        self.human_players: int = 0
        self.current_lap: int = 0
        self.in_race_placement: int = 0
        self.race_timer: int = 0
        self.race_timer_s: float = 0.0
        self.item_box: int = 0
        self.finished: bool = False
        # Print system.
        self.message_queue: list[str] = []
        self.message_time_left: int = 0
        self.text_str: list[str] = ["" for _ in range(self.memory_addresses.text_amount)]
        self.text_x: list[int] = [0 for _ in range(self.memory_addresses.text_amount)]
        self.text_y: list[int] = [0 for _ in range(self.memory_addresses.text_amount)]
        self.text_just: list[int] = [1 for _ in range(self.memory_addresses.text_amount)]
        self._current_text_id: int = 0

        # Track changes over time.
        self.last_selected_vehicle_class: int = 0
        self.last_selected_cup: int = 0
        self.last_selected_course: int = 0
        self.last_item_box: int = 0
        self.last_selected_character: list[int] = [0 for _ in range(4)]
        self.last_selected_kart: list[int] = [0 for _ in range(4)]

        # Populate custom box table.
        self.custom_box_table: dict[str, dict[int, tuple[tuple[float, float, float], int, str]]] = {}
        for course, c_boxes in locations.CUSTOM_BOXES.items():
            cb_table: dict[int, tuple[tuple[float, float, float], int, str]] = {}
            box_groups = locations.BOX_NAMES.get(course, [])
            for c_idx, c_box in enumerate(c_boxes):
                for g_idx, group in enumerate(box_groups):
                    if group.name == c_box.replaces_group:
                        loc_name: str = locations.get_loc_name_custom_box(course, c_idx)
                        loc_id: int = locations.name_to_id.get(loc_name)
                        cb_table[self.memory_addresses.item_box_data_x[course][g_idx][c_box.replaces_number]] = (c_box.position, loc_id, loc_name)
            self.custom_box_table[course] = cb_table


    def update(self):
        self.last_selected_cup = self.selected_cup
        self.last_selected_course = self.selected_course
        self.last_item_box = self.item_box
        self.last_selected_vehicle_class = self.vehicle_class
        # Menu-level data.
        self.menu_pointer = dolphin.read_word(self.memory_addresses.menu_pointer)
        self.mode = dolphin.read_word(self.memory_addresses.mode_w)
        self.vehicle_class = dolphin.read_word(self.memory_addresses.vehicle_class_w)
        self.selected_cup = dolphin.read_word(self.memory_addresses.cup_w)
        self.selected_course: int = int(dolphin.read_word(self.memory_addresses.menu_course_w))
        # Course-level data.
        self.total_ranking = dolphin.read_word(self.memory_addresses.total_ranking_w)
        self.total_points = dolphin.read_word(self.memory_addresses.total_points_wx)
        self.current_starting_position = dolphin.read_word(self.memory_addresses.starting_positions_wx)
        # Race-level data.
        self.human_players = dolphin.read_byte(self.memory_addresses.human_players_b)
        self.current_lap = dolphin.read_word(self.memory_addresses.current_lap_wx) + 1
        # Get placement and modify it to be 0-based for less confusion (rankings are also 0-based).
        self.in_race_placement = dolphin.read_word(self.memory_addresses.in_race_placement_wx) - 1

        # Course changing. Reset current course if in menu.
        if self.menu_pointer != 0 and self.current_course.id != 0:
            dolphin.write_word(self.memory_addresses.current_course_w, 0)
        course_id = dolphin.read_word(self.memory_addresses.current_course_w)
        courses: list[game_data.Course] = [c for c in game_data.COURSES if c.id == course_id]
        if course_id != self.current_course.id and len(courses) > 0:
            new_course = courses[0]
            logger.debug(f"Course changed: {new_course.name}")
            self.current_course = new_course
            self.course_changed = True
            dolphin.write_word(self.memory_addresses.item_box_p, 0) # Clean up item box data.
        else:
            self.course_changed = False
            self.item_box = dolphin.read_word(self.memory_addresses.item_box_p)

        last_race_timer = self.race_timer
        timer_pointer = dolphin.read_word(self.memory_addresses.race_timer_pointer)
        if timer_pointer:
            self.race_timer = dolphin.read_word(timer_pointer)
        else:
            self.race_timer = 0
        # Remove 182 frame headstart and convert to seconds.
        # Close enough (to 1/10th of a second), altough probably exact formula should be investigated.
        # Rounded in favor of the player.
        self.race_timer_s = (self.race_timer - 182) / 60

        last_in_game = self.in_game
        self.in_game = self.race_timer - last_race_timer > 0 and self.human_players > 0 # From countdown to finish.

        # One frame leeway in case we read finishing state after the last frame advance has happened.
        laps = self.current_course.laps if self.mode == game_data.Modes.TIMETRIAL else self.options.custom_lap_counts.get(self.current_course.name, 3)
        self.finished = (self.in_game or last_in_game) and self.current_lap > laps


    def sync_state(self) -> None:
        """Sets game state to match client data about unlocks."""
        for character in range(len(game_data.CHARACTERS)):
            dolphin.write_byte(
                self.memory_addresses.available_characters_bx + character,
                int(character in self.unlocked_characters)
            )
        for k in range(len(game_data.KARTS)):
            kart = game_data.KARTS[k]
            dolphin.write_byte(
                self.memory_addresses.available_karts_bx + kart.unlock_id,
                int(k in self.unlocked_karts)
            )
        dolphin.write_word(self.memory_addresses.max_vehicle_class_w, self.unlocked_vehicle_class)
        dolphin.write_bytes(self.memory_addresses.tt_items_bx, game_data.TT_ITEM_TABLE[self.time_trial_items])
    

    def check_item_box_locations(self) -> set[str]:
        """Check for locations that are granted from item boxes."""
        if (not self.in_game 
                or self.options.item_boxes_as_locations == options.ItemBoxesAsLocations.option_disabled
                or self.item_box == self.last_item_box
                or self.item_box == 0):
            return set()
        
        logger.debug(f"Box: {hex(self.item_box)}")
        course_name = self.current_course.name
        if course_name == "Luigi Circuit": # LC has different layout and boxes on 50cc.
            course_name += " 50cc" if self.vehicle_class == 0 else " 100cc"
        
        # Check first for custom item box.
        if self.options.add_custom_item_boxes:
            custom_item_box = self.custom_box_table.get(course_name, {}).get(self.item_box)
            if custom_item_box:
                return {custom_item_box[2]}
        
        # Normal item box if custom is not enabled or not found.
        box_groups = self.memory_addresses.item_box_data_x.get(course_name, [])
        for (group_idx, box_ids) in enumerate(box_groups):
            if self.item_box in box_ids:
                if self.options.item_boxes_as_locations == options.ItemBoxesAsLocations.option_boxsanity:
                    return {locations.get_loc_name_item_box(self.current_course.name, group_idx, box_ids.index(self.item_box))}
                else: # Groups or interesting locations (latter also uses groups just not all of them).
                    return {locations.get_loc_name_item_box(self.current_course.name, group_idx)}
        return set()
    

    def update_item_box_visuals(self, locations_checked: set[int]) -> None:
        """
        Update item box visuals (takes effect when the box spawns).
        Boxes that are unchecked, are inverted by changing their x size to -1 resulting in look reminiscent of MK64 boxes.
        """
        course_name = self.current_course.name
        if course_name == "Luigi Circuit": # LC has different layout and boxes on 50cc.
            course_name += " 50cc" if self.vehicle_class == 0 else " 100cc"
        
        box_groups = self.memory_addresses.item_box_data_x.get(course_name, [])
        for (group_idx, box_ids) in enumerate(box_groups):
            custom_boxes = {}
            if self.options.add_custom_item_boxes:
                custom_boxes = self.custom_box_table.get(course_name, {})
            if self.options.item_boxes_as_locations == options.ItemBoxesAsLocations.option_boxsanity:
                for box_idx, box_address in enumerate(box_ids):
                    if box_address in custom_boxes:
                        continue
                    loc_name: str = locations.get_loc_name_item_box(self.current_course.name, group_idx, box_idx)
                    size_x = 1 if locations.name_to_id.get(loc_name) in locations_checked else -1
                    dolphin.write_float(box_address + 12, size_x)
            else:
                if (self.options.item_boxes_as_locations == options.ItemBoxesAsLocations.option_interesting_locations and
                        locations.TAG_ITEM_BOX_INTERESTING not in locations.BOX_NAMES[self.current_course.name][group_idx].tags):
                    continue
                loc_name: str = locations.get_loc_name_item_box(self.current_course.name, group_idx)
                size_x = 1 if locations.name_to_id.get(loc_name) in locations_checked else -1
                for box_idx, box_address in enumerate(box_ids):
                    if box_address in custom_boxes:
                        continue
                    dolphin.write_float(box_address + 12, size_x)
        
        if not self.options.add_custom_item_boxes:
            return
        for box_address, box_data in self.custom_box_table.get(course_name, {}).items():
            box_position = box_data[0]
            box_location_id = box_data[1]
            for i in range(3):
                dolphin.write_float(box_address + i * 4, box_position[i])
            if self.options.item_boxes_as_locations != options.ItemBoxesAsLocations.option_disabled: # These boxes are always a group of 1 and interesting locations, so all options are handled the same.
                size_x = 1 if box_location_id in locations_checked else -1
                dolphin.write_float(box_address + 12, size_x)
    

    def check_finish_course_locations(self) -> set[str]:
        """Checks for locations that are given upon finishing a track in either TT or GP mode."""
        if self.finished:
            return {locations.get_loc_name_finish(self.current_course.name)}
        else:
            return set()


    def check_take_lead_locations(self) -> set[str]:
        """Checks for locations that are given upon being in first place after the first lap."""
        if (self.mode == game_data.Modes.GRANDPRIX
                and self.in_game
                and self.current_lap > 1 
                and self.in_race_placement != 0):
            return {locations.get_loc_name_lead(self.current_course.name)}
        else:
            return set()


    def check_gp_race_locations(self) -> set[str]:
        """Checks for locations that are given upon winning a race."""
        new_locations: set[str] = set()
        if self.mode != game_data.Modes.GRANDPRIX or not self.finished or self.in_race_placement != 0:
            return new_locations
        
        # Win in course.
        new_locations.add(locations.get_loc_name_first(self.current_course.name))

        # Win with default character pairs.
        character1 = min(c.id for c in self.active_characters)
        character2 = max(c.id for c in self.active_characters)
        if character1 % 2 == 0 and character1 + 1 == character2:
            new_locations.add(locations.get_loc_name_win_characters(
                game_data.CHARACTERS[character1].name, game_data.CHARACTERS[character2].name
            ))

        # Win with default character + kart combination.
        for character in self.active_characters:
            kart = game_data.KARTS[character.default_kart]
            if self.active_kart == kart:
                new_locations.add(locations.get_loc_name_win_char_kart(character.name, kart.name))
        
        # Win with course owner.
        owner_count = 0
        for character in self.current_course.owners:
            if game_data.CHARACTERS[character] in self.active_characters:
                owner_count += 1
            if owner_count == len(self.current_course.owners):
                new_locations.add(locations.get_loc_name_win_course_char(self.current_course))
        
        return new_locations
    
        
    def check_gp_cup_locations(self) -> set[str]:
        """Checks for locations that from finishing GP cups."""
        new_locations: set[str] = set()
        if self.mode != game_data.Modes.CEREMONY or self.selected_cup == game_data.CUP_ALL_CUP_TOUR:
            return new_locations
        
        cup_name = game_data.CUPS[self.selected_cup]
        
        # Finish a cup.
        new_locations.add(locations.get_loc_name_finish(cup_name))

        # Bronze or better. Add all variants that are considered easier than current (ie. 50 bronze for 150 gold finish).
        if self.total_ranking <= 2:
            for r in range(2, self.total_ranking - 1, -1):
                for c in range(self.vehicle_class + 1):
                    new_locations.add(locations.get_loc_name_cup(cup_name, r, c))
                    if r == 0:
                        new_locations.add(locations.get_loc_name_trophy(cup_name, c))
        
        # Gold for various vehicles.
        if self.total_ranking == 0:
            if self.active_kart.weight == 0:
                new_locations.add(locations.GOLD_LIGHT)
            elif self.active_kart.weight == 1:
                new_locations.add(locations.GOLD_MEDIUM)
            elif self.active_kart.weight == 2:
                new_locations.add(locations.GOLD_HEAVY)
            elif self.active_kart.weight == -1:
                new_locations.add(locations.GOLD_PARADE)
        
        # Perfect score.
        if self.total_points == 40:
            new_locations.add(locations.get_loc_name_perfect(cup_name))

        return new_locations


    def check_all_cup_tour_locations(self) -> set[str]:
        """Checks for winning in All Cup Tour."""
        if (self.mode == game_data.Modes.CEREMONY and 
                self.selected_cup == game_data.CUP_ALL_CUP_TOUR and
                self.total_ranking == 0):
            return {locations.WIN_ALL_CUP_TOUR}
        else:
            return set()


    def check_tt_locations(self) -> set[str]:
        """Checks for locations that are time trials specific."""
        new_locations: set[str] = set()
        if not self.finished or self.mode != game_data.Modes.TIMETRIAL:
            return new_locations

        if self.race_timer_s < self.current_course.good_time:
            new_locations.add(locations.get_loc_name_good_time(self.current_course))
        if self.race_timer_s < self.current_course.staff_time:
            new_locations.add(locations.get_loc_name_ghost(self.current_course.name))
        return new_locations


    def print_ingame(self, x: int, y: int, text: str, justification: int = 1, msg_id: int = -1) -> None:
        """
        Print text in game.

        :param x: X coorditate, from 0 (left) to 608 (right).
        :param y: Y coordinate, from 12 (top) to 450 (bottom).
        :param text: The text to show. One line only, max 43 characters.
        :param justification: 1 for left justification, 0 for center, -1 for right.
        :param msg_id: Id for the text. From 0 upwards. Using same id replaces the text. Default = automatic.
        """
        if msg_id == -1:
            msg_id = self._current_text_id
            self._current_text_id = min(self._current_text_id + 1, self.memory_addresses.text_amount - 1)
        self.text_str[msg_id] = text
        self.text_x[msg_id] = x
        self.text_y[msg_id] = y
        self.text_just[msg_id] = justification


    def queue_ingame_message(self, message: str) -> None:
        """
        Show message in game. If there's multiple messages, they will be shown one after another.

        :param message: The message to show. Can be 2 lines long.
        """
        self.message_queue.append(message)
        if len(self.message_queue) == 1:
            self.message_time_left = 40
    

    def flush_ingame_text(self) -> None:
        """Prints queued text and resets the message table."""
        self._current_text_id = 0
        font_size = 12

        # In game message system
        self.message_time_left -= 1
        if self.message_time_left > 0:
            lines: list[str] = self.message_queue[0].split("\n")
            for i, text in enumerate(lines):
                # Use text slots from the end to interfere minimally with other texts.
                text_id = self.memory_addresses.text_amount - i - 1
                self.print_ingame(304, 13 + i * font_size, text, 0, text_id)
                
        # Try to show the message first, only then check for new message.
        # This causes one tick long disappearing of the message between messages,
        # making message changing more noticeable.
        if self.message_time_left == 0:
            self.message_queue.pop(0)
            if len(self.message_queue) > 0:
                self.message_time_left = 40
        
        for idx in range(self.memory_addresses.text_amount):
            text = self.text_str[idx][:43]
            text_width = len(text) * font_size
            x = self.text_x[idx] + int(text_width * (self.text_just[idx] - 1) / 2)
            y = self.text_y[idx]
            address = self.memory_addresses.text_sx + idx * self.memory_addresses.text_size
            dolphin_write_str(address, text)
            dolphin_write_half(address + self.memory_addresses.text_x_offset_h, x)
            dolphin_write_half(address + self.memory_addresses.text_y_offset_h, y)

            self.text_str[idx] = ""


    def handle_character_menu(self) -> None:
        """
        Updates state about selected characters and karts.
        Ensures that the player chooses valid characters and karts.
        Prints character/kart info in game.
        """
        if self.menu_pointer == 0:
            return
        target_icons = self.memory_addresses.menu_pointer_to_char_icons.get(self.menu_pointer)
        if target_icons:
            for (char_id, address) in enumerate(target_icons):
                if char_id in self.unlocked_characters:
                    dolphin.write_word(address, 0x0100FFFF)
                else:
                    dolphin.write_word(address, 0x0000FFFF)

        driver = dolphin.read_word(self.menu_pointer + self.memory_addresses.menu_driver_w_offset)
        rider = dolphin.read_word(self.menu_pointer + self.memory_addresses.menu_rider_w_offset)
        # Save active selections for printing info.
        p1_character: game_data.Character | None = None
        p2_character: game_data.Character | None = None
        p1_kart: game_data.Kart | None = None
        # Save selections for later use (when menu pointer becomes invalid).
        if driver >= 0 and driver < len(game_data.CHARACTERS):
            self.active_characters[0] = game_data.CHARACTERS[driver]
            p1_character = self.active_characters[0]
        if rider >= 0 and rider < len(game_data.CHARACTERS):
            self.active_characters[1] = game_data.CHARACTERS[rider]
            p2_character = self.active_characters[1]
        
        for player in range(4):
            player_offset = player * self.memory_addresses.menu_player_struct_size
            character: int = int(dolphin.read_word(self.menu_pointer + self.memory_addresses.menu_character_w_offset + player_offset))
            kart: int = int(dolphin.read_word(self.menu_pointer + self.memory_addresses.menu_kart_w_offset + player_offset))
            
            if character >= 0 and character < len(game_data.CHARACTERS):
                if player == 0:
                    if not p1_character:
                        # Player 1 is choosing the driver.
                        p1_character = game_data.CHARACTERS[character]
                    else:
                        # Player 1 is choosing the rider.
                        p2_character = game_data.CHARACTERS[character]
                elif player == 1:
                    # Player 2 can choose only the rider.
                    p2_character = game_data.CHARACTERS[character]

                # Force character selection.
                if character not in self.unlocked_characters:
                    direction: int = character - self.last_selected_character[player]
                    direction = 1 if direction == 0 or direction == 1 else -1
                    for _ in range(len(game_data.CHARACTERS)):
                        character = wrap(character + direction, len(game_data.CHARACTERS))
                        if character in self.unlocked_characters:
                            break
                    dolphin.write_word(self.menu_pointer + self.memory_addresses.menu_character_w_offset + player_offset, character)

            self.last_selected_character[player] = character
            
            if kart >= 0 and kart < len(game_data.KARTS):
                # Force kart selection.
                weight = max(self.active_characters[0].weight, self.active_characters[1].weight)
                direction: int = kart - self.last_selected_kart[player]
                direction = 1 if direction == 0 else int(direction / abs(direction))
                for _ in range(len(game_data.KARTS)):
                    if kart in self.unlocked_karts and (game_data.KARTS[kart].weight == weight or game_data.KARTS[kart].weight == -1):
                        break
                    kart = wrap(kart + direction, len(game_data.KARTS))
                dolphin.write_word(self.menu_pointer + self.memory_addresses.menu_kart_w_offset + player_offset, kart)

                if player == 0:
                    self.active_kart = game_data.KARTS[kart]
                    p1_kart = self.active_kart
            self.last_selected_kart[player] = kart

        # Print selected kart or characters and their items.
        def _get_character_text(char: game_data.Character, items: list[game_data.Item]) -> str:
            if len(items) == 0:
                return f"{char.name} (no items)"
            text = f"{char.name}: {", ".join([item.name for item in items])}"
            if len(text) > 40:
                text = f"{char.name}: {", ".join([item.short_name for item in items])}"
            if len(text) > 43:
                text = text[:41] + ".."
            return text

        text_x = 92
        text_y1 = 215
        text_y2 = 240
        text_y3 = 265
        if p1_kart:
            kart_upgrade_text = ", ".join(u.short_name for u in self.kart_upgrades[p1_kart.id])
            self.print_ingame(text_x, text_y1, f"{p1_kart.name} {kart_upgrade_text}")
        elif p1_character:
            p1_items: list[game_data.Item] = self.character_items.get(p1_character, []).copy()
            p1_items.extend(self.global_items)
            if p2_character:
                p2_items: list[game_data.Item] = self.character_items.get(p2_character, []).copy()
                p2_items.extend(self.global_items)
                # Check for synergy (default character combo).
                character1 = min(p1_character.id, p2_character.id)
                character2 = max(p1_character.id, p2_character.id)
                if character1 % 2 == 0 and character1 + 1 == character2 or character1 >= 16 and character2 >= 16:
                    # Remove global items and add p2 items (including global items).
                    for _ in self.global_items:
                        p1_items.pop()
                    p1_items.extend(p2_items)
                    p2_items = p1_items
                    if len(p2_items) > 0:
                        self.print_ingame(text_x, text_y3, "Item synergy")
                self.print_ingame(text_x, text_y2, _get_character_text(p2_character, p2_items))
            self.print_ingame(text_x, text_y1, _get_character_text(p1_character, p1_items))


    def apply_shuffled_courses(self) -> None:
        """Changes what courses are in what cups."""
        # Apply shuffled courses only upon selecting vehicle class.
        if self.vehicle_class == self.last_selected_vehicle_class:
            return
        
        offset = self.memory_addresses.cup_contents_wx
        for i_cup in self.cups_courses:
            for i_course in i_cup:
                dolphin.write_word(offset, game_data.COURSES[i_course].id)
                dolphin.write_word(offset + 4, self.memory_addresses.course_names_s[i_course])
                dolphin.write_word(offset + 8, self.memory_addresses.course_previews_s[i_course])
                offset += 12


    def apply_item_box_items(self) -> None:
        """Tells the game what items should come from item boxes."""
        if self.mode != game_data.Modes.GRANDPRIX or not self.in_game:
            return
        
        def _calculate_and_apply(adr: int, pool: list[game_data.Item], total_weight: int) -> None:
            item_weights = [item.weight_table[self.in_race_placement] for item in pool]
            # Yet to be unlocked items still count towards item weights so fill the rest with nothing.
            weight_gap = total_weight - sum(item_weights)
            if weight_gap > 0:
                pool.append(game_data.ITEM_NONE)
                item_weights.append(weight_gap)
            rand_item = game_data.ITEM_NONE
            if len(pool) > 0:
                rand_item = random.sample(pool, 1, counts = item_weights)[0]
            dolphin.write_byte(adr, rand_item.id)
        
        item_adr_0: int = self.memory_addresses.gp_next_items_bx + self.active_characters[0].item_offset
        item_adr_1: int = self.memory_addresses.gp_next_items_bx + self.active_characters[1].item_offset
        item_weight_global: int = self.global_items_total_weights[self.in_race_placement]
        item_weight_0: int = self.character_item_total_weights[self.active_characters[0].name][self.in_race_placement]
        item_weight_1: int = self.character_item_total_weights[self.active_characters[1].name][self.in_race_placement]
        item_pool_0: list[game_data.Item] = self.character_items[self.active_characters[0]]
        item_pool_1: list[game_data.Item] = self.character_items[self.active_characters[1]]
        
        if item_adr_0 != item_adr_1: # No item synergy, handle separately.
            _calculate_and_apply(item_adr_0, self.global_items + item_pool_0, item_weight_global + item_weight_0)
            _calculate_and_apply(item_adr_1, self.global_items + item_pool_1, item_weight_global + item_weight_1)
        else: # Item synergy, combine item pools.
            total_weight = item_weight_global + item_weight_0 + item_weight_1
            item_pool = self.global_items + item_pool_0 + item_pool_1
            _calculate_and_apply(item_adr_0, item_pool, total_weight)


    def apply_lap_counts(self) -> None:
        """Modifies lap counts to match custom (or short) lap counts if playing in GP."""
        if self.mode == game_data.Modes.TIMETRIAL:
            # Use vanilla lap counts in time trials.
            for i_course in game_data.RACE_COURSES:
                dolphin.write_byte(self.memory_addresses.lap_count_bx + i_course.id, i_course.laps)
        elif self.mode == game_data.Modes.GRANDPRIX:
            # Use custom lap counts in grand prix.
            for i_course in game_data.RACE_COURSES:
                dolphin.write_byte(self.memory_addresses.lap_count_bx + i_course.id, self.options.custom_lap_counts[i_course.name])


    def handle_all_cup_tour(self) -> None:
        """Shortens All Cup Tour if option is set and shuffles its contents."""
        if self.selected_cup != game_data.CUP_ALL_CUP_TOUR:
            return
        # Set All Cup Tour length by skipping to the second-last race. This ensures that Rainbow Road is still the last.
        if dolphin.read_word(self.memory_addresses.gp_race_no_w) == self.options.all_cup_tour_length - 2:
            dolphin.write_word(self.memory_addresses.gp_race_no_w, 14)
        
        # Shuffle All Cup Tour properly with randomized courses.
        if self.selected_cup != self.last_selected_cup:
            course_order = list(range(1, 15)) # First is LC, last is RR - shuffle everything between.
            random.shuffle(course_order)
            course_order = [0, *course_order, 15]
            flat_course_list = [i_course for i_cup in self.cups_courses for i_course in i_cup]
            offset = 0
            for i_course in course_order:
                dolphin.write_word(
                        self.memory_addresses.all_cup_tour_contents_wx + offset,
                        flat_course_list.index(i_course)
                )
                offset += 4


    def apply_course_availability(self) -> None:
        """Prevent the game from allowing the selection of locked courses."""
        # Make a table of currently unlocked courses.
        available_cups_courses: dict[int, set[int]] = {} # Key: Cup (0-4), value: selectable courses in cup (0-3).
        if self.mode == game_data.Modes.TIMETRIAL:
            for i_cup in range(4):
                for i_course in self.unlocked_courses:
                    if i_course in self.cups_courses[i_cup]:
                        if i_cup not in available_cups_courses:
                            available_cups_courses[i_cup] = set()
                        available_cups_courses[i_cup].add(self.cups_courses[i_cup].index(i_course))
            if len(available_cups_courses) == 0 and self.menu_pointer == 0:
                self.print_ingame(304, 180, "No Time Trials unlocked yet!", 0)
                self.print_ingame(304, 200, "Change mode to Grand Prix.", 0)
        elif self.mode == game_data.Modes.GRANDPRIX:
            # Give option to skip x first courses.
            gp_selectable_courses = range(self.unlocked_cup_skips + 1)
            for i_cup in self.unlocked_cups:
                if i_cup == game_data.CUP_ALL_CUP_TOUR:
                    available_cups_courses[i_cup] = [0]
                else:
                    available_cups_courses[i_cup] = gp_selectable_courses

        # Force cup and course selection.
        if len(available_cups_courses) > 0:
            if self.selected_cup not in available_cups_courses:
                direction: int = self.selected_cup - self.last_selected_cup
                direction = 1 if direction == 0 or direction == 1 else -1
                for _ in range(5):
                    self.selected_cup = wrap(self.selected_cup + direction, len(game_data.CUPS))
                    if self.selected_cup in available_cups_courses:
                        break
                dolphin.write_word(self.memory_addresses.cup_w, self.selected_cup)

            for i_cup in range(len(game_data.CUPS)):
                dolphin.write_byte(self.memory_addresses.available_cups_bx + i_cup, int(i_cup in available_cups_courses))

            if self.selected_course not in available_cups_courses[self.selected_cup]:
                direction: int = self.selected_course - self.last_selected_course
                direction = 1 if direction == 0 or direction == 1 else -1
                for _ in range(4):
                    self.selected_course = wrap(self.selected_course + direction, 4)
                    if self.selected_course in available_cups_courses[self.selected_cup]:
                        break
                dolphin.write_word(self.memory_addresses.menu_course_w, self.selected_course)


    def apply_200cc(self) -> None:
        """Makes mirror mode 200cc if option is enabled."""
        if self.mode == game_data.Modes.GRANDPRIX and self.vehicle_class == 3 and self.options.mirror_200cc:
            dolphin.write_float(self.memory_addresses.speed_multiplier_150cc_f, 1.4)
            dolphin.write_float(self.memory_addresses.max_speed_f, 250)
        else:
            dolphin.write_float(self.memory_addresses.speed_multiplier_150cc_f, 1.15)
            dolphin.write_float(self.memory_addresses.max_speed_f, 200)


    def apply_kart_stats(self) -> None:
        """Writes custom kart stats into game."""
        kart_stats_pointer = self.memory_addresses.kart_stats_pointer
        for i in range(len(game_data.KARTS)):
            kart: game_data.Kart = game_data.KARTS[i]
            kart_address = kart_stats_pointer + i * self.memory_addresses.kart_struct_size

            speed_1_multiplier = 1.0
            speed_2_multiplier = 1.0
            speed_3_multiplier = 1.0
            speed_4_multiplier = 1.0
            acceleration_1_addition = 0.0
            acceleration_2_addition = 0.0
            mini_turbo_addition = 0.0
            weight_addition = 0.0
            steer_addition = 0.0
            # Upgrades apply to the player only (by side-effect also bots using the same kart).
            if kart == self.active_kart:
                speed_1_multiplier = self.calculate_speed_multiplier()
                for upgrade in self.kart_upgrades[i]:
                    if upgrade == game_data.KART_UPGRADE_ACC:
                        acceleration_1_addition += 1
                        acceleration_2_addition += .1
                    elif upgrade == game_data.KART_UPGRADE_OFFROAD:
                        speed_2_multiplier *= 1.1
                        speed_3_multiplier *= 1.2
                        speed_4_multiplier *= 3
                    elif upgrade == game_data.KART_UPGRADE_WEIGHT:
                        weight_addition += 2
                    elif upgrade == game_data.KART_UPGRADE_TURBO:
                        mini_turbo_addition += 30
                    elif upgrade == game_data.KART_UPGRADE_STEER:
                        steer_addition += 1
            # Speed 1 (on road) is also general speed multiplier.
            speed_2_multiplier *= speed_1_multiplier
            speed_3_multiplier *= speed_1_multiplier
            speed_4_multiplier *= speed_1_multiplier
            stats = kart.stats
            
            dolphin.write_float(kart_address + self.memory_addresses.kart_speed_on_road_f_offset, stats.speed_on_road * speed_1_multiplier)
            dolphin.write_float(kart_address + self.memory_addresses.kart_speed_off_road_sand_f_offset, stats.speed_off_road_sand * speed_2_multiplier)
            dolphin.write_float(kart_address + self.memory_addresses.kart_speed_off_road_grass_f_offset, stats.speed_off_road_grass * speed_3_multiplier)
            dolphin.write_float(kart_address + self.memory_addresses.kart_speed_off_road_mud_f_offset, stats.speed_off_road_mud * speed_4_multiplier)
            dolphin.write_float(kart_address + self.memory_addresses.kart_acceleration_1_f_offset, stats.acceleration_1 + acceleration_1_addition)
            dolphin.write_float(kart_address + self.memory_addresses.kart_acceleration_2_f_offset, stats.acceleration_2 + acceleration_2_addition)
            dolphin.write_float(kart_address + self.memory_addresses.kart_mini_turbo_f_offset, stats.mini_turbo + mini_turbo_addition)
            dolphin.write_float(kart_address + self.memory_addresses.kart_mass_f_offset, stats.mass + weight_addition)
            dolphin.write_float(kart_address + self.memory_addresses.kart_roll_f_offset, stats.roll)
            dolphin.write_float(kart_address + self.memory_addresses.kart_steer_f_offset, stats.steer + steer_addition)


    def calculate_speed_multiplier(self) -> float:
        # Engine upgrades by levels: .9, 1, 1.05, 1.1
        if self.engine_upgrade_level == 0:
            return .9
        elif self.engine_upgrade_level > 1:
            return .95 + self.engine_upgrade_level * .05
        return 1.0


    def handle_starting_position(self) -> None:
        """Forces the player to start at the right position."""
        if self.current_starting_position == self.starting_position:
            return
        
        dolphin.write_word(self.memory_addresses.starting_positions_wx, self.starting_position)
        for i in range(1, 8):
            cpu_position = dolphin.read_word(self.memory_addresses.starting_positions_wx + i * 4)
            # Push up if player should be below this.
            if cpu_position >= self.starting_position and cpu_position < self.current_starting_position:
                cpu_position += 1
            # Push down if player should be above this.
            elif cpu_position <= self.starting_position and cpu_position > self.current_starting_position:
                cpu_position -= 1
            dolphin.write_word(self.memory_addresses.starting_positions_wx + i * 4, cpu_position)
        logger.debug(f"Adjusted starting position to {self.starting_position}")


    def handle_overlapping_start_trap(self) -> None:
        """Forces all karts into the same starting position if trap is received."""
        if self.overlapping_start_traps == 0:
            return
        
        if self.course_changed and self.current_course in game_data.RACE_COURSES:
            self.overlapping_start_traps = max(0, self.overlapping_start_traps - 1)
            logger.debug(f"Removed overlap trap. Traps remaining: {self.overlapping_start_traps}")

        p2_pos: int = dolphin.read_word(self.memory_addresses.starting_positions_wx + 4)
        if p2_pos == self.current_starting_position:
            return
        
        for i in range(8):
            dolphin.write_word(self.memory_addresses.starting_positions_wx + i * 4, self.starting_position)
        logger.debug(f"Applied overlap trap. Traps remaining: {self.overlapping_start_traps}")


def dolphin_write_half(address: int, value: int) -> None:
    """Write a half-word/short (2 bytes) into memory."""
    dolphin.write_bytes(address, value.to_bytes(2, byteorder="big"))


def dolphin_write_str(address: int, value: str) -> None:
    """Write a string into memory."""
    dolphin.write_bytes(address, bytes(value, "ascii", "replace"))
    dolphin.write_byte(address + len(value), 0)


def wrap(value: int, max_value: int) -> int:
    if value < 0:
        return max_value - 1
    if value >= max_value:
        return 0
    return value
