#!/bin/sh
# usage: tools/buildprgs.sh   (run from the repo folder)
# Crunches each listing in src/ into its program in prg/ (tools/crunch.py
# checks that the crunched program means exactly the same as the listing).
set -e
T="$(dirname "$0")"
for f in petsciipitloader petsciipitstory petsciipitendless petsciipitdemo glyphshowcase; do
  python3 "$T/crunch.py" src/$f.bas prg/$f.prg
done
