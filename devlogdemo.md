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
