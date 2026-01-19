# Mario Kart: Double Dash!! Archipelago Randomizer

This is an Archipelago implementation for Mario Kart: Double Dash!!. In case you aren't familiar with Archipelago, it's a multiworld randomizer system, ie. items from one game can be found in another player's game! Read more at [archipelago.gg](https://archipelago.gg/).

## What does randomization do to this game?

Characters, karts, items, cups and access to time trial courses are shuffled into the item pool. There's also upgrades for the karts and character specific items. The courses in the cups can be also shuffled. The locations include winning races in each course, getting bronze/silver/gold cups at various vehicle classes and winning races with certain character/kart/course combinations (for example, win with Mario driving Red Fire or win with Daisy at Daisy Cruiser).

## What is the goal of the game?

Collect enough gold trophies and finish All Cup Tour.

## When the player receives an item, what happens?

Currently there is no in-game notification system and the game generally doesn't have any visual indication of what's unlocked. You can refer to the client to see what's unlocked (there's a nifty `/unlocked` command which tells you what do you have).

## What game modes are available?

Grand Prix and Time Trial. 2 players on one kart should work, but is untested (you may want to enable 2 player time trials cheat code to be able to get all the checks). 3-4 players is unsupported.

## Setup

See [setup guide](docs/en_Setup.md) for a throughout explanation and troubleshooting.

If you are familiar with the general Archipelago workflow, here's a super quick guide:
* Install the apworld and set up your multiworld as usual. Having [Universal Tracker](https://github.com/FarisTheAncient/Archipelago/releases) is recommended.
* Launch the client from Archipelago Launcher.
* Launch Mario Kart: Double Dash!! (NTSC-U/USA) in Dolphin.
* Connect to the host.

You're good to go!

## Special Thanks

* To **Yoshi2** for patiently showing me the ropes of reverse engineering! This is my first romhacking project so help was really needed!
* To **Ralph@gc-forever** for making tons of cheat codes for MKDD and allowing me to use them for the randomizator! Some of them are used by the project as is (see [ar_codes.py](ar_codes.py) for complete list) and many of them have given insight to make some custom features myself.
* To **ItzRonsku** and **Hugeli** for testing.
