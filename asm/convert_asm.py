import os
import subprocess

END_OF_PROGRAM = 0x002E7379
NEW_BLOCK = 0x00aabbee

def convert(input_path: str, out: list) -> None:
    if subprocess.call(["powerpc-gekko-as.exe", "-a32", "-mbig", "-mregnames", "-mgekko", input_path]) != 0:
        print(f"Couldn't convert file {input_path}.")
        return
    
    blocks: dict[int, int] = {}
    with open("a.out", "rb") as obj:
        obj.seek(0x34)
        new_key: int = 0
        new_block: list[int] = []
        while True:
            read_bytes = obj.read(4)
            if len(read_bytes) < 4:
                break
            word = int.from_bytes(read_bytes, "big")
            if word == END_OF_PROGRAM:
                break
            elif word == NEW_BLOCK:
                if new_key == 0:
                    continue
                blocks[new_key] = new_block
                new_key = 0
                new_block = []
            elif new_key == 0:
                # New block is just started, the first word should be used as the key.
                new_key = word
            else:
                new_block.append(word)
        if new_key != 0:
            blocks[new_key] = new_block
    
    # Finally, write the contents.
    out.append(f"{input_path.removesuffix(".asm")} = {{\n")
    for key, block in blocks.items():
        out.append(f"    0x{key:08x}: [\n")
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
