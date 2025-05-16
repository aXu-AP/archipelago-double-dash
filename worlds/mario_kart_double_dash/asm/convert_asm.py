import os
import subprocess

def convert(input_path: str, out: list) -> None:
    if subprocess.call(["powerpc-gekko-as.exe", "-a32", "-mbig", "-mregnames", "-mgekko", input_path]) != 0:
        print(f"Couldn't convert file {input_path}.")
        return
    
    out.append(f"{input_path.removesuffix(".asm")} = {{\n")
    with open("a.out", "rb") as obj:
        obj.seek(0x34)
        last_word = 0
        first_address = True
        while True:
            read_bytes = obj.read(4)
            if len(read_bytes) < 4:
                break
            word = int.from_bytes(read_bytes, "big")
            # Beginning of the other data... Let's just hope this value is never met in the code.
            if word == 0x002E7379:
                out.append(f"    ]\n}}\n")
                break
            # Another hack. 2 sequential, identical words which could be valid addresses mark an offset for the code.
            # Probably a safe assumption that this would never make sense in actual program data.
            if last_word == word and word >= 0x8000_0000 and word < 0x817f_ffff:
                out.pop()
                if first_address:
                    out.append(f"    0x{word:08x}: [\n")
                    first_address = False
                else:
                    out.append(f"    ],\n    0x{word:08x}: [\n")
            else:
                out.append(f"        0x{word:08x},\n")
            last_word = word

os.chdir("worlds/mario_kart_double_dash/asm")

out = [
    "# This file is generated automatically by convert_asm.py.\n",
    "# To modify the patches, edit .asm files directly and rerun convert.\n",
]

for file in os.listdir("."):
    if file.endswith(".asm"):
        convert(file, out)

with open("patches.py", "w") as out_file:
    out_file.writelines(out)
