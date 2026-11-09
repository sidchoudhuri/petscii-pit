#!/usr/bin/env python3
"""Stand-alone full-volume .sid files, PAL and NTSC:
   petscii-pit-{pal,ntsc}.sid   - all songs (Dungeoneering, Assailing, Lamenting)
   <song>-{pal,ntsc}.sid        - one song each
Writes into ./sids. Afterwards rebuilds the normal in-game music data."""
import os
import struct
import subprocess

BASE = 0x9700
SONGS = ["Dungeoneering", "Assailing", "Lamenting"]
AUTHOR, RELEASED = "m0nde", "12 October, 2026"


def field(s):
    return s.encode("latin-1")[:32].ljust(32, b"\0")


os.makedirs("sids", exist_ok=True)
for std, flags, env in (("pal", 0x0014, {}), ("ntsc", 0x0018, {"NTSC": "1"})):
    subprocess.run(["python3", "compose.py"], check=True,
                   env=dict(os.environ, FULL_VOLUME="1", **env), stdout=subprocess.DEVNULL)
    subprocess.run(["acme", "-f", "cbm", "-o", "x.prg", f"-DBASE=${BASE:04x}",
                    "player.asm"], check=True)
    prg = open("x.prg", "rb").read()
    code = prg[2:]
    start = prg[0] | prg[1] << 8                     # file starts below the jump table
    assert start + len(code) <= 0xA000

    def write(fn, title, init, songs, body):
        h = b"PSID" + struct.pack(">HHHHHHHI", 2, 0x7C, 0, init, BASE + 3, songs, 1, 0)
        h += field(title) + field(AUTHOR) + field(RELEASED)
        h += struct.pack(">HBBH", flags, 0, 0, 0)       # PAL/NTSC, 6581
        open(os.path.join("sids", fn), "wb").write(h + body)
        print(fn, "-", title)

    write(f"petscii-pit-{std}.sid", "PETSCII Pit", BASE, len(SONGS), prg)
    for song, name in enumerate(SONGS):
        # 5-byte stub in front of the player: lda #song / jmp init
        load = start - 5
        stub = bytes([0xA9, song, 0x4C, BASE & 255, BASE >> 8])
        write(f"{name.lower()}-{std}.sid", f"PETSCII Pit - {name}", load, 1,
              bytes([load & 255, load >> 8]) + stub + code)

subprocess.run(["python3", "compose.py"], check=True, stdout=subprocess.DEVNULL)
