.set insert_adr, 0x80002000

# Writes code into specified address.
.macro WriteTo address
    .long 0x00aabbee
    .long \address
.endm

# Writes a branch from specified address to separate block.
.macro InsertAt address, lines
    WriteTo \address
    b   insert_adr - \address
    WriteTo insert_adr
    .set insert_adr, insert_adr + \lines * 4
    .set _last_insert, \address + 4
.endm

# Does a linked jump (bl) into new address. Assumed to be placed after InsertAt/Write lines.
.macro BranchLinkAt address
    bl  \address - insert_adr
    .set insert_adr, insert_adr + 4
.endm

# Jumps into new address after using InsertAt/Write. Assumed to be placed after InsertAt/Write lines.
.macro ReturnAt address
    b   \address - insert_adr
    .set insert_adr, insert_adr + 4
.endm

# Resumes program after using InsertAt. Assumed to be placed after InsertAt/Write lines.
.macro Return
    ReturnAt _last_insert
.endm

# Writes code into free memory.
.macro Write lines
    WriteTo insert_adr
    .set insert_adr, insert_adr + \lines * 4
.endm

# Invalidates cache at given address.
.macro Invalidate address
    lis     r12, \address@ha
    addi    r12, r12, \address@l
    dcbst   0, r12
    icbi    0, r12
    .set insert_adr, insert_adr + 4 * 4
.endm

.macro REGION name
    .long 0x00aabbaa
.endm

# Pushes stack backing up 4 registers (r28-r31).
.macro PushStack4
    stwu    sp, -0x18 (sp)
    mflr    r0
    stw     r0, 0x1c (sp)
    stmw    r28, 0x8 (sp)
.endm
# Pops stack retrieving 4 registers (r28-r31).
.macro PopStack4
    lmw     r28, 0x8 (sp)
    lwz     r0, 0x1c (sp)
    mtlr    r0
    addi    sp, sp, 0x18
.endm


.set available_characters_bx,   0x80001000 # Size 20
.set available_karts_bx,        0x80001014 # Size 21
.set menu_pointer,              0x80001030
.set max_vehicle_class_w,       0x80001038
.set available_cups_bx,         0x8000103c # Size 5
.set tt_items_driver_b,         0x80001041
.set tt_items_rider_b,          0x80001042
.set gp_next_items_bx,          0x80001043
.set item_box_p,                0x80001060
.set shuffle_queue_w,           0x80001064
.set rolling_from_queue_w,      0x80001068
.set spawn_item_id_w,           0x8000106c  # Size 7
.set spawn_item_pos_fx,         spawn_item_id_w + 4
.set spawn_item_vel_fx,         spawn_item_id_w + 16

# 4 bytes for position, 44 for string per text. text_sx points to the start of the string, x and y are offset -4 and -2.
.set text_sx, 0x80000da0 + 4
.set text_size, 0x30
.set text_amount, 5


REGION character_selection
# Change character flag setter to a custom one (below) when picking random characters.
# The original function must be left intact as it's used for cpu character selection also.
.set code_random_characters, 0x801638b0
.set code_character_flags, 0x80165744
.set jump_set_char_flags, code_character_flags + 0x4 - code_random_characters
WriteTo code_random_characters
    bl      jump_set_char_flags

# Character flag setter, checks for unclocked ap characters.
WriteTo code_character_flags
    blr     # Return early, skip checking for vanilla character unlocks.
    # set_char_flags:
    li      r0, 20
    li      r5, 0
    lis     r31, available_characters_bx@ha
    addi    r31, r31, available_characters_bx@l
    mtctr   r0
    addi    r0, r5, 8864
    lbzx    r4, r31, r5
    stbx    r4, r3, r0
    addi    r5, r5, 1
    bdnz+   -0x10
    blr

# Select left. After checking if we can move left once, continue in zig zag pattern.
.set code_character_left, 0x801636cc
InsertAt 0x801636cc, 9
    bne-    0x24
    addi    r4, r29, 19
    divw    r0, r4, r3
    mullw   r0, r0, r3
    sub     r29, r4, r0
    addi    r0, r29, 0x228c
    lbzx    r0, r28, r0
    cmplwi  r0, 0
    beq+    -0x1c
Return

# Select right. After checking if we can move right once, continue in zig zag pattern.
.set code_character_right, 0x801636f8
InsertAt 0x801636f8, 9
    bne-    0x24
    addi    r4, r29, 21
    divw    r0, r4, r3
    mullw   r0, r0, r3
    sub     r29, r4, r0
    addi    r0, r29, 0x228c
    lbzx    r0, r28, r0
    cmplwi  r0, 0
    beq+    -0x1c
Return

# Intercept cursor moving function checking flags for valid characters.
.set code_cursor_move, 0x801639bc
WriteTo code_cursor_move
    lis     r6, available_characters_bx@ha
    addi    r6, r6, available_characters_bx@l
    mtctr   r0
    b       0xb8                # Jump to unlock_check.
# No need for check Toads + Boo + Petey, replace with checking ap characters.
.set code_check_available_characters, 0x80163a7c
WriteTo code_check_available_characters
    blr     # Return earlier than the original function.
    addi    r0, r5, 8844        # unlock_check
    lbzx    r4, r6, r5
    stbx    r4, r3, r0
    addi    r5, r5, 1
    bdnz+   -0x10
    b       -0xc0


REGION kart_selection
# Just overwrite the kart unlock check, there's nothing we need from the original code.
.set code_kart_selection, 0x801dbc90
WriteTo code_kart_selection
    lis     r5, menu_pointer@ha
    lwz     r5, menu_pointer@l (r5)
    cmpwi   r5, 0
    beq     5 * 4
    lis     r5, available_karts_bx@ha
    addi    r5, r5, available_karts_bx@l
    lbzx    r3, r5, r3
    blr
    li      r3, 1               # If not in character selection menu, just return 1 (used for cpu karts).
    blr


REGION update_menu_pointer
# Write the pointer while in the character selection menu.
.set code_write_menu_pointer, 0x801599fc
InsertAt code_write_menu_pointer, 3
    lis     r3, menu_pointer@ha
    stw     r30, menu_pointer@l (r3)
    mr      r3, r30 # Default code.
Return

# Clear the pointer when exiting character selection menu.
.set code_clear_menu_pointer, 0x8016a4e0
InsertAt code_clear_menu_pointer, 4
    li      r0, 0
    lis     r3, menu_pointer@ha
    stw     r0, menu_pointer@l (r3)
    lwz     r3, -0x5588 (r13) # Default code.
Return


REGION cup_selection
# Make All Cup Tour visible even in time trials (because we are using tt menu for gp also).
.set code_all_cup_tour_show, 0x80169f20
WriteTo code_all_cup_tour_show
    nop

# Move right
.set code_cup_right, 0x8016b090
WriteTo code_cup_right
    lis     r4, available_cups_bx@ha
    addi    r4, r4, available_cups_bx@l
    nop                         # Code below is inserted here.
    nop
    lwz     r4, 0x0390 (r31)    # Default code.
    lfs     f0, -0x5FF4 (rtoc)  # Default code.
InsertAt 0x8016b098, 7
    addi    r3, r3, 1           # Move cursor.
    cmpwi   r3, 5               # Wrap around.
    bne     0x8
    li      r3, 0
    lbzx    r5, r4, r3          # Check cup availability, loops if =0.
    cmpwi   r5, 0
    beq     -6 * 4
Return

# Move left
.set code_cup_left, 0x8016b028
WriteTo code_cup_left
    lwz     r3, -0x5C78 (r13)
    lis     r4, available_cups_bx@ha
    addi    r4, r4, available_cups_bx@l
    nop                         # Code below is inserted here.
    nop
    nop
    li      r0, 0               # Default code.
    lwz     r5, 0x0390 (r31)    # Default code.
    lfs     f0, -0x5FF4 (rtoc)  # Default code.
InsertAt 0x8016b034, 7
    subi    r3, r3, 1           # Move cursor
    cmpwi   r3, -1              # Wrap around
    bne     0x8
    li      r3, 4
    lbzx    r5, r4, r3          # Check cup availability, loops if =0.
    cmpwi   r5, 0
    beq     -6 * 4
Return


REGION vehicle_class_selector
# Move right.
.set code_vehicle_class_right, 0x8015ee60
WriteTo code_vehicle_class_right
    lis     r3, max_vehicle_class_w@ha
    addi    r3, r3, max_vehicle_class_w@l
    lwz     r3, 0 (r3)
    cmpw    r0, r3
    ble     0xf0
    nop

# Move left.
.set code_vehicle_class_left, 0x8015edac
WriteTo code_vehicle_class_left
    lis     r3, max_vehicle_class_w@ha
    addi    r3, r3, max_vehicle_class_w@l
    lwz     r3, 0 (r3)
    cmpw    r0, r3
    ble     0x8015ee80 - 0x8015edbc
    mr      r0, r3
    nop


REGION time_trial_items
# Driver
.set code_tt_items_driver, 0x802baf7c
InsertAt code_tt_items_driver, 2
    lis     r4, tt_items_driver_b@ha
    lbz     r4, tt_items_driver_b@l (r4)
Return

# Rider
.set code_tt_items_rider, 0x802bafa8
InsertAt code_tt_items_rider, 2
    lis     r4, tt_items_rider_b@ha
    lbz     r4, tt_items_rider_b@l (r4)
Return


REGION item_shuffle
.set code_item_shuffle, 0x8020cbc0
.set item_shuffle_return_player, code_item_shuffle + 8
InsertAt code_item_shuffle, 13
    stw     r0, 0x24 (r1)
    cmplwi  r0, 0
    bne+    12 * 4                  # Return if cpu.

    lis     r31, rolling_from_queue_w@ha  # Check if we should receive global random item.
    lwz     r30, rolling_from_queue_w@l (r31)
    cmplwi  r30, 0
    beq     4 * 4
    li      r5, 0                   # Use offset of 0 if global item.
    subi    r30, r30, 1
    stw     r30, rolling_from_queue_w@l (r31)

    lis     r3, gp_next_items_bx@ha
    addi    r3, r3, gp_next_items_bx@l
    lbzx    r3, r3, r5              # Offset by assumed special item.
ReturnAt item_shuffle_return_player
Return


REGION force_item_shuffle
.set item_obj_mgr, 0x803cbf40
.set code_force_item_shuffle, 0x80189c50
InsertAt code_force_item_shuffle, 4
    li      r5, 1
    li      r4, 0
    lis     r3, item_obj_mgr@ha
    lwz     r3, item_obj_mgr@l (r3)
BranchLinkAt 0x8020b62c             # Check for available slot.
Write 15
    rlwinm. r0, r3, 0, 24, 31
    beq     15 * 4

    lis     r5, shuffle_queue_w@ha  # Check if we have queued items.
    lwz     r4, shuffle_queue_w@l (r5)
    cmplwi  r4, 0
    beq     11 * 4
    subi    r4, r4, 1               # Remove from to be shuffled queue.
    stw     r4, shuffle_queue_w@l (r5)
    lwz     r4, rolling_from_queue_w@l (r5)
    addi    r4, r4, 1               # Add to currently rolling queue.
    stw     r4, rolling_from_queue_w@l (r5)

    li      r5, 0
    li      r4, 0
    lis     r3, item_obj_mgr@ha
    lwz     r3, item_obj_mgr@l (r3)
BranchLinkAt 0x8020b800             # Shuffle item.
Write 1
    mr      r3, r31                 # Default code.
Return


REGION item_box
# Send box id.
.set code_send_box_id, 0x801fbe1c
InsertAt code_send_box_id, 7
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    5*4
    lwz     r4, 0xe8 (r3)       # Load box's id.
    lis     r3, item_box_p@ha
    stw     r4, item_box_p@l (r3)
    li      r4, 0               # Return value to 0.
    lwz	    r3, -0x5560 (r13)   # Default code.
Return
# Update box size.
# Grow the stack frame bigger to use more registers.
.set code_update_box_stack_1, 0x801fb77c
WriteTo code_update_box_stack_1
    PushStack4
.set code_update_box_stack_2, 0x801fb79c
WriteTo code_update_box_stack_2
    PopStack4
.set code_update_box, 0x801fb78c
InsertAt code_update_box, 7
    lwz     r12, 0x17c (r3)     # Load current mode.
    cmpwi   r12, 2
    bne-    5 * 4               # Skip if not idle.
    lwz     r12, 0xe8 (r3)      # Load box data address.
    lmw     r29, 0xc (r12)      # Load x, y, z sizes.
    stmw    r29, 0x40 (r3)      # Save x, y, z sizes.
    mr	    r31, r3             # Default code.
Return

REGION rolling_item_box
# Send box id.
.set code_rolling_box_send_id, 0x8027d1e4
InsertAt code_rolling_box_send_id, 7
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    5*4
    lwz     r4, 0xe8 (r3)       # Load box's id.
    lis     r31, item_box_p@ha
    stw     r4, item_box_p@l (r31)
    li      r4, 0               # Return value to 0.
    mr      r31, r3             # Default code.
Return
# Update box size.
# Grow the stack frame bigger to use more registers.
.set code_rolling_box_update_stack_1, 0x8027cb1c
WriteTo code_rolling_box_update_stack_1
    PushStack4
.set code_rolling_box_update_stack_2, 0x8027cb60
WriteTo code_rolling_box_update_stack_2
    PopStack4
.set code_rolling_box_update, 0x8027cb2c
InsertAt code_rolling_box_update, 4
    lwz     r12, 0xe8 (r3)      # Load box data address.
    lmw     r29, 0xc (r12)      # Load x, y, z sizes.
    stmw    r29, 0x40 (r3)      # Save x, y, z sizes.
    mr	    r31, r3             # Default code.
Return


REGION car_item_box
# Send box id.
.set code_car_box_send_id, 0x8019a69c
InsertAt code_car_box_send_id, 6
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    4*4
    lwz     r30, 0xe8 (r3)      # Load box's id.
    lis     r31, item_box_p@ha
    stw     r30, item_box_p@l (r31)
    mr      r30, r3             # Default code.
Return
# Update box size.
# Grow the stack frame bigger to use more registers.
.set code_car_box_update_stack_1, 0x8019a630
WriteTo code_car_box_update_stack_1
    PushStack4
.set code_car_box_update_stack_2, 0x8019a660
WriteTo code_car_box_update_stack_2
    PopStack4
.set code_car_box_update, 0x8019a640
InsertAt code_car_box_update, 4
    lwz     r12, 0xe8 (r3)      # Load box data address.
    lmw     r29, 0xc (r12)      # Load x, y, z sizes.
    stmw    r29, 0x40 (r3)      # Save x, y, z sizes.
    mr	    r31, r3             # Default code.
Return


REGION disable_start_pos_shuffle
.set code_disable_start_pos_shuffle, 0x8016c65c
WriteTo code_disable_start_pos_shuffle
    nop


REGION spawn_item
InsertAt 0x80189b90, 10
    lis     r5, spawn_item_id_w@ha
    lwz     r4, spawn_item_id_w@l (r5)
    cmplwi  r4, 20              # Item 20 = don't spawn any item.
    beq+    14 * 4
    li      r0, 20
    stw     r0, spawn_item_id_w@l (r5)
    addi    r6, r5, spawn_item_vel_fx@l
    addi    r5, r5, spawn_item_pos_fx@l
    lis     r3, item_obj_mgr@ha
    lwz     r3, item_obj_mgr@l (r3)
BranchLinkAt 0x8020929c         # Call occurItem.
Write 7
    cmplwi  r3, 0               # Check that item was created successfully.
    beq-    5 * 4
    li      r0, 0               # Initialize some needed data (owner id?).
    stw     r0, 0x120 (r3)
    li      r0, 1
    stb     r0, 0x124 (r3)
    lbz     r3, 0x22 (r31)      # Default code.
Return


REGION draw_string
# Call the print function during race.
.set code_draw_string, 0x801d1b58
InsertAt code_draw_string, 10
    # Push stack.
    stwu    sp, -0x10 (sp)
    mflr    r0
    stw     r0, 0x14 (sp)
    stw     r31, 0x8 (sp)
    # Draw texts.
    li      r31, 0
    lis     r5, text_sx@ha   # String address.
    addi    r5, r5, text_sx@l
    add     r5, r5, r31
    lhz     r3, -4 (r5)         # X position.
    lhz     r4, -2 (r5)         # Y position.
BranchLinkAt 0x80019c4c         # JutReport / print text.
Write 8
    addi    r31, r31, text_size
    cmplwi  r31, text_size * text_amount
    blt+    -0x20
    # Pop stack.
    lwz     r31, 0x8 (sp)
    lwz     r0, 0x14 (sp)
    mtlr    r0
    addi    sp, sp, 0x10
    lwz     r0, 0x0014 (sp)     # Default code.
Return


REGION invalidate_cache
InsertAt 0x80159394, 0          # Entering player count menu.
InsertAt 0x80162308, 0          # Entering character selection screen.
InsertAt 0x8011510c, 0          # Pausing the game.
Invalidate code_random_characters
Invalidate code_character_flags
Invalidate code_draw_string
Invalidate code_character_left
Invalidate code_character_right
Invalidate code_cursor_move
Invalidate code_check_available_characters
Invalidate code_kart_selection
Invalidate code_write_menu_pointer
Invalidate code_clear_menu_pointer
Invalidate code_all_cup_tour_show
Invalidate code_cup_right
Invalidate code_cup_left
Invalidate code_vehicle_class_right
Invalidate code_vehicle_class_left
Invalidate code_tt_items_driver
Invalidate code_tt_items_rider
Invalidate code_item_shuffle
Invalidate code_force_item_shuffle
Invalidate code_send_box_id
Invalidate code_update_box_stack_1
Invalidate code_update_box_stack_2
Invalidate code_update_box
Invalidate code_rolling_box_send_id
Invalidate code_rolling_box_update_stack_1
Invalidate code_rolling_box_update_stack_2
Invalidate code_rolling_box_update
Invalidate code_car_box_send_id
Invalidate code_car_box_update_stack_1
Invalidate code_car_box_update_stack_2
Invalidate code_car_box_update
Invalidate code_disable_start_pos_shuffle
Invalidate 0x80005420   # Lap modifier 1 (AR CODES)
Invalidate 0x80187BA0   # Lap modifier 2
Invalidate 0x801CD680   # Unlock everything
Invalidate 0x80169E94   # Allow course selection
Invalidate 0x80251CB0   # Disable reverse Lakitu
Write 2
    isync
    blr                         # Default code (all the entry points are from end of function).
