#!/usr/bin/env python3
"""PETSCII Pit: scripted test runs in VICE (x64sc, headless, warp).

Makes a throwaway TEST copy of the disk: the loader picks a game by itself,
and the game reads its keys from a script string instead of the keyboard,
with optional set-up lines (cheats) to put the player where a test needs him.
The real .bas files are never changed. Each run boots the disk, runs for a
number of CPU cycles, and saves a screenshot (and the screen text) there.

Needs VICE (x64sc, c1541) and xvfb-run. Run from the repo folder; the test
disks and screenshots go in ./vtest.

usage (from Python):
  from vicetest import make_disk, run
  d = make_disk(".", "t1", game="ENDLESS",
                keys="R" + "D"*20, setup='XP=150:TT=2:TN=2:PH=2', patches={...})
  run(d, [40e6, 60e6], "t1")

loader_keys: the title-menu keys (default: the game's key, then N for "no
rune"); when they run out the loader waits forever, so a title or menu
screen stays up for its screenshot.

Keys: one character per key press (a key only, never an empty press);
"!" stands for RETURN.
Patches are (old, new) pairs of whole listing text, applied to the test copy
only, e.g. ('2600 IF AC>90 THEN AC=90', '2600 AC=100') to force an ambush.
"""
import os, re, subprocess, sys, shutil

TOOLS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.getcwd(), "vtest")   # test disks and screenshots go here
SCREEN = 0xC000          # the game's map screen (VIC bank 3)


def patch(src, repl):
    s = src
    for old, new in repl:
        assert s.count(old) == 1, ("patch not found once", old)
        s = s.replace(old, new)
    return s


def crunch_path():
    for p in (os.path.join(TOOLS, "crunch.py"), os.path.join(TOOLS, "..", "crunch.py")):
        if os.path.exists(p):
            return p
    raise SystemExit("crunch.py not found next to vicetest.py or one folder up")


def build_prg(bas_text, out):
    tmp = out + ".bas"
    open(tmp, "w").write(bas_text)
    subprocess.run([sys.executable, crunch_path(), tmp, out],
                   check=True, stdout=subprocess.DEVNULL)


# The test lines use the variable ZY (key pointer) and K$ (key script);
# a game that uses ZY or K$ itself needs these renamed.
def make_disk(folder, name, game="ENDLESS", keys="", setup="", patches=(), loader_keys=None):
    os.makedirs(OUT, exist_ok=True)
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    # loader: menu key and the rune question come from a script
    pick = "E" if game == "ENDLESS" else "P"
    sd = os.path.join(folder, "src") if os.path.isdir(os.path.join(folder, "src")) else folder
    ld = open(os.path.join(sd, "petsciipitloader.bas")).read()
    ld = patch(ld, [
        ('500 GET A$:IF A$="" THEN 470', '500 GOSUB 9000:IF A$="" THEN 470'),
        ('580 FOR C9=-1 TO 0:GET A$:C9=(A$=""):NEXT C9:RETURN', '580 GOSUB 9000:RETURN'),
    ]) + ('9000 ZY=ZY+1:A$=MID$("%s",ZY,1):IF A$="" THEN ZY=ZY-1:GOTO 9000\n'
           '9010 RETURN\n') % (pick + "N" if loader_keys is None else loader_keys)
    build_prg(ld, os.path.join(d, "loader.prg"))
    subprocess.run([sys.executable, os.path.join(TOOLS, "textbank.py"), "attach",
                    os.path.join(sd, "texts.txt"), os.path.join(d, "loader.prg"),
                    os.path.join(folder, "prg", "musicshop.bin")],
                   check=True, stdout=subprocess.DEVNULL)
    src = "petsciipitendless.bas" if game == "ENDLESS" else "petsciipitstory.bas"
    g = open(os.path.join(sd, src)).read()
    g = patch(g, [
        ("1760 T3=TI+20:FOR C9=-1 TO 0:GET A$:C9=(A$=\"\" AND TI<T3):NEXT C9:",
         "1760 T3=TI+20:GOSUB 9000:"),
        ("4160 FOR C9=-1 TO 0:GET A$:C9=(A$=\"\" AND TI<T2):NEXT C9",
         "4160 FOR C9=-1 TO 0:C9=(TI<T2):NEXT C9:A$=\"\""),
        ("4180 GOSUB 6870:FOR C9=-1 TO 0:GET A$:C9=(A$=\"\"):NEXT C9",
         "4180 GOSUB 9020"),
        ("5540 GOSUB 4340", "5535 %s\n5540 GOSUB 4340" % (setup or "REM")),
    ] + list(patches))
    g += ('9000 A$="":IF ZY<LEN(K$) THEN ZY=ZY+1:A$=MID$(K$,ZY,1):IF A$="!" THEN A$=CHR$(13)\n'
          '9010 RETURN\n'
          '9020 GOSUB 9000:IF A$<>"" THEN RETURN\n'
          '9030 IF ZY<=LEN(K$) THEN 9020\n'
          '9040 GOTO 9040\n')
    g = g.replace("\n5535 ", "\n5535 K$=\"%s\":" % keys, 1)
    build_prg(g, os.path.join(d, "game.prg"))
    disk = os.path.join(d, "test.d64")
    shutil.copy(os.path.join(folder, "petsciipit.d64"), disk)
    fname = "endless" if game == "ENDLESS" else "story"
    subprocess.run(["c1541", "-attach", disk, "-delete", "petsciipit", "-delete", fname,
                    "-write", os.path.join(d, "loader.prg"), "petsciipit",
                    "-write", os.path.join(d, "game.prg"), fname],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return disk


def run(disk, cycles, tag):
    """Run the disk to each cycle count; return the screenshot paths."""
    shots = []
    d = os.path.dirname(disk)
    for c in cycles:
        png = os.path.join(d, "%s-%dM.png" % (tag, int(c / 1e6)))
        subprocess.run(["timeout", "600", "xvfb-run", "-a", "x64sc", "-default", "-warp",
                        "+sound", "+drive8truedrive", "-virtualdev8",
                        "-autostart", disk, "-limitcycles", str(int(c)),
                        "-exitscreenshot", png],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shots.append(png)
    return shots


if __name__ == "__main__":
    print(__doc__)
