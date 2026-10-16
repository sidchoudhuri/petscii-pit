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

## AI Misses Doors — IMPLEMENTED (the AI now reads the level layout)
- On closer watching, the AI didn't find doors at all, on any side of a
  room. It walked straight at the centre of the room it wanted and only
  knew the four squares next to it, so a corridor that started off in
  the wrong direction, or a door on the far side, left it pacing.
- The demo now cheats: while the level build carves each corridor it
  records the corridor's squares (PP%, about 200 at most), which rooms
  it joins and the door square at each end (AJ%(room,room) = position
  of that room's door in PP%). Lines 5320 (reset), 5690, 5710-5720,
  5770-5780; AJ% is cleared with the other map arrays (POKE 780,3).
- The AI routes through rooms: in a room that isn't its target it finds
  the next room to go through (a search over the 5-7 rooms, only when
  the room or target changes, 7010-7060), walks to that door (7070-
  7090), then follows the recorded corridor square by square to the
  next room's door and steps in (7100-7130). Off the recorded path it
  heads for that door. Monsters, items, resting and the "stuck for 15
  moves" fallback are unchanged. Hooks: 2640 (FM=0), 2680, 2700.
- Tested in a Python model of the demo's level build and AI (no
  monsters or items), 2000 levels: the old AI reached the stairs in
  1775, the new one in 1978, in fewer moves on average (105 -> 96).
- Cost: under a second more per level build; corridor moves are a
  little cheaper than before; about 1 KB more memory.

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

## Bug: AI Trail Shares `VY` With the Wall Reveal — FIXED
- `VY` is one of the AI's six remembered steps (2530, 3070) and is also
  set to `INT(IX/40)` by the corridor-wall reveal (200). Each wall reveal
  overwrites one remembered step with a row number, so the AI can
  backtrack more than intended. Fix: rename one of them.
- Fixed: the corridor-wall reveal (200-240) now uses `VQ`, so the AI's
  remembered steps are no longer overwritten.

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
- Same instructions-screen "2SID" note as the main game. The music starts
  on line 6750, before the instructions. No volume keys (the demo
  doesn't read the keyboard while it plays); fixed volumes instead: two
  SIDs = music 3, sound effects 15; one SID = 9. Set once on line 6750.
  Old lines 6800 (SID volume 15 and voice-1 envelope) and 6810 (music
  start) are removed: the player's start sets the volume and clears the
  SID, and every sound effect sets voice 1's envelope through SYS 38668.

## Main-Game Engine Sync: Scaling, Groups, Levels, Weapons, Holes — IMPLEMENTED
- Same as the main game: monster HP/attack scaling, hit-back tied to the
  monster's attack, monster groups from level 3 ("ANOTHER GOBLIN!"),
  growing character levels (25 x N x (N+1) XP, +5 x level max HP),
  Shadow Hand at 750 XP, random weapon attack rolls, and hidden holes
  from level 5 with the Keen Eyes spotting roll and the fall.
- The AI walks around a hole it has spotted (treated like a wall in its
  move checks, 2980-3010), but falls in like a player if it didn't spot
  it. Demo lines: groups 2150-2200 and 7140, hole drawing 7150, fall
  7160-7190 (from 2330), placement 7200-7230 (from 6090), spotting
  7240-7250 (from the room reveal at 1410).

## Main-Game Engine Sync: Version Number and Two-SID Key Line — IMPLEMENTED
- Top line of the instructions screen shows the version (3850), and the
  key line gets the "VOLUME" prefix with two SIDs (3900).

## Main-Game Engine Sync: Animated Characters — IMPLEMENTED (V13)
- Same frames and rules as the game (glyph DATA 6430-6530, 20 glyphs at
  6410; monster frame flips at 1230, 1260, 2080; player walk frames at
  2370, fight frame at 2080, standing again when resting (3490) and on
  each new level (5320)).

## Demo Speed-up — IMPLEMENTED (V14)
- Goal: the demo as fast as possible, with exactly the same AI decisions.
  The demo was much slower than the game because the AI's thinking runs
  in BASIC before every step.
- Removed the forced memory clean-up every 25 steps (old line 1750,
  FR=FRE(0)). BASIC still cleans up strings by itself when it needs to,
  far less often, at the same cost per clean-up.
- The item scan (all squares of the current room, every step) is now
  remembered per room: it only rescans when the AI enters a room, after
  the remembered item is picked up, or when a monster drops a weapon
  (IQ = room that was scanned, reset each level).
- The "don't walk back" check compared each of the 4 neighbours with the
  last 6 positions in a loop of 24 IFs; it is now 4 single expressions,
  e.g. OW=OW AND QW<>VZ AND QW<>VY ... (no array, no extra memory; V%
  removed).
- The route-following lines (old 7010-7130) moved next to the AI so the
  jump to them is short, and the whole demo was renumbered in steps of
  10 again. Every GOTO/GOSUB/THEN/ON target was remapped and checked.
- Where things are now (old -> new): main loop 1760 -> 1750; AI 2530 ->
  2520; item scan 2720 -> 2710; move choice 2960 -> 2950; neighbour
  checks 3070-3130 -> 3060-3090; route search 7010-7060 -> 3450-3500;
  route entry 7070 -> 3510; corridor follow 7100-7130 -> 3540-3570;
  rest 3490 -> 3580; instructions 3850 -> 3940; level build 5290 ->
  5380; corridor recording 5710-5780 -> 5800-5870; glyph DATA 6430-6530
  -> 6520-6620; group kill 7140 -> 7080; hole drawing 7150 -> 7090;
  fall 7160-7190 -> 7100-7130; hole placement 7200-7230 -> 7140-7170;
  hole spotting 7240-7250 -> 7180-7190.

## Loader — IMPLEMENTED (V15)
- The demo now starts from the loader's menu (D) and goes straight to
  level 1; pressing Q returns to the menu (checked once per step on
  line 1730 with GET K$ and PEEK(197)=62, so taps and held keys both
  work; the music is stopped first). Its music loading, font and glyph setup and
  instruction text are gone (the I routine at 3930 shows the loader's
  stored screen). About 2.3 KB of BASIC memory won back.
- Renumbered in steps of 10 again. Main places now: main loop 1730-1740,
  AI 2510, item scan 2700, move choice 2940, route search 3440, route
  entry 3500, corridor follow 3530, rest 3570, level build 5130,
  startup 6110, groups 6530, hole drawing 6540, fall 6550, hole
  placement 6590, hole spotting 6630 (after V18's startup change).

## Battle Screen — IMPLEMENTED (V19)
- Same battle screen as the game (see roadmap.md): big player and
  monster, HUD, HP bars, group count, lunges with damage numbers. No hint
  line, and the AI never flees.
- In a battle the AI's move is always turned into an attack on the
  monster on screen (6850), so it can't switch to a second monster that
  is also next to it.
- Lines: enter 6650-6670, bars and group line 6680-6710, glyph and colour
  6720-6730, big glyph 6740, player lunge 6750, monster lunge 6760-6790,
  monster attack hook 6800-6820, kill 6830, exit 6840, attack direction
  6850. Hooks: 390, 1210, 1730 (quitting resets the screen first), 1860,
  2000, 2060, 2110, 2140, 3790 (death leaves the battle first), 6530.
- V19: on the disk the demo is DEMO; quitting (1730) loads PETSCIIPIT.
