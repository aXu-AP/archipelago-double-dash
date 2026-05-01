.set insert_adr, 0x80001080

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

.macro REGION name
    .long 0x00aabbaa
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

# 4 bytes for position, 44 for string per text. text_sx points to the start of the string, x and y are offset -4 and -2.
.set text_sx, 0x80000da0 + 4
.set text_size, 0x30
.set text_amount, 5


REGION character_selection
# Change character flag setter to a custom one (below) when picking random characters.
# The original function must be left intact as it's used for cpu character selection also.
.set jump_set_char_flags, 0x80165744 + 0x4 - 0x801638b0
WriteTo 0x801638b0
    bl      jump_set_char_flags

# Character flag setter, checks for unclocked ap characters.
WriteTo 0x80165744
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
WriteTo 0x801639bc
    lis     r6, available_characters_bx@ha
    addi    r6, r6, available_characters_bx@l
    mtctr   r0
    b       0xb8                # Jump to unlock_check.
# No need for check Toads + Boo + Petey, replace with checking ap characters.
WriteTo 0x80163a7c
    blr     # Return earlier than the original function.
    addi    r0, r5, 8844        # unlock_check
    lbzx    r4, r6, r5
    stbx    r4, r3, r0
    addi    r5, r5, 1
    bdnz+   -0x10
    b       -0xc0


REGION kart_selection
# Just overwrite the kart unlock check, there's nothing we need from the original code.
WriteTo 0x801dbc90
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
InsertAt 0x801599fc, 3
    lis     r3, menu_pointer@ha
    stw     r30, menu_pointer@l (r3)
    mr      r3, r30 # Default code.
Return

# Clear the pointer when exiting character selection menu.
InsertAt 0x8016a4e0, 4
    li      r0, 0
    lis     r3, menu_pointer@ha
    stw     r0, menu_pointer@l (r3)
    lwz     r3, -0x5588 (r13) # Default code.
Return


REGION cup_selection
# Make All Cup Tour visible even in time trials (because we are using tt menu for gp also).
WriteTo 0x80169f20
    nop

# Move right
WriteTo 0x8016b090
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
WriteTo 0x8016b028
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
WriteTo 0x8015ee60
    lis     r3, max_vehicle_class_w@ha
    addi    r3, r3, max_vehicle_class_w@l
    lwz     r3, 0 (r3)
    cmpw    r0, r3
    ble     0xf0
    nop

# Move left.
WriteTo 0x8015edac
    lis     r3, max_vehicle_class_w@ha
    addi    r3, r3, max_vehicle_class_w@l
    lwz     r3, 0 (r3)
    cmpw    r0, r3
    ble     0x8015ee80 - 0x8015edbc
    mr      r0, r3
    nop


REGION time_trial_items
# Driver
InsertAt 0x802baf7c, 2
    lis     r4, tt_items_driver_b@ha
    lbz     r4, tt_items_driver_b@l (r4)
Return

# Rider
InsertAt 0x802bafa8, 2
    lis     r4, tt_items_rider_b@ha
    lbz     r4, tt_items_rider_b@l (r4)
Return


REGION item_shuffle
.set item_shuffle_jump, 0x8020cbc0
.set item_shuffle_return_player, item_shuffle_jump + 8
InsertAt item_shuffle_jump, 6
    stw     r0, 0x24 (r1)
    cmplwi  r0, 0
    bne+    0x14            # Return if cpu.
    lis     r3, gp_next_items_bx@ha
    addi    r3, r3, gp_next_items_bx@l
    lbzx    r3, r3, r5      # Offset by assumed special item.
ReturnAt item_shuffle_return_player
Return


REGION item_box
InsertAt 0x801fbe1c, 7
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    5*4
    lwz     r4, 0xe8 (r3)       # Load box's id.
    lis     r3, item_box_p@ha
    stw     r4, item_box_p@l (r3)
    li      r4, 0               # Return value to 0.
    lwz	    r3, -0x5560 (r13)   # Default code.
Return


REGION rolling_item_box
InsertAt 0x8027d1e4, 7
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    5*4
    lwz     r4, 0xe8 (r3)       # Load box's id.
    lis     r31, item_box_p@ha
    stw     r4, item_box_p@l (r31)
    li      r4, 0               # Return value to 0.
    mr      r31, r3             # Default code.
Return


REGION car_item_box
InsertAt 0x8019a69c, 6
    cmplwi  r4, 0               # Skip for other karts than no. 0 (player).
    bne+    4*4
    lwz     r30, 0xe8 (r3)      # Load box's id.
    lis     r31, item_box_p@ha
    stw     r30, item_box_p@l (r31)
    mr      r30, r3             # Default code.
Return


REGION draw_string
# Call the print function in the character selection screen.
InsertAt 0x80159434, 2
    bl      9 * 4
    lwz     r0, 0x20E0 (r31)    # Default code.
Return
# Call the print function in the course selection screen.
InsertAt 0x8016a380, 2
    bl      6 * 4
    lfs     f1, -0x603C (rtoc)  # Default code.
Return
# Call the print function during race.
InsertAt 0x801cd91c, 2
    bl      3 * 4
    lwz     r0, 0x0014 (sp)     # Default code.
Return

Write 10
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
    blr
