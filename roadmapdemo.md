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

## Everything Else
- No other outstanding feature requests for the demo specifically at
  this time — it currently does what it was built for (explore, fight,
  loot, and restart on death, unattended, at a faster pace than normal
  play). Anything else from the main game's roadmap (difficulty
  balance, new mechanics, etc.) would need a matching decision about
  whether it should also apply to this program, or stay exclusive to
  the demo's simpler, non-interactive purpose, if and when those items
  get built.
