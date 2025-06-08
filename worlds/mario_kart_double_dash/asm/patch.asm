.macro WriteTo address
.long \address
.long \address
.endm

.set char_unlock_table, 0x80001000
.set kart_unlock_table, 0x80001000 + 0x14
.set race_counter, 0x80001000 + 0x2c
.set menu_pointer, 0x80001000 + 0x30
.set race_timer, 0x80001000 + 0x34
.set max_vehicle_class, 0x80001000 + 0x38
.set cup_unlock_table, 0x80001000 + 0x3c
.set tt_driver_item, 0x80001000 + 0x41
.set tt_rider_item, 0x80001000 + 0x42
.set gp_next_item, 0x80001000 + 0x43

# 4 bytes for position, 44 for string per text. text_table points to the start of the string, x and y are offset -4 and -2.
.set text_table, 0x80000da0 + 4
.set text_size, 0x30
.set text_amount, 5


# SECTION character_selection
# Change character flag setter to a custom one (below) when picking random characters.
# The original function must be left intact as it's used for cpu character selection also.
.set jump_set_char_flags, 0x80165744 + 0x4 - 0x801638b0
WriteTo 0x801638b0
bl      jump_set_char_flags

# Character flag setter, checks for unclocked ap characters.
WriteTo 0x80165744
blr     # Return early, skip checking for vanilla character unlocks.
li      r0, 20
li      r5, 0
lis     r31, char_unlock_table@ha
addi    r31, r31, char_unlock_table@l
mtctr   r0
addi    r0, r5, 8864
lbzx    r4, r31, r5
stbx    r4, r3, r0
addi    r5, r5, 1
bdnz+   -0x10
blr

# Select left. After checking if we can move left once, continue in zig zag pattern.
.set select_left_jump, 0x800010d8 - 0x801636cc
.set select_left_return, 0x801636cc + 4 - 0x800010d8 - 0x24
WriteTo 0x801636cc
b   select_left_jump
WriteTo 0x800010d8
bne-    0x24
addi    r4, r29, 19
divw    r0, r4, r3
mullw   r0, r0, r3
sub     r29, r4, r0
addi    r0, r29, 0x228c
lbzx    r0, r28, r0
cmplwi  r0, 0
beq+    -0x1c
b       select_left_return

# Select right. After checking if we can move right once, continue in zig zag pattern.
.set select_right_jump, 0x80001100 - 0x801636f8
.set select_right_return, 0x801636f8 + 4 - 0x80001100 - 0x24
WriteTo 0x801636f8
b   select_right_jump
WriteTo 0x80001100
bne-    0x24
addi    r4, r29, 21
divw    r0, r4, r3
mullw   r0, r0, r3
sub     r29, r4, r0
addi    r0, r29, 0x228c
lbzx    r0, r28, r0
cmplwi  r0, 0
beq+    -0x1c
b       select_right_return

# Intercept cursor moving function checking flags for valid characters.
WriteTo 0x801639bc
lis     r6, char_unlock_table@ha
addi    r6, r6, char_unlock_table@l
mtctr   r0
b       0xb8

# No need for check Toads + Boo + Petey, replace with checking ap characters.
WriteTo 0x80163a7c
blr     # Return earlier than the original function.
addi    r0, r5, 8844
lbzx    r4, r6, r5
stbx    r4, r3, r0
addi    r5, r5, 1
bdnz+   -0x10
b       -0xc0


# SECTION race_counter
.set race_counter_jump, 0x80163a98 - 0x801ce0cc
.set race_counter_return, 0x801ce0d0 - 0x80163ab0
lis     r3, race_counter@ha
addi    r3, r3, race_counter@l
lwz     r23, 0 (r3)
addi    r23, r23, 1
stw     r23, 0 (r3)
li      r0, 0 # default code
b       race_counter_return

WriteTo 0x801ce0cc
b       race_counter_jump


# SECTION kart_selection
WriteTo 0x801dbc90
lis     r12, kart_unlock_table@ha
addi    r12, r12, kart_unlock_table@l
lbzx    r3, r12, r3
blr

.set menu_pointer_write_jump, 0x80000f98 - 0x801599fc
.set menu_pointer_write_return, 0x80159a00 - 0x80000fa8
WriteTo 0x801599fc
b       menu_pointer_write_jump
WriteTo 0x80000f98
lis     r3, menu_pointer@ha
addi    r3, r3, menu_pointer@l
stw     r30, 0 (r3)
mr      r3, r30 # default code
b       menu_pointer_write_return

.set menu_pointer_clear_jump, 0x80000fac - 0x8016a4e0
.set menu_pointer_clear_return, 0x8016a4e4 - 0x80000fc0
WriteTo 0x8016a4e0
b       menu_pointer_clear_jump
WriteTo 0x80000fac
lis     r3, menu_pointer@ha
addi    r3, r3, menu_pointer@l
li      r0, 0
stw     r0, 0 (r3)
lwz     r3, -0x5588 (r13) # default code
b       menu_pointer_clear_return


# SECTION cup_selection
# Move right
.set cup_selection_right_jump, 0x80000fd4 - 0x8016b090 - 0x8
.set cup_selection_right_return, 0x8016b090 + 0xc - 0x80000ff0
WriteTo 0x8016b090
lis     r4, cup_unlock_table@ha
addi    r4, r4, cup_unlock_table@l
b       cup_selection_right_jump
nop
lwz     r4, 0x0390 (r31)    # default code
lfs     f0, -0x5FF4 (rtoc)  # default code
WriteTo 0x80000fd4
addi    r3, r3, 1           # Move cursor
cmpwi   r3, 5               # Wrap around
bne     0x8
li      r3, 0
lbzx    r5, r4, r3          # Check cup availability, loops if =0
cmpwi   r5, 0
beq     -6 * 4
b       cup_selection_right_return

# Make All Cup Tour visible even in time trials (because we are using tt menu for gp also).
WriteTo 0x80169f20
nop

# Move left
.set cup_selection_left_jump, 0x80001080 - 0x8016b028 - 0xc
.set cup_selection_left_return, 0x8016b028 + 0x10 - 0x8000109c
WriteTo 0x8016b028
lwz     r3, -0x5C78 (r13)
lis     r4, cup_unlock_table@ha
addi    r4, r4, cup_unlock_table@l
b       cup_selection_left_jump
nop
nop
li      r0, 0               # default code
lwz     r5, 0x0390 (r31)    # default code
lfs     f0, -0x5FF4 (rtoc)  # default code
WriteTo 0x80001080
subi    r3, r3, 1           # Move cursor
cmpwi   r3, -1              # Wrap around
bne     0x8
li      r3, 4
lbzx    r5, r4, r3          # Check cup availability, loops if =0
cmpwi   r5, 0
beq     -6 * 4
b       cup_selection_left_return


# SECTION race_timer
.set race_timer_jump, 0x80000fc4 - 0x801dce0c
WriteTo 0x801dce0c
b   race_timer_jump
WriteTo 0x80000fc4
lis     r3, race_timer@ha
addi    r3, r3, race_timer@l
stw     r0, 0 (r3)
blr


# SECTION vehicle_class_selector
# Move right.
WriteTo 0x8015ee60
lis     r3, max_vehicle_class@ha
addi    r3, r3, max_vehicle_class@l
lwz     r3, 0 (r3)
cmpw    r0, r3
ble     0xf0
nop
# Move left.
WriteTo 0x8015edac
lis     r3, max_vehicle_class@ha
addi    r3, r3, max_vehicle_class@l
lwz     r3, 0 (r3)
cmpw    r0, r3
ble     0x8015ee80 - 0x8015edbc
mr      r0, r3
nop


# SECTION time_trial_items
# Driver
.set driver_item_jump, 0x800010a0 - 0x802baf7c
.set driver_item_return, 0x802baf7c + 4 - 0x800010a0 - 8
WriteTo 0x802baf7c
b driver_item_jump
WriteTo 0x800010a0
lis     r4, tt_driver_item@ha
lbz     r4, tt_driver_item@l (r4)
b driver_item_return
# Rider
.set rider_item_jump, 0x800010ac - 0x802bafa8
.set rider_item_return, 0x802bafa8 + 4 - 0x800010ac - 8
WriteTo 0x802bafa8
b rider_item_jump
WriteTo 0x800010ac
lis     r4, tt_rider_item@ha
lbz     r4, tt_rider_item@l (r4)
b rider_item_return


# SECTION item_shuffle
.set item_shuffle_jump, 0x800010b8 - 0x8020cbc0
.set item_shuffle_return_player, 0x8020cbc0 + 8 - 0x800010b8 - 0x18
.set item_shuffle_return_cpu, 0x8020cbc0 + 4 - 0x800010b8 - 0x1c
WriteTo 0x8020cbc0
b       item_shuffle_jump
WriteTo 0x800010b8
stw     r0, 0x24 (r1)
cmplwi  r0, 0
bne+    0x14
lis     r3, gp_next_item@ha
addi    r3, r3, gp_next_item@l
lbzx    r3, r3, r5 # Offset by assumed special item.
b       item_shuffle_return_player
b       item_shuffle_return_cpu

# SECTION draw_string
.set jutreport_jump, 0x80019c4c - 0x80001128 - 10*4
WriteTo 0x80001128
# Push stack.
stwu    sp, -0x10 (sp)
mflr    r0
stw     r0, 0x14 (sp)
stw     r31, 0x8 (sp)
# Draw texts.
li      r31, 0
lis     r5, text_table@ha   # String address
addi    r5, r5, text_table@l
add     r5, r5, r31
lhz     r3, -4 (r5)         # X position
lhz     r4, -2 (r5)         # Y position
bl      jutreport_jump
addi    r31, r31, text_size
cmplwi  r31, text_size * text_amount
blt+    -0x20
# Pop stack.
lwz     r31, 0x8 (sp)
lwz     r0, 0x14 (sp)
mtlr    r0
addi    sp, sp, 0x10
blr
# Call the print function in the character selection screen.
.set draw_string_character_jump, 0x80001128 + 19*4 - 0x80159434
.set draw_string_character_return, 0x80159434 + 4 - 0x80001128 - 21*4
bl      -19 * 4
lwz     r0, 0x20E0 (r31)    # default code
b       draw_string_character_return
# Call the print function in the course selection screen.
.set draw_string_course_jump, 0x80001128 + 22*4 - 0x8016a380
.set draw_string_course_return, 0x8016a380 + 4 - 0x80001128 - 24*4
bl      -22 * 4
lfs     f1, -0x603C (rtoc)  # default code
b       draw_string_course_return
# Call the print function during race.
.set draw_string_race_jump, 0x80001128 + 25*4 - 0x801cd91c
.set draw_string_race_return, 0x801cd91c + 4 - 0x80001128 - 27*4
bl      -25 * 4
lwz     r0, 0x0014 (sp)     # default code
b       draw_string_race_return

WriteTo 0x80159434
b       draw_string_character_jump
WriteTo 0x8016a380
b       draw_string_course_jump
WriteTo 0x801cd91c
b       draw_string_race_jump
