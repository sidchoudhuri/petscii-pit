# PETSCII PIT DEMO — Roadmap

## Continued Navigation Tuning
- The AI's movement is still a greedy, distance-based heuristic, not
  true pathfinding — it's been through two rounds of anti-oscillation
  fixes (last-move-reversal avoidance, a short position-memory buffer,
  nearest-target selection, and a stuck-timeout that blacklists a
  difficult room and retargets), but genuine pathfinding was
  deliberately avoided as too heavy for BASIC V2 to compute every turn.
- Given that, further edge cases in navigation (getting stuck, taking
  an inefficient route, missing something reachable) are plausible and
  worth watching for during continued use, rather than assuming the
  current fixes are the final word. If new stuck patterns show up,
  the fix is more likely to be a targeted addition to the existing
  heuristic (as with the last two rounds) than a full pathfinding
  rewrite, unless the heuristic approach is found to have a hard
  ceiling.

## Main-Game Engine Sync — IMPLEMENTED
- One item from the main game's roadmap did get carried over: the fast
  font-copy, integer-array, and safer array-null work, plus the full
  set of custom monster/dungeon glyphs (potion, treasure/coin, Golem on
  its own dedicated slot, Leech, Goblin, Guard, Imp, Cultist, stairs),
  and the fix for monsters not drawing while still in the dark. Applied
  carefully rather than copy-pasted, since the demo's fog-of-war tracking
  diverges from the main game (direct memory PEEK/POKE instead of a
  third BASIC array) — that difference was preserved as-is, not forced
  to match.
- Walls (`#`) are the one glyph still on the stock ROM shape in both
  programs — matches the main game's own roadmap status, not a demo-
  specific gap.
- Also fixed a display bug specific to the demo: the instructions
  screen was scrolling one line too far, cutting off its first line.

## Main-Game Engine Sync: Music, Speed-ups, Fixes, Glyphs — IMPLEMENTED
- Background music ("Dungeoneering") and fight music ("Assailing"),
  with the same fight trigger and resume-where-it-left-off behavior as
  the main game. M toggles music, E toggles sound effects.
- Faster level generation, including clearing the demo's raw-memory
  fog-of-war map with the same machine-code helper.
- Doorway disappearing fix, full recolor when the eyes adjust, and the
  keyboard buffer cleared after a kill.
- Redrawn treasure chest, Golem, Goblin, and Imp glyphs, matching the
  main game.

## Level Loading Progress Bar — IMPLEMENTED
- Same as the main game's roadmap: when descending to a new level, draw
  a progress bar under the "DESCENDING TO LEVEL..." text while the
  level is generated.
- The bar is made of `.` characters, shaded from lightest to darkest:
  white, then the C64's three greys (light grey, medium grey, dark grey).
- Built the same way as the main game: three dots after "PLEASE WAIT ..."
  cycling left to right through the four shades while the level is built.

## Main-Game Engine Sync: PAL/NTSC, Music Timing, HUD — IMPLEMENTED
- PAL/NTSC detection loads `musicpal` or `musicntsc`.
- Music starts while the first level is built, pauses when a level is
  ready, while resting, and after a fight, and continues on the next move.
- HUD shows HP as current/max.
- Instructions screen shows the machine type: "PAL - PRESS ANY KEY TO
  CONTINUE" or "NTSC - PRESS ANY KEY TO CONTINUE".

## Main-Game Engine Sync: "Lamenting" Mood Music — IMPLEMENTED
- Same mood rules as the main game: Lamenting before Alley Rat or below a
  quarter of max HP, Dungeoneering otherwise, each continuing where it
  left off. Music player now at $9700.

## AI Misses Doors — TO DO
- On closer watching, the AI doesn't seem to find any doors at all, on
  any side of a room (first noticed as missing doors on the left side).

## Main-Game Engine Sync: Optimization Pass — IMPLEMENTED
- Glyph setup as DATA/READ instead of 88 POKEs.
- Room, monster and AI-trail tables are integer arrays.
- Fewer IFs: tile drawing by `ON ... GOTO`, monster and weapon stats from
  DATA tables, Keen Eyes through one reveal routine, title tier as one
  expression, and the AI's move choice returning as soon as a move is
  picked.
- HUD and message line each built as one string and printed with one
  PRINT, only when they change.
- Hot routines moved to the top and the whole program renumbered in
  steps of 10, the same as the main game. The AI move choice now sits
  right after the main loop (old 5870-6820, now 2530-3480). Audited
  line for line against the previous listing.

## Bug: AI Trail Shares `VY` With the Wall Reveal — TO DO
- `VY` is one of the AI's six remembered steps (2530, 3070) and is also
  set to `INT(IX/40)` by the corridor-wall reveal (200). Each wall reveal
  overwrites one remembered step with a row number, so the AI can
  backtrack more than intended. Fix: rename one of them.

## Main-Game Engine Sync: Ambush Message, Ambush Fight Music
- Ambush message now reads "A MONSTER AMBUSHED YOU!" (line 4670).
- Same open bug as the main game: no fight music after an ambush while
  resting (see the main roadmap). Not fixed yet.

## Resting Dots — NOT FOR THE DEMO
- The main game plans to show "RESTING ..." with cycling dots during its
  4-second rest wait. Not applied here: the demo's rest wait is only 1
  second.

## Everything Else
- No other outstanding feature requests for the demo specifically at
  this time — it currently does what it was built for (explore, fight,
  loot, and restart on death, unattended, at a faster pace than normal
  play). Anything else from the main game's roadmap (difficulty
  balance, new mechanics, etc.) would need a matching decision about
  whether it should also apply to this program, or stay exclusive to
  the demo's simpler, non-interactive purpose, if and when those items
  get built.

## Main-Game Engine Sync: Second SID — IMPLEMENTED
- Same second-SID music support as the main game (POKE 56,150).
- Same instructions-screen "2SID" note and the same volume keys as the
  main game: V on one SID; separate M (music) and E (effects) volume
  cycles on two SIDs. Lines: V check on 1760, M/E on 1770/1780, music
  starts on 6750 before the instructions, VL/VM/VF set on 6810, new
  routines at 7010-7040.
