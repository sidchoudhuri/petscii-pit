# PETSCII PIT DEMO — Dev Log

A separate, standalone program (`petsciipitdemo`) built specifically for
unattended recording — the character explores, fights, and loots on its
own with no player input. Built on top of the same, unmodified game
engine as the real game; only the input source and a few pacing/flow
details differ.

## Initial Build
- Started from a full copy of the real game's engine (dungeon
  generation, combat, rendering, weapons, room names — all unchanged).
- Replaced the single point where the game reads a keypress with an AI
  decision routine. Everything downstream (movement, combat resolution,
  pickups, messages) is identical to the real game and doesn't know or
  care that the "keypress" came from logic instead of a person.
- AI priority order each turn: attack any adjacent monster; rest if hurt
  and safe; otherwise move toward the nearest room you haven't revealed
  yet, or the stairs once every room has been revealed.
- Death now auto-restarts (stats reset, fresh level generated) instead
  of showing the K/N/Q prompt and waiting for a keypress — the demo
  runs indefinitely.
- Pacing sped up across the board: the rest pause dropped from 4
  seconds to 1, the stairs-found pause from 2 seconds to 0.5, and the
  title-announcement pause similarly — short enough to still read on
  camera, not long enough to drag.
- Finding a second weapon no longer interrupts with a full-screen
  Y/N prompt — the AI automatically keeps whichever weapon has the
  higher attack bonus and shows a one-line message instead, so it never
  needs to clear or redraw the dungeon for this.

## Item-Seeking Fix
- The AI wasn't detouring for potions or treasure sitting elsewhere in
  a room it was already walking through — it only ever targeted room
  centers, with zero awareness of item locations.
- Fixed: before continuing toward its exploration target, the AI now
  checks whether the room it's currently standing in has a known,
  uncollected potion or treasure, and grabs it first if so.
- Later extended to also cover weapons, which weren't part of the
  original fix (see below).

## Anti-Oscillation Fix (first pass)
- Found and fixed a real bug where the AI would bounce back and forth
  between two tiles indefinitely, right from the start of a level. The
  greedy movement logic had no memory of which direction it had just
  moved, so if a room's actual exit wasn't in the straight-line
  direction toward the target, it would walk into a wall, take the only
  safe step backward, and then immediately try the same wall again the
  next turn — a stable infinite loop.
- Fixed by tracking the last move direction and excluding an immediate
  reversal of it, with a fallback that still allows reversing if truly
  boxed in on every other side (so it can back out of genuine dead
  ends rather than freezing).
- Verified with actual Python simulations of the exact decision logic
  before shipping, including a deliberately adversarial loop-shaped
  obstacle, not just reasoning about it.

## Real Crash Found and Fixed: Reserved-Word Variable Collision
- A variable named `IF9` caused a real syntax-error crash on real
  hardware. The C64 BASIC tokenizer only looks at the first two
  characters of a variable name — `IF9` and the reserved `IF` keyword
  are literally the same thing to it, so the line was being
  mis-tokenized as the `IF` keyword followed by a stray, meaningless
  character. Renamed to `FD`.
- This is the same underlying class of bug as an earlier one found in
  the main game (`FN$` colliding with the `FN` keyword).
- Importantly, the verification method used to check for this class of
  bug had a real gap: it only ever considered 1-2 character candidate
  names, so a 3-character variable like `IF9` was never even tested.
  The check has since been rebuilt to strip out string literals,
  comments, and label references, extract every real variable and
  array name regardless of length, and empirically confirm each one's
  actual tokenized bytes rather than just comparing names against each
  other. Both this program and the main game now pass that corrected,
  more thorough check with zero real collisions.

## Anti-Oscillation Fix (second pass) + Smarter Targeting
- The first anti-oscillation fix only prevented small, 2-cell bounces —
  larger loops (a wider cycle around an obstacle) could still trap it,
  and because the AI only ever re-evaluated its target once it exactly
  reached it, getting stuck on one hard-to-reach room meant it would
  never notice an easier, closer unexplored exit sitting right next to
  it along the way.
- Target selection is no longer arbitrary: the AI now picks the
  *nearest* unexplored room by simple distance, rather than whichever
  one happened to be found last in a loop.
- The stuck-timeout dropped from 40 turns to 15, and — the actual fix
  for ignoring nearby exits — hitting that timeout now blacklists the
  room it was struggling to reach and forces a genuine new target pick
  next turn, rather than just taking one random step and returning to
  the same difficult target. The blacklist isn't permanent — it only
  remembers the single most recent failure, so a room becomes
  available again as soon as something else fails instead, and it
  resets fresh every new level.
- The short-term movement-memory buffer grew from 4 recent positions to
  6, as a smaller, complementary defense against loops slightly larger
  than the original buffer could catch.
- Verified again with Python simulations, plus the corrected full
  variable-safety sweep, before shipping.

## Weapon-Seeking Added
- The item-seeking fix above only ever checked for potions and
  treasure, since that's what was originally reported — weapons use a
  different tile range and were never included. The AI would only pick
  one up by coincidence, if it happened to sit directly on the path
  toward wherever it was already headed; otherwise it walked past
  without detouring, which could look like active avoidance from the
  outside even though nothing was specifically steering away from it.
- Fixed by extending the same current-room item check to also include
  weapon tiles, with the same priority as potions and treasure.

## Engine Sync: Performance, Memory, and Art Carried Over From the Main Game
- Brought the demo up to date with a batch of under-the-hood work done on
  the real game, applied carefully rather than copy-pasted wholesale,
  since the demo's engine has diverged slightly from the main game in a
  couple of places (see below).
- The font now loads with a single fast block-copy instruction instead
  of a byte-by-byte loop, same as the main game.
- The dungeon-tracking arrays switched to a more memory-efficient number
  type, and the risky array-clearing trick the demo was also using
  between levels was replaced with a safer plain loop — both matching
  the main game's fix. Note: unlike the main game, the demo doesn't keep
  a third tracking array for fog-of-war; it already stores that
  information directly in memory instead of a BASIC array, so there was
  nothing to convert there.
- Fixed the same real bug the main game had: monsters (and in the
  demo's case, two separate reveal routines) could fail to actually
  draw on screen while still in the dark, before the AI "learns" Keen
  Eyes — fog-of-war itself was working, the monster just never got
  POKEd to the screen.
- Added the same hand-drawn custom glyphs as the main game for: potions,
  treasure/coins, the Golem (now on its own dedicated character slot
  instead of sharing one with a generic solid block), the Leech,
  Goblin, Guard, Imp, Cultist, and the stairs down.

## Instructions Screen Overflow Fix
- The instructions screen was scrolling one line too far and cutting
  off its first line. A stray blank-line `PRINT` ahead of the "find the
  stairs" line was pushing the whole screen past where it needed to be
  — removed.

## Music: "Dungeoneering"
- The demo now has the same background music as the main game:
  "Dungeoneering", an original 3-voice SID tune (drums, bouncing octave
  bass, lead melody and arpeggio). It loads from disk automatically at
  startup, so launching is still just LOAD"PETSCIIPITDEMO",8 and RUN.
- It starts once the first level has been built and runs on its own
  raster interrupt, so it keeps a steady tempo while the AI plays
  without changing any of the demo's pacing.
- Mixed quietly so sound effects stay easy to hear. Sound effects
  borrow the music's first voice and hand it back afterwards.
- M toggles the music and E toggles sound effects, same as the main
  game. The instructions screen lists both.

## Faster Level Generation
- Same speed-ups as the main game: clearing the dungeon arrays between
  levels is now done by a tiny machine-code helper bundled with the
  music instead of a BASIC loop. Unlike the main game, the demo also
  clears its fog-of-war memory this way, since it keeps fog-of-war in
  raw memory rather than a BASIC array.
- Corridor walls are placed while the corridors are dug, and treasure
  rooms/apothecaries are recorded as their contents are placed, instead
  of separate full-map scans afterwards.
- Same dungeons as before, just built faster: the shortcuts were
  checked against 5,000 sample dungeons and matched the old generator
  every time.

## Fight Music: "Assailing"
- Same as the main game: the music was reorganized into reusable
  patterns so two songs fit in less memory than one used to, and a
  short, scary fight theme, "Assailing", was added.
- It plays whenever a living monster is in the room with the character
  or the character is fighting one, kicking in as the room is entered
  or the first swing lands, before the monster acts.
- When the monster dies or the character leaves the room,
  "Dungeoneering" picks up exactly where it left off, and a new level
  always brings the dungeon music back.

## Engine Sync: Bug Fixes From the Main Game
- Fixed the character vanishing while fighting from a doorway: attacking
  into a room that hadn't been revealed yet redrew the whole room,
  including the doorway the character was standing in, and it stayed
  invisible until its next move.
- When the character's eyes adjust at Alley Rat, everything already
  revealed now lights up to its proper color (potions, treasure,
  stairs, weapons, monsters, and the character itself), not just the
  walls.
- The keyboard buffer is now cleared when a kill finishes, matching the
  main game.

## Redrawn Characters: Chest, Golem, Goblin, Imp
- Same new designs as the main game for the treasure chest, Golem,
  Goblin, and Imp, so both programs keep matching character sets.

## Engine Sync: PAL/NTSC, Music Timing, Loading Animation, HUD
- Same as the main game: PAL/NTSC detection picks the matching music,
  and the instructions screen shows the machine type.
- HP on the HUD shows current and max health.
- Music starts while the first level is built, waits silently once a
  level is ready, while resting, and after a fight, and comes back as
  the character moves on.
- The "PLEASE WAIT ..." dots animate through white and the greys, left
  to right, while each level is built, and the startup message appears
  while the music is still loading.

## Engine Sync: "Lamenting" and Music Moods
- Same as the main game: Lamenting plays while it's still dark (before
  Alley Rat) and when the character is near death (HP below a quarter of
  max), and Dungeoneering the rest of the time, each picking up where it
  left off.

## Engine Sync: Glyph Setup as DATA
- Same as the main game: the 11 custom glyphs are now one DATA line each
  (screen code, 8 bitmap bytes, name in a REM) written by a short READ
  loop instead of 88 POKEs. Same glyphs, smaller listing.
