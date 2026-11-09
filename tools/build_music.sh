#!/bin/sh
# usage: tools/build_music.sh   (run from the repo folder; needs acme)
# Builds prg/musicpal.prg and prg/musicntsc.prg from src/music (compose.py
# writes the tune data music.asm, player.asm is the player). With "sids" it
# also makes the stand-alone .sid files in sid/ (with the current player).
set -e
cd src/music
python3 build.py
mv musicpal.prg musicntsc.prg ../../prg/
if [ "$1" = "sids" ]; then
  mkdir -p sids && python3 makesids.py && mv sids/*.sid ../../sid/ && rmdir sids
fi
rm -f music.asm tune.lst x.prg
