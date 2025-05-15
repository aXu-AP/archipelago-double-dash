.macro WriteTo address
.long \address
.long \address
.endm

# Spare space from the function below.
.set char_unlock_table, 0x80001000
.set kart_unlock_table, 0x80001000 + 0x14
.set race_counter, 0x80001000 + 0x2c

# SECTION character_selection
# Change character flag setter to a custom one (below) when picking random characters.
# The original function must be left intact as it's used for cpu character selection also.
WriteTo 0x80163840
.set jump_set_char_flags, 0x80165748 - 0x80163840
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

# This function's space has been used to the last byte.

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
