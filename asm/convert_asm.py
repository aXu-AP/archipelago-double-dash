import os
import subprocess

END_OF_PROGRAM = 0x002E7379
NEW_REGION = 0x00aabbaa
NEW_BLOCK = 0x00aabbee

def convert(input_path: str, out: list) -> None:
    region_names: list[str] = ["patch"] # Default name before any regions are defined.
    with open(input_path) as f:
        while True:
            line: str = f.readline()
            if not line:
                break
            if line.startswith("REGION"):
                region_names.append(line.split()[1])
    
    if subprocess.call(["powerpc-gekko-as.exe", "-a32", "-mbig", "-mregnames", "-mgekko", input_path]) != 0:
        print(f"Couldn't convert file {input_path}.")
        return
    
    regions: dict[str, dict[int, int]] = {}
    with open("a.out", "rb") as obj:
        obj.seek(0x34)
        current_region_idx = 0
        new_region_name: str = region_names[current_region_idx]
        new_region: dict[int, int] = {}
        new_address: int = 0
        new_block: list[int] = []
        while True:
            read_bytes = obj.read(4)
            if len(read_bytes) < 4:
                break
            word = int.from_bytes(read_bytes, "big")
            if word == END_OF_PROGRAM:
                break
            elif word == NEW_REGION:
                if new_address != 0: # Finish current block.
                    new_region[new_address] = new_block
                    new_address = 0
                    new_block = []
                if len(new_region) > 0:
                    regions[new_region_name] = new_region
                current_region_idx += 1
                new_region_name = region_names[current_region_idx]
                new_region = {}
                print(f"Region {new_region_name}")
            elif word == NEW_BLOCK:
                if new_address == 0:
                    continue
                new_region[new_address] = new_block
                new_address = 0
                new_block = []
            elif new_address == 0:
                # New block is just started, the first word should be used as the key.
                new_address = word
                print(f"  Block {new_address}")
            else:
                new_block.append(word)
        
        # At the end of file flush new blocks and regions.
        if new_address != 0:
            new_region[new_address] = new_block
        if len(new_region) > 0:
            regions[new_region_name] = new_region
    
    # Finally, write the contents.
    for name, region in regions.items():
        out.append(f"{name}: dict[int, list[int]] = {{\n")
        for address, block in region.items():
            out.append(f"    0x{address:08x}: [\n")
            for line in block:
                out.append(f"        0x{line:08x},\n")
            out.append("    ],\n")
        out.append("}\n")

os.chdir("worlds/mario_kart_double_dash/asm")

out = [
    "# This file is generated automatically by convert_asm.py.\n",
    "# To modify the patches, edit .asm files directly and rerun convert.\n",
]

for file in os.listdir("."):
    if file.endswith(".asm"):
        convert(file, out)

os.chdir("..")
with open("patches.py", "w") as out_file:
    out_file.writelines(out)
