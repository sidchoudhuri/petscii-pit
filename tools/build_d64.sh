#!/bin/sh
# usage: tools/build_d64.sh <version>   (run from the repo folder)
# Builds the two disks from prg/ and applies their directory art:
#   petsciipit.d64       - the game: loader, STORY, ENDLESS, ARENA, ENDING, music,
#                          the story levels (made by tools/pitlevels.py from
#                          src/levels.txt) and their index (read back from the disk)
#                          (tools/dirlayout29.bin)
#   petsciipit-disk2.d64 - the extras: a copy of the loader, the demo, the glyph
#                          showcase and the Grand Medley (both versions, taken
#                          from grand-medley/pitmedley.d64) (tools/dirlayout29b.bin)
# The disk ID is the version, e.g. tools/build_d64.sh 29
set -e
T="$(dirname "$0")"
rm -rf petsciipit.d64 petsciipit-disk2.d64 _levels
python3 "$T/pitlevels.py" build _levels >/dev/null
cp _levels/levels.prg prg/levels.prg
c1541 -format "petscii pit,$1" d64 petsciipit.d64 -write prg/petsciipitloader.prg petsciipit -write prg/petsciipitstory.prg story -write prg/petsciipitendless.prg endless -write prg/petsciipitarena.prg arena -write prg/petsciipitending.prg ending -write prg/musicpal.prg musicpal -write prg/musicntsc.prg musicntsc -write prg/levels.prg levels >/dev/null
python3 "$T/pitlevels.py" index petsciipit.d64
mv levelidx.prg prg/levelidx.prg
c1541 -attach petsciipit.d64 -write prg/levelidx.prg levelidx >/dev/null
python3 "$T/dirlayout.py" petsciipit.d64 dirlayout29.bin
rm -rf _levels
mkdir _medley
for f in pitmedley medleypal medleyntsc democode demohi demodng pitmedleybas; do
  c1541 -attach grand-medley/pitmedley.d64 -read $f _medley/$f.prg >/dev/null
done
c1541 -format "petscii pit 2,$1" d64 petsciipit-disk2.d64 -write prg/petsciipitloader.prg petsciipit -write prg/petsciipitdemo.prg demo -write prg/glyphshowcase.prg showcase -write _medley/pitmedley.prg pitmedley -write prg/musicpal.prg musicpal -write prg/musicntsc.prg musicntsc -write _medley/medleypal.prg medleypal -write _medley/medleyntsc.prg medleyntsc -write _medley/democode.prg democode -write _medley/demohi.prg demohi -write _medley/demodng.prg demodng -write _medley/pitmedleybas.prg pitmedleybas >/dev/null
python3 "$T/dirlayout.py" petsciipit-disk2.d64 dirlayout29b.bin
rm -rf _medley
c1541 -attach petsciipit.d64 -list
c1541 -attach petsciipit-disk2.d64 -list
