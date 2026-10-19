#!/bin/sh
# PETSCII Pit - Grand Medley demo build (machine code and BASIC versions)
# needs: python3 with py65 and Pillow, ACME 0.96+
# src/ needs: petsciipitloader.bas, me-petscii.prg, chargen.bin (C64 font ROM),
#             petscii-pit-medley-pal.sid, petscii-pit-medley-ntsc.sid
#             (basictest.py/loadertest.py also want basic-901226-01.bin, kernal-901227-03.bin)
set -e
cd "$(dirname "$0")"
python3 gen.py                                  # strips, portrait, dungeon, texts, song length
acme --vicelabels build/medley.lbl medley.asm   # build/democode.prg ($0900-)
acme loader.asm                                 # build/pitmedley.prg (SYS 2061 loader)
python3 gen_basic.py                            # pitmedleybas.bas
python3 build_disk.py --basic                   # build/pitmedley.d64 with both versions
python3 simtest.py PAL 400                      # machine code: IRQ and drawing timing in py65
