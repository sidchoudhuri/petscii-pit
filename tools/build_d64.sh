#!/bin/sh
# usage: tools/build_d64.sh <version>   (run from the repo folder)
# Builds petsciipit.d64 from prg/: the programs, the story levels (made by
# tools/pitlevels.py from src/levels.txt) and their index (read back from the
# disk), then applies the directory art (tools/dirlayout24.bin).
# The disk ID is the version, e.g. tools/build_d64.sh 27
set -e
T="$(dirname "$0")"
rm -rf petsciipit.d64 _levels
python3 "$T/pitlevels.py" build _levels >/dev/null
cp _levels/levels.prg prg/levels.prg
c1541 -format "petscii pit,$1" d64 petsciipit.d64 -write prg/petsciipitloader.prg petsciipit -write prg/petsciipitstory.prg story -write prg/petsciipitendless.prg endless -write prg/petsciipitdemo.prg demo -write prg/glyphshowcase.prg showcase -write prg/musicpal.prg musicpal -write prg/musicntsc.prg musicntsc -write prg/levels.prg levels >/dev/null
python3 "$T/pitlevels.py" index petsciipit.d64
mv levelidx.prg prg/levelidx.prg
c1541 -attach petsciipit.d64 -write prg/levelidx.prg levelidx >/dev/null
python3 "$T/dirlayout.py" petsciipit.d64 dirlayout24.bin
rm -rf _levels
c1541 -attach petsciipit.d64 -list
