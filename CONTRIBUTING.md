# Contributing to MKDD AP
Are you interested in helping out with the project? Contributions are welcome and help with romhacking side are especially appreciated! Before implementing features it would be good to ask if it fits into my vision of course. Discussion on Issues page is encouraged to have it all well documented.

## How to Start
For starters, you should get the [Archipelago source](https://github.com/ArchipelagoMW/Archipelago) and ensure you can build it ([here](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/running%20from%20source.md) are the instructions for that).
You should then fork this repo and clone it into Archipelago/worlds folder. I recommend naming the folder as `mario_kart_double_dash`. So in the end the directory should look like this:
```
Archipelago
-worlds
--mario_kart_double_dash
---__init__.py (and the rest of the files)
```

## Helpful Resources
For working with Archipelago, check Archipelago's [docs](https://github.com/ArchipelagoMW/Archipelago/tree/main/docs)
For modding the game:
- [MKDD thread at gc-forever](https://www.gc-forever.com/forums/viewtopic.php?t=2436) (tons of AR codes)
- [MKDD Wiki](https://mkdd.org/wiki/Main_Page) (general resource)
- Some files in this project:
  - [mem_addresses.py](mem_addresses.py) (list of memory addresses used by MKDD AP)
  - [game_data.py](game_data.py) (character/item/course ids and some stats)
  - [asm/patch.asm](asm/patch.asm) (patch source file)
