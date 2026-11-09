#!/usr/bin/env python3
"""Build the in-game music files musicpal.prg and musicntsc.prg.

Both play the full, original mix (same as the stand-alone .sid files). With a
second SID at $D420 the player moves the music there; with one SID the music
and the game's sound effects share the chip.
The file loads at $9600 (programs using it do POKE 56,150); the jump table
stays at $9700, so every SYS address is unchanged. The PAL and NTSC files
share the same code.
"""
import os
import subprocess

BASE = 0x9700          # jump table (SYS addresses)
LOAD = BASE - 0x100    # file starts one page lower (second-SID detection)


def build(out, ntsc):
    env = dict(os.environ, FULL_VOLUME="1")
    if ntsc:
        env["NTSC"] = "1"
    else:
        env.pop("NTSC", None)
    subprocess.run(["python3", "compose.py"], check=True, env=env)
    subprocess.run(["acme", "-f", "cbm", "-o", out, "-r", "tune.lst",
                    f"-DBASE=${BASE:04x}", "player.asm"], check=True)
    prg = open(out, "rb").read()
    end = LOAD + len(prg) - 2
    assert prg[0] | prg[1] << 8 == LOAD and end <= 0xA000, "player overruns $A000"
    print(f"{out}: ${LOAD:04X}-${end - 1:04X} ({len(prg) - 2} bytes)")


build("musicntsc.prg", ntsc=True)
build("musicpal.prg", ntsc=False)       # last, so music.asm is left as PAL

names = ["init", "play", "start", "stop", "fx", "fxhold", "clrarr", "clrmap",
         "fight", "resume", "pause", "unpause", "mood", "sids"]
offs = [0, 3, 6, 9, 12, 15, 16, 19, 22, 25, 28, 31, 34, 37]
print(f"POKE 56,{LOAD >> 8}")
for name, off in zip(names, offs):
    print(f"  {name:8} {BASE + off}")
