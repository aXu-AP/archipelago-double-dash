# This file is generated automatically by convert_asm.py.
# To modify the patches, edit .asm files directly and rerun convert.
character_selection: dict[int, list[int]] = {
    0x801638b0: [
        0x48001e99,
    ],
    0x80165744: [
        0x4e800020,
        0x38000014,
        0x38a00000,
        0x3fe08000,
        0x3bff1000,
        0x7c0903a6,
        0x380522a0,
        0x7c9f28ae,
        0x7c8301ae,
        0x38a50001,
        0x4200fff0,
        0x4e800020,
    ],
    0x801636cc: [
        0x4be9d9b4,
    ],
    0x80001080: [
        0x40820024,
        0x389d0013,
        0x7c041bd6,
        0x7c0019d6,
        0x7fa02050,
        0x381d228c,
        0x7c1c00ae,
        0x28000000,
        0x4182ffe4,
        0x4816262c,
    ],
    0x801636f8: [
        0x4be9d9b0,
    ],
    0x800010a8: [
        0x40820024,
        0x389d0015,
        0x7c041bd6,
        0x7c0019d6,
        0x7fa02050,
        0x381d228c,
        0x7c1c00ae,
        0x28000000,
        0x4182ffe4,
        0x48162630,
    ],
    0x801639bc: [
        0x3cc08000,
        0x38c61000,
        0x7c0903a6,
        0x480000b8,
    ],
    0x80163a7c: [
        0x4e800020,
        0x3805228c,
        0x7c8628ae,
        0x7c8301ae,
        0x38a50001,
        0x4200fff0,
        0x4bffff40,
    ],
}
kart_selection: dict[int, list[int]] = {
    0x801dbc90: [
        0x3ca08000,
        0x80a51030,
        0x2c050000,
        0x41820014,
        0x3ca08000,
        0x38a51014,
        0x7c6518ae,
        0x4e800020,
        0x38600001,
        0x4e800020,
    ],
}
update_menu_pointer: dict[int, list[int]] = {
    0x801599fc: [
        0x4bea76d4,
    ],
    0x800010d0: [
        0x3c608000,
        0x93c31030,
        0x7fc3f378,
        0x48158924,
    ],
    0x8016a4e0: [
        0x4be96c00,
    ],
    0x800010e0: [
        0x38000000,
        0x3c608000,
        0x90031030,
        0x806daa78,
        0x481693f4,
    ],
}
cup_selection: dict[int, list[int]] = {
    0x80169f20: [
        0x60000000,
    ],
    0x8016b090: [
        0x3c808000,
        0x3884103c,
        0x60000000,
        0x60000000,
        0x809f0390,
        0xc002a00c,
    ],
    0x8016b098: [
        0x4be9605c,
    ],
    0x800010f4: [
        0x38630001,
        0x2c030005,
        0x40820008,
        0x38600000,
        0x7ca418ae,
        0x2c050000,
        0x4182ffe8,
        0x48169f8c,
    ],
    0x8016b028: [
        0x806da388,
        0x3c808000,
        0x3884103c,
        0x60000000,
        0x60000000,
        0x60000000,
        0x38000000,
        0x80bf0390,
        0xc002a00c,
    ],
    0x8016b034: [
        0x4be960e0,
    ],
    0x80001114: [
        0x3863ffff,
        0x2c03ffff,
        0x40820008,
        0x38600004,
        0x7ca418ae,
        0x2c050000,
        0x4182ffe8,
        0x48169f08,
    ],
}
vehicle_class_selector: dict[int, list[int]] = {
    0x8015ee60: [
        0x3c608000,
        0x38631038,
        0x80630000,
        0x7c001800,
        0x408100f0,
        0x60000000,
    ],
    0x8015edac: [
        0x3c608000,
        0x38631038,
        0x80630000,
        0x7c001800,
        0x408100c4,
        0x7c601b78,
        0x60000000,
    ],
}
time_trial_items: dict[int, list[int]] = {
    0x802baf7c: [
        0x4bd461b8,
    ],
    0x80001134: [
        0x3c808000,
        0x88841041,
        0x482b9e44,
    ],
    0x802bafa8: [
        0x4bd46198,
    ],
    0x80001140: [
        0x3c808000,
        0x88841042,
        0x482b9e64,
    ],
}
item_shuffle: dict[int, list[int]] = {
    0x8020cbc0: [
        0x4bdf458c,
    ],
    0x8000114c: [
        0x90010024,
        0x28000000,
        0x40a20014,
        0x3c608000,
        0x38631043,
        0x7c6328ae,
        0x4820ba64,
        0x4820ba5c,
    ],
}
item_box: dict[int, list[int]] = {
    0x801fbe1c: [
        0x4be05350,
    ],
    0x8000116c: [
        0x28040000,
        0x40a20014,
        0x808300e8,
        0x3c608000,
        0x90831060,
        0x38800000,
        0x806daaa0,
        0x481fac98,
    ],
}
rolling_item_box: dict[int, list[int]] = {
    0x8027d1e4: [
        0x4bd83fa8,
    ],
    0x8000118c: [
        0x28040000,
        0x40a20014,
        0x808300e8,
        0x3fe08000,
        0x909f1060,
        0x38800000,
        0x7c7f1b78,
        0x4827c040,
    ],
}
car_item_box: dict[int, list[int]] = {
    0x8019a69c: [
        0x4be66b10,
    ],
    0x800011ac: [
        0x28040000,
        0x40a20010,
        0x83c300e8,
        0x3fe08000,
        0x93df1060,
        0x7c7e1b78,
        0x481994dc,
    ],
}
draw_string: dict[int, list[int]] = {
    0x80159434: [
        0x4bea7d94,
    ],
    0x800011c8: [
        0x48000025,
        0x801f20e0,
        0x48158268,
    ],
    0x8016a380: [
        0x4be96e54,
    ],
    0x800011d4: [
        0x48000019,
        0xc0229fc4,
        0x481691a8,
    ],
    0x801cd91c: [
        0x4be338c4,
    ],
    0x800011e0: [
        0x4800000d,
        0x80010014,
        0x481cc738,
    ],
    0x800011ec: [
        0x9421fff0,
        0x7c0802a6,
        0x90010014,
        0x93e10008,
        0x3be00000,
        0x3ca08000,
        0x38a50da4,
        0x7ca5fa14,
        0xa065fffc,
        0xa085fffe,
        0x48018a39,
    ],
    0x80001218: [
        0x3bff0030,
        0x281f00f0,
        0x4180ffe0,
        0x83e10008,
        0x80010014,
        0x7c0803a6,
        0x38210010,
        0x4e800020,
    ],
}
