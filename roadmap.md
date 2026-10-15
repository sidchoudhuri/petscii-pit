# PETSCII Pit — Game Plan / Roadmap

Features and mechanics for the game. Implemented items are listed first,
in the order they were completed, as a record of what's shipped. Everything
after that is still just a planning reference for when we're ready to build
each piece.

## Monster Variety — IMPLEMENTED
- 6 monster types, all sharing the same chase/bump-attack behavior as
  before, differing in glyph, color, and difficulty (HP/damage bonus
  stacked on top of the existing per-level scaling):
  - Leech (green) — baseline difficulty
  - Goblin (yellow)
  - Imp (orange)
  - Guard (light red)
  - Cultist (red)
  - Golem (purple) — toughest
- Spawns are depth-weighted rather than uniform: early levels (1-3) only
  spawn Leech and Goblin, with tougher types unlocking gradually until
  the full roster is available by level 16.
- XP and coin rewards scale by type (Leech still gives the original
  10XP/1-5GP; Golem gives up to 22XP/11GP).
- Combat messages name the monster type you fought, e.g.
  `KILLED CULTIST +18XP +9GP -TOOK 5DMG`.
- Each type has its own hit/death sound pitch.
- Still to come later: monster types with genuinely different behavior
  (e.g. a stationary wall-mimic, a ranged elemental) — these need their
  own AI branching rather than sharing `@MONSTERSTEP`, and were
  deliberately deferred as a separate, larger piece of work.
- New follow-up request: double the roster to 12 types total. Motivation
  is that the game gets boring past level 10 — with only 6 types (and
  the full roster already available by level 16 today), there's no more
  new variety left to encounter for a large stretch of play. The new
  types need the same treatment as the existing 6: their own glyph,
  color, HP/damage bonus scaling, XP/coin reward tier, and hit/death
  sound pitch.
- Open question this raises: the current depth-weighted unlock schedule
  reaches the full 6-type roster by level 16 — with double the types,
  that schedule likely needs to extend further or be redistributed,
  otherwise the "boring past level 10" problem just resurfaces once the
  now-larger roster is still fully unlocked too early. Not yet decided.
- This is separate from the "different behavior" item above — this is
  about more types sharing the existing chase/bump-attack behavior,
  not new AI patterns.

## Weapon Pickups — IMPLEMENTED
- Starting at dungeon level 2, and only once the player has reached Alley
  Rat, monster kills have a 20% chance to drop a weapon on the tile
  where the monster died (raised from an initial 8% to shorten the wait
  for a first weapon).
- 5 weapon types (Dagger, Sword, Blade, Mace, Flail), each with its own
  glyph, color, attack bonus, and one extra effect (dodge chance, bonus
  sneak-attack damage, or reduced counter-damage).
- One weapon equipped at a time. Picking up a new one while unarmed
  auto-equips it; picking one up while already armed shows a full
  comparison screen and asks whether to take it — declining leaves the
  new weapon on the floor to come back for later.
- Shown on the character sheet: name, attack bonus, and effect.

## Room Names — IMPLEMENTED
- Certain rooms get a name, displayed bottom-left (mirroring the
  existing title badge's position, drawn together as one combined line
  that only redraws when the text actually changes, not every turn).
- Normal (empty, or not covered by a rule below) rooms have no name.
- The first room you land in — at the start of the game, or arriving
  from the previous level — is named "LEVEL X ENTRYWAY" (X = current
  dungeon level). The last room is named "STAIRS TO LEVEL X" (X = the
  level you're about to descend to). If a level ever has so few rooms
  that the first and last room are the same one, STAIRS TO LEVEL X
  takes priority over ENTRYWAY — though every level always generates
  at least 5 rooms today, so this case can't currently occur.
- Every middle room always contains exactly one monster by generation
  design, so its name always includes that monster: a room that also
  has treasure is "[MONSTER] TREASURY" (treasure takes priority even if
  potions are also present); a room with only potions and no treasure
  is "[MONSTER] APOTHECARY"; otherwise it's just "[MONSTER] ROOM".
- Once that room's monster is defeated, its name gains a "(CLEARED)"
  suffix. There is no separate "looted" state — clearing the monster is
  the only status the name reflects.

## Grand Hallway — IMPLEMENTED
- Corrected understanding from the original Room Names entry: this is
  not about generating a deliberately wide corridor. Dungeon generation
  already occasionally produces two separate, genuinely 1-cell-wide
  corridors that happen to run parallel and land directly adjacent to
  each other, purely by coincidence of room placement — nothing needed
  to change about corridor generation itself.
- While standing in a corridor cell, if there's a genuinely separate
  corridor running parallel and directly adjacent to it, the bottom-left
  name shows "GRAND HALLWAY".
- Detection is based purely on the surrounding cell layout, not which
  direction you're currently moving. It specifically excludes a plain
  corridor bend (only one side continues, so it's a turn, not a second
  corridor), a genuine 4-way crossing where two corridors intersect at
  a single point, and a T-junction (a different corridor's dead end
  touching a straight run at one point) — none of these are a real
  "two hallways running side by side," which is the only case that
  should count.

## Confirm Before Descending Stairs — IMPLEMENTED
- Stepping onto the stairs tile no longer triggers instant descent.
  Instead it asks "DESCEND TO LEVEL X?" on the message line. Y
  overwrites that same line with "DESCENDING TO LEVEL X" and the new
  level generates; any other key leaves the message and returns to
  normal play — no screen clearing either way.
- Resolved (previously open) questions: declining leaves you standing
  on the stairs tile normally, free to walk off; stepping onto it again
  later re-asks every time rather than remembering a prior decline.
- The level transition itself still does a full screen clear, but the
  HUD is shown immediately afterward alongside the transition message,
  rather than the message appearing alone on an otherwise blank screen.

## Avoid Full Dungeon Redraws Where Possible — IMPLEMENTED
- General goal: several interactions used to clear the whole screen and
  redraw the entire dungeon afterward when they didn't need to. Fixed
  across quit, death, stairs (see above), and weapon discovery below.
- Core change enabling this: the single message line below the HUD
  expanded to two lines. The only two things that still clear the
  whole screen are pressing I (instructions) and C (character sheet).
  Row 2, which previously existed purely as visual breathing room
  between the message line and the dungeon, is now used for real text,
  so that gap is gone and message text sits right against the top wall
  of whatever room the player is in.
- Weapon discovery is redesigned around these two lines, replacing both
  the old silent auto-equip-when-unarmed behavior and the old
  full-screen comparison-when-armed behavior with one unified flow:
  - Every time a weapon is found, regardless of whether one is already
    held, line 1 shows "FOUND [weapon name] KEEP IT? Y/N".
  - If the player is currently unarmed, this message just stays as-is
    and waits for a keypress — Y equips it, any other key leaves it.
  - If the player already has a weapon equipped, it alternates back
    and forth between the "FOUND... KEEP IT?" message and a two-line
    "EQP: [current weapon description]" / "NEW: [new weapon
    description]" comparison, on a 2-second cycle, repeating
    continuously until the player responds — Y swaps to the new
    weapon, any other key leaves the current one equipped, whichever
    point in the cycle they respond at. The 2-second timer checks for a
    keypress continuously rather than blocking, so responding
    immediately doesn't wait out the clock. This replaced an earlier,
    simpler one-time version that showed the message once, paused, then
    showed the comparison a single time and waited silently — that
    version shipped first and worked, but was then superseded by this
    alternating version once requested.
  - This was a real behavior change from the original game, not just a
    visual one: previously your very first weapon auto-equipped with
    no prompt at all. Now every weapon discovery asks first.
- Quit confirmation (pressing Q during gameplay) no longer does a
  full-screen "QUIT GAME?" clear-and-redraw — the HUD stays up and
  line 1 shows "QUIT GAME? Y/N". Y exits the game entirely; any other
  key clears the message and returns to play, with no redraw needed
  either way.
- Death screen is redesigned for visual consistency with level
  transitions, rather than being a bare full-screen takeover: the
  screen still clears, but the HUD is shown immediately afterward
  (same pattern as descending to a new level), with the existing
  "GAME OVER - YOU REACHED LEVEL X", "FINAL XP", and K/N/Q options
  displayed below it exactly as before — this one keeps its full clear
  since its content doesn't fit cleanly into just two lines, but
  keeping the HUD visible makes it feel consistent with everything else
  instead of a jarring, disconnected screen. Death now also plays a new
  sound: three sad notes in descending order.
- See also "Remaining Backward-GOSUB Speed Fixes" below, now also
  implemented — it was the complementary half of this same effort: this
  section was about not drawing things unnecessarily; that one was
  about making the drawing that's genuinely required (a new level
  actually needs to render) faster to execute.

## Remaining Backward-GOSUB Speed Fixes — IMPLEMENTED
- Background: on the C64, a GOSUB/GOTO to a line number less than or
  equal to the current line forces BASIC to search for that target
  starting from the very beginning of the program, rather than
  searching nearby — a well-documented quirk that gets worse as a
  program grows. `@DRAWTILE`, `@WTYPE`, `@MSGDRAW`, and the whole
  `@HUDDRAW`/`@PUTSTR`/`@CLREOL`/`@TITLEDRAW`/`@ROOMNAME`/`@CHKHALL`/
  `@CHKHALLV`/`@CHKCLEAR` chain have all been moved later in the file
  to fix this (done, verified, shipped).
- `@MAINLOOP` itself couldn't be relocated the same way (its body
  flows via fall-through into most of the game's turn logic), so its
  many scattered re-entry points are instead redirected through a
  tiny early "skip" label instead. An initial hardware test of this
  appeared to fail, but that turned out to be a mistake in the test
  itself, not a real bug — confirmed done, verified, shipped.
- Ran a fresh, comprehensive sweep (covering GOSUB, GOTO, and implicit
  THEN targets, not just GOSUB) rather than trusting the older, vaguer
  note this entry used to have, since a lot of code had changed since
  it was written. Found that `@WAITKEY` had three backward callers, all
  from features that fire frequently — stairs confirmation on every
  level transition, the quit prompt, and first-weapon pickup — making
  it the clear highest-impact remaining case. It was self-contained
  (called nothing else), so it moved to the end of the file the same
  way as the earlier fixes; confirmed via the same sweep that all of
  its callers are now forward. Done, verified, shipped.
- Everything else the fresh sweep turned up is low-impact and was
  deliberately left alone: `@MONSTERSTEP`'s one backward caller turned
  out to be from `@REST` specifically, not its far more frequent
  every-combat-turn caller (which was already forward); `@GOWAIT`'s
  backward self-loop only fires on an invalid keypress during the death
  screen; and the remaining handful are all generation-time-only code
  (room and corridor carving) or per-event sound effects, none of which
  run anywhere near often enough to be worth the added risk right now.

## Softer Death, Starting at Level 5 — IMPLEMENTED
- Dying while at dungeon level 5 or deeper, and having reached at least
  the Alley Rat title (XP 50+), unlocks a new option on the death
  screen: press S to resume one level below where you died (die on
  level 5, resume on level 4), keeping both your current XP and your
  weapon. This is a new, separate option (K and N behave exactly as
  they did before, regardless of depth or title).
- The option is always visible on the death screen, every time, never
  absent. It's only active (shown in normal white/grey, selectable)
  when both requirements are met at once — level 5+ and Alley Rat.
  Missing either one — not deep enough, not experienced enough, or
  both — shows the same greyed-out version (shown in the darkest
  available grey rather than the normal white/grey used for K, N, and
  Q), so every player is reminded the feature exists regardless of how
  close they are to it. Revised from an earlier version of this idea,
  which hid the option entirely for a player who hadn't reached Alley
  Rat yet — now it's always shown, just greyed out until both
  conditions are met. Pressing S while greyed out does nothing, same as
  any other unrecognized key on this screen.
- Exact wording, identical whether active or greyed out (only the color
  changes): "S - RESUME WITH XP + WEAPON (LEVEL 5+)" — this is a fixed,
  generic reminder of the requirement rather than dynamically showing
  which level you'd actually resume at.

## Healing & Ambush Rebalance — IMPLEMENTED
- Discovered while investigating Combat Difficulty / Balance above:
  player max HP grows completely uncapped (+5 for every 50 XP earned,
  forever), and the old level-transition heal (33-50% of max HP, random)
  scaled directly off of that ever-growing number. Simulating an actual
  playthrough showed the compounding effect clearly — HP remaining
  after a level's worth of combat climbed steadily from near-zero
  around level 5 to 85+ by level 25, meaning the game was getting safer
  over time instead of more dangerous, independent of any weapon or
  monster-scaling issues.
- Level-transition healing changed from 33-50% of max HP (random) to a
  flat 10% of max HP, every time.
- Rest and potion healing (previously a flat 3-5 HP each, which had
  become trivial against a large, uncapped max HP pool) now share a
  tiered formula: still flat 3-5 HP while max HP is under 30, then a
  random 10-20% of max HP once past that threshold.
- Resting is capped at 3 uses per level before risk kicks in. The base
  ambush chance during rest also increased, from LV*0.75 (capped at
  15%) to LV*1.5 (capped at 25%).
- Every rest beyond the 3rd per level now shows a warning — "RESTING
  AGAIN IS RISKY! REST ANYWAY? Y/N" — and requires confirmation, with
  ambush chance escalating steeply beyond that point (+35 percentage
  points per additional rest, capped at 90%), replacing an earlier,
  simpler version of this idea that just hard-blocked a 4th rest
  outright.
- Shadow Hand's ambush immunity changed from true immunity to a flat
  3-5% chance instead — meaningfully safer than earlier titles, but no
  longer risk-free. The character screen description was updated to
  match ("RARELY AMBUSHED" instead of "IMMUNE TO AMBUSHES"). Fixing
  this surfaced a real bug: the ambush check had a separate `XP<600`
  gate that was the actual mechanism behind the old immunity — just
  changing the percentage without removing that gate would have left
  Shadow Hand silently immune regardless of the new number.

## Split Keen Eyes Into Two Levels — IMPLEMENTED
- Keen Eyes is now two separate, named tiers instead of one skill
  granted all at once.
  - "Keen Eyes (1)" — granted at Alley Rat (XP 50, as before) — just
    the base 6-square ring around you, no forward extension.
  - "Keen Eyes (2)" — granted at Basic Burglar (XP 150), alongside that
    title's existing Nimble Fingers skill, not replacing it — adds
    seeing 2 tiles ahead in your direction of travel instead of 1,
    while keeping the same 6-square ring from tier 1.
- Character screen updated to list both as separate, named skills.
- New follow-up idea, not yet built: a further perk specifically for
  Keen Eyes (2) (Basic Burglar) — individual room types show as
  different colors once revealed, rather than the single uniform
  light grey rooms currently get once Alley Rat is reached:
  - Treasure room: yellow
  - Apothecary: green
  - Monster room (no special trait): light red while its monster is
    still alive, changing to red once that monster is defeated
  - Stairs room and entryway: light blue
- Open questions for when we build this: does this recolor just the
  room's walls, or the floor too (floor currently stays permanently
  dark grey regardless of title, by earlier explicit decision, so this
  would need to be a deliberate exception for that case). Corridors
  are unaffected either
  way, since room type is a property of rooms, not corridors.

## Corridor Wall Decoration — IMPLEMENTED
- Corridors now have actual wall tiles flanking them instead of blank
  void, via a generation-time pass: after corridors are carved, every
  corridor cell's void neighbors (orthogonal and diagonal) become
  walls. Checking diagonals too was an addition beyond the original
  plan — without it, L-shaped bends left a gap at the outer corner,
  since the corner cell is only ever diagonally adjacent to the turn
  point, never a direct neighbor of any corridor cell.
- Found and fixed a real bug during this: walls were being placed
  correctly in the data, but the game's existing reveal logic only
  ever marks the single cell the player is standing on as "seen" —
  neighboring wall cells never got their own turn to be revealed or
  drawn, so they existed but stayed invisible. Fixed by adding wall
  reveals to both the normal per-step reveal and Keen Eyes' wider
  extended-vision reveal (16 separate reveal points there needed the
  same fix).
- Caught and fixed a bounds-checking bug in that same fix before it
  shipped: the first version could have read past the map array's
  bounds for a corridor cell sitting at the map's bottom or side edge,
  which would have thrown a real BAD SUBSCRIPT ERROR on hardware.
- Room walls and corridor walls are now visually distinct once earned,
  which required giving corridor walls their own separate tile value
  (rather than sharing the room-wall value) and updating every
  existing wall-blocking check (player movement, monster movement) to
  recognize both values as impassable:
  - Before reaching Alley Rat, both wall types render dark grey and
    look identical.
  - After Alley Rat, room walls become light grey while corridor walls
    stay dark grey.
  - The instant XP first crosses into Alley Rat, every already-
    revealed room wall on the current screen is immediately recolored
    light grey, not just ones discovered from that point forward.
- Confirmed this doesn't add to per-turn redraw cost, which mattered
  given how much of this session focused on cutting that down — the
  one-time generation pass and the one-time recolor-on-title-change
  are both bounded, rare events, not new per-turn work. Also confirmed
  this doesn't interfere with the existing Grand Hallway text-detection
  logic, which only ever looks at corridor floor cells and never at
  void or wall cells.
## Win Condition
- Reaching Shadow Hand is required to win the game.
- A specific dungeon level (not yet decided which) requires the player to
  modify the game itself in order to exit — a meta win condition.
- Guaranteed hints appear at certain dungeon levels (not yet decided which),
  but their placement within the level is random each time.

## Darkness Mechanic (Partial Rollout)
- The previously-discussed dynamic vision/darkness system (shelved for now),
  applied to certain parts of the dungeon rather than entire levels,
  starting at dungeon level 3.
- When built, being in a dark area should also switch the music to
  "Lamenting" (add the condition to the mood check, `QT=` at line 6470).

## Teleportation Circles
- Deeper in the dungeon: rooms containing only "O" characters and nothing
  else.
- Stepping into one teleports the player to a matching circle on the other
  side of the dungeon level.
- Glyph decided: PETSCII 113 (screen code 81 for our POKE-based rendering —
  worth a visual check on real hardware once built).

## Hidden Holes / Trap Tiles
- Dungeon levels 5 and below can contain filled "O" PETSCII characters that
  are actually holes rather than teleport circles.
- Falling into one damages the player.
- Glyph decided: PETSCII 119 (screen code 87), distinct from the
  teleportation circle glyph above — resolves the earlier open question
  about telling the two apart.

## Roaming Vendor
- Starting at dungeon level 5, a chance to encounter a roaming vendor.
- The vendor sells weapons and shields with buffs similar to the weapon
  pickups above.

## "R" - Rest Until Healed
- A new key, separate from the existing SPACE (rest 10 turns, small
  fixed heal). R rests for as long as it takes to fully heal instead of
  a fixed duration.
- Trade-off: the ambush chance on waking up is much higher than SPACE's
  existing per-rest chance (currently LV × 0.75%, capped at 15%) — not
  yet decided how much higher, but meaningfully riskier given the
  guaranteed full heal.
- Open questions for when we build this: how is "how long it takes"
  represented (a longer real-time pause scaled to the number of turns
  rested, similar to the existing 4-second SPACE pause)? Does the
  ambush check happen once, or does risk escalate the longer you rest?

## Monsters Chasing Through Corridors
- Currently, monsters are confined to their home room — one is
  confirmed reachable today (a monster taking a single step into a
  corridor while chasing, then going permanently inert there because
  its AI refuses to act outside a real room).
- The idea: let (some) monsters actually chase you across corridors
  and into other rooms, rather than freezing at the corridor's edge.
- Only certain monster types would chase this way — not all of them —
  and likely only starting at later dungeon levels, rather than being
  a universal behavior from level 1.
- Chasing monsters should only ever be pursuing the player, not
  independently wandering/patrolling on their own when they haven't
  spotted you.
- Interesting extra idea: a chasing monster that runs into a *different*
  monster along the way could end up fighting that monster instead of
  you.
- All of the above are open design questions to think through when we
  actually build this, not decided specifics yet.

## Fast Travel ("T" key)
- Scoped to the current dungeon level only — levels aren't saved once
  you leave them (each one is generated fresh and discarded on
  descent), so traveling back to a previous level isn't part of this;
  that would be a much larger feature (real level persistence) on its
  own.
- Press T to see a list of every named room you've discovered so far
  in the current level, and pick one to teleport to.
- The room you're currently standing in appears in the list too, but
  greyed out and not selectable — you can't fast travel to where you
  already are.
- Never available while fighting or in the middle of resting.
- Using it costs a turn, same as a normal move.
- No empty-list case to handle — the entrance room is always known
  from the moment a level starts, so the list is never empty when T is
  pressed.
- Under consideration: rather than being available from the very start
  of the game, this might work better as a new thief skill instead —
  something like "Backtrack" ("you have a great memory and can swiftly
  run from room to room"), gated behind reaching a specific title the
  same way Keen Eyes, Nimble Fingers, Sneak Attack, and Shadowstep
  already are. Not decided yet which title it would attach to.

## Combat Difficulty / Balance
- Once armed and at Basic Burglar, combat becomes too easy — you rarely
  take damage because your hits are strong enough to end fights before
  the monster gets a real chance to counter. Needs real balance work,
  not yet scoped: could mean toning down early weapon attack bonuses,
  making monsters hit harder or more often at this stage, or something
  else — needs more thought before deciding an approach.
- A confirmed contributing cause, still open: monster HP and damage
  scaling with dungeon depth has effectively been left flat — it needs
  to definitely scale as you go deeper, not just nominally. This is
  part of why the game gets too easy, alongside the weapon-strength
  issue above. Neither the weapon-strength nor the monster-scaling
  side of this has been addressed yet.
- A second contributing cause, now addressed: see "Healing & Ambush
  Rebalance" below. Simulating actual play uncovered that player max
  HP grows completely uncapped, and healing sources scaled off of it
  in ways that compounded into the game getting *safer* over time
  instead of harder — a separate mechanism from the weapon/monster
  scaling issue above, and the first piece of this overall balance
  problem to actually get fixed.

## Dungeon Density
- Maps should feel slightly more dense than they currently do — more
  packed with rooms/corridors relative to the available space. Only a
  small increase, not a major overhaul of generation.

## Named Treasures with Effects
- Beyond plain coin treasure, add specific named treasure items, each
  with its own effect — some good, some bad (a risk/reward or
  identify-the-unknown-item angle, similar in spirit to how weapons
  have individual names and effects).
- Open questions to resolve when we design this: does an effect apply
  immediately on pickup (like a potion) or does it become something
  you carry/equip (like a weapon)? Is it a separate pickup type from
  existing coin treasure, or a variant of it? Do effects reveal
  themselves immediately, or is part of the risk not knowing whether
  a treasure is good or bad until you pick it up?

## Unidentified Potions
- Companion idea to the named-treasures item above, applied to potions
  instead: alongside the existing plain healing potions, add potions
  marked with "??" whose effect isn't known until you drink one — a
  buff, doing nothing at all, or something actively bad.
- Open questions to resolve when we design this: does drinking one
  "??" potion of a given kind reveal what that kind does for the rest
  of the run (so future potions of the same one are then known), or
  does every "??" potion require testing separately? What's the actual
  range of possible effects on each side — what counts as a buff, and
  what counts as something bad (temporary damage, a debuff, something
  else)? Does this replace the existing plain potions, or exist
  alongside them as a separate, riskier pickup?

## Weapons With Variable Stat Rolls
- Currently each weapon type has fixed stats (e.g. Mace is always
  exactly +6 ATK, -1 counter damage). Planned change: each stat rolls
  within a range specific to that weapon type instead of being a fixed
  number — e.g. Mace becomes +4 to +6 ATK, and its counter-damage
  reduction ranges from 0 (no reduction) to -2, rather than always -1.
  Two Maces you find could end up with different actual stats.
- Open questions for when we build this: does every weapon type get
  this treatment, and does it apply to every one of a weapon's stats
  (attack bonus, dodge %, sneak bonus, counter reduction) or only
  some? The comparison screen and character sheet would need to show
  the specific rolled values for the weapon you're holding, not just
  a generic per-type description like they do now.

## Custom Character Set for a Small Set of Glyphs
- Goal: redefine only a handful of characters, not the whole 256-glyph
  set — specifically the player (`@`, into a little-man shape per an
  existing mockup), walls (`#`), floor (`.`), treasure (`$`), and the
  monster symbols.
- Real technical constraint found while scoping this: this program's
  own tokenized code already spans from $0801 to roughly $51A6 — that's
  the code alone, before counting any of its arrays or variables — which
  already exceeds the entire 16K of VIC-II's default memory bank (bank
  0, $0000-$3FFF) by over 4.5KB. There's no free 2K gap left anywhere in
  that bank to hold a custom character set alongside the program.
- The only place a custom character set could actually live is a
  different VIC bank — specifically the always-free RAM at
  $C000-$CFFF. But screen memory and character memory must live in the
  same 16K bank as each other (a VIC-II hardware rule, not a design
  choice), so this means relocating screen memory too, not just adding
  a character set off to the side.
- The real risk in that: screen memory isn't only where this game's own
  POKE-based dungeon drawing writes to — it's also where every ordinary
  PRINT statement writes to, via the C64's own separate, independent
  bookkeeping of "where the screen currently is" (kernal zero-page
  pointers). If screen memory moves without also correctly updating
  that bookkeeping, every PRINT-based screen in the game — messages,
  HUD text, instructions, the character sheet, every Y/N prompt — would
  silently keep writing to a location the chip no longer displays,
  while POKE-based dungeon drawing would keep working fine. That
  mismatch is a real, plausible failure mode, not a hypothetical one.
- Given that, this needs to be built and tested carefully as its own
  piece of work, not rushed — a bank relocation touching both screen
  and character memory is a meaningfully bigger and riskier change than
  swapping a single glyph would have been.
- Update: the hardest, riskiest part of this — the bank-3 relocation
  itself — is now proven working on real hardware, not just reasoned
  through. `rogue6.src` / `petsciipit6.bas`/`.prg` was originally a
  separate test copy for this specific feature, but is now the current,
  primary version of the game going forward — not a test branch. The
  `@` character has been successfully redefined into the little-man
  shape from the mockup, confirmed working by the user, alongside a
  full pre-Alley-Rat darkness system (see below) and the color-scheme
  fixes that came with it. Keep the relocation, interrupt-safe copy,
  and quit-path restore logic as the reference template for when the
  remaining four glyphs (`#`, `.`, `$`, monster symbols) get added —
  that part is already correct and tested; extending it is mainly a
  matter of overwriting a few more characters' worth of bytes in the
  same already-relocated character set, not repeating the risky part
  from scratch.
- Update: in the end, the mainline `petsciipit.bas` didn't need the
  bank-3 relocation described above at all — the "quick memcopy for the
  font" merge (fast font copy update, see below) already lands the
  whole ROM charset in the default bank's own redefinable character
  memory ($C800-$CFFF / 51200-53247) via `SYS 41964`, with no screen-
  memory relocation and no VIC bank switch required. Individual glyphs
  are then overridden by just POKEing 8 bytes per character on top of
  that copy. Custom bitmaps are now in for: player (`@`), floor (`.`),
  potions, treasure/coins (`$`), and all six monster types (Leech,
  Goblin, Imp, Guard, Cultist, Golem), plus the stairs down. The Golem
  also moved off a shared glyph (it used to double up on the reverse-
  video solid-block character) onto its own dedicated slot (screen code
  65) so it no longer collides with anything else.
- Remaining: walls (`#`, screen code 102) are still the only glyph in
  this list using the stock ROM shape rather than a custom bitmap.
- One real mistake worth remembering from getting here: an earlier,
  simpler-looking approach (placing the character set within the
  default bank at a fixed address like $3000, no relocation needed)
  was verified working in an isolated test — but is a dead end for the
  actual game specifically, since the game's own code already extends
  well past that address. That simpler approach only works for small,
  standalone test programs, not this game.

## Everything Dark Before Alley Rat — IMPLEMENTED
- Walls, floor, the player character, monsters, potions, treasure,
  stairs, and weapons on the ground all render dark grey before
  reaching Alley Rat, switching to their normal colors once earned —
  every drawable tile type in the game is now covered.
- "IT'S SO DARK!" recurs throughout that stretch: a 1-in-10 chance on
  any turn where nothing else happened. Fighting a monster while still
  in the dark has a separate 1-in-2 chance of showing "I COULD HARDLY
  SEE THAT THING!" instead of the normal kill/hit message that turn.
- The instructions screen now explains this up front so it reads as
  intentional rather than a bug.
- The moment Alley Rat is first reached, the game shows "MY EYES HAVE
  ADJUSTED!", pauses a second, then recolors every already-revealed
  wall. Reaching Basic Burglar similarly shows "I CAN PICK OUT MORE
  DETAILS!" with the same pause, ahead of a future perk for that tier.
- Along the way, corrected a color-scheme mistake: the C64 has three
  distinct grey shades (light, medium, dark), not two. The player
  character is now cyan after Alley Rat instead of reusing light grey,
  and room walls are medium grey instead of light grey, so they're
  visually distinct from the HUD text which also uses light grey.
- Follow-up fix: the "MY EYES HAVE ADJUSTED!" recolor now covers every
  already-revealed tile, not just walls: potions, treasure, stairs,
  weapons, visible monsters, and the player all switch to their real
  colors on the spot, in the same single screen pass.
## Compilation Using MOSpeed — IN PROGRESS
- Goal: compile both `petsciipit.prg` (the main game) and `petsciipitdemo.prg`
  (the demo) from BASIC to native 6502 machine code using MOSpeed's web
  edition, for a speed boost without a full assembly rewrite. Both are
  hitting problems.
- Same recommended settings apply to both files, worked out from MOSpeed's
  actual documentation rather than guesswork:
  - **Memory holes / locked regions**: add a hole from decimal 49152 to
    53247 for both files. In the demo, this is the exact range the custom
    screen ($C000), the raw `FG` array storage ($C400), and the custom
    character set ($C800) all live in. In the main game, `FG` is still a
    normal BASIC array (never moved to raw storage there), so only the two
    ends of that range are actually used (screen and character set) — the
    middle is genuinely empty, but reserving the same single contiguous
    block is simpler and equally safe. Without this hole, MOSpeed doesn't
    know that range is already spoken for and could place its own compiled
    code, runtime, or variables on top of it. To add it: in the "Memory
    holes / locked regions" section, type 49152 into the "start address
    (decimal)" box, 53247 into "end address (decimal)", then click "Add
    memory hole".
  - **Use hidden RAM**: turn this OFF. Initial recommendation was to turn
    it on, but the actual compile log revealed this is very likely the
    real cause of the demo's black screen (see "Current status" below) —
    it relocates part of the compiled program's own executing code to
    $D000–$FFEB, which collides directly with a POKE already in the boot
    sequence that temporarily banks character ROM into that exact address
    range. The compiled program at ~22.7KB after compaction comfortably
    fits in normal BASIC memory without this anyway, so there's no longer
    a reason to enable it.
  - **Compact level**: raise from Default (which actually disables size
    optimization entirely) to 4 or 5, per MOSpeed's own docs — a 10–15%
    size reduction for roughly 0.5–1% performance cost.
  - **Loop handling ("Remove empty loops")**: recommended to turn OFF.
    This optimization strips loops whose computed value isn't used
    afterward — which describes every timing loop in this game (the
    Keen Eyes pause, rest/stairs/title waits, all sound effects use
    `FOR C9=-1 TO 0:C9=(TI<T2):NEXT C9`-style loops purely to burn time).
    Risk of silently zeroing out all pacing and sound timing without a
    compile error.
  - **Forced integers "ALL!"**: flagged as the highest-risk setting.
    Appears to force every variable to integer with no analysis, which
    would truncate `RND(1)` (always fractional, 0–1) to 0 — silently
    breaking every chance-based mechanic in the game (monster spawns,
    damage variance, ambush chance, the darkness message chances) without
    a visible error. Recommendation: try compiling without it first, using
    only the memory hole + compact level (which carry no behavioral
    risk), and only reach for forced integers if still short on
    space — then test chance-based mechanics extensively afterward.
- Current status: the demo compiled successfully with no reported errors
  (MOSpeed's own log confirms this — 1714 commands compiled, extensive
  optimization passes completed, final output written). The black screen
  is a runtime issue, not a compile failure, and the actual compile log
  points to a specific, traceable cause: with "Use hidden RAM" enabled,
  MOSpeed relocated part of the compiled program's own code to
  $D000–$FFEB. The boot sequence's character-ROM copy trick does
  `POKE 1,PEEK(1) AND 251` right at the very start, before anything else
  runs, which temporarily banks character ROM into that exact $D000–$DFFF
  range so the next few lines can read bitmap data out of it. If part of
  the compiled program's own executing code lives there too, that POKE
  makes the CPU unable to see its own next instructions the instant it
  executes — it starts trying to run character-ROM bitmap data as code
  instead, which crashes or hangs immediately, matching the "solid black
  screen, nothing ever prints" symptom exactly. Resolution: turn "Use
  hidden RAM" off (see updated setting above) and recompile — the
  program's size doesn't require it, and this removes the cause of the
  collision rather than trying to work around it with a narrower memory
  hole.
- Test compile with the music build: MOSpeed's output came out at
  roughly 48-62KB depending on settings, well over the ~37KB of BASIC
  memory available below the music player, so it doesn't fit as-is.
- The main game is also reporting errors when compiled — not yet
  established whether it's the same black-screen symptom. If so, the same
  cause almost certainly applies here too, since the demo's boot sequence
  (including the character-ROM copy trick and the $D000-colliding "hidden
  RAM" relocation) was ported directly from this file — the same "hidden
  RAM off" fix would apply. Still waiting on the specifics of what the
  main game's error actually says to confirm.

## Show HP as Current/Max — IMPLEMENTED
- HUD currently shows "HP:X" (current health only). Change to "HP:X/Y"
  format, showing current health over max health (PM), matching how XP
  and level are already shown with more context.
- Done: the HUD now shows current/max, e.g. `HP:15/30`.

## Faster Screen Restore After Instructions/Character Screen — TRIED, DROPPED
- Currently, pressing I or C clears the screen, shows instructions or
  character info, waits for a key, then calls @REDRAW — which clears the
  screen again and redraws every dungeon tile one at a time from scratch.
  Two possible faster approaches instead of a full tile-by-tile redraw:
  - Save a copy of the dungeon screen to scratch memory before showing
    the instructions/character screen, then copy it straight back
    afterward (the "copy mem trick") instead of regenerating it tile by
    tile.
  - Keep a second, pre-built screen page for instructions/character info
    and just flip the VIC-II's screen memory pointer to it temporarily,
    then flip back — no copying needed at all, just a bank switch.
- Checked where either approach could safely store data: $C000–$CFFF is
  already fully spoken for in both games, so a naive "just use $C000"
  isn't available as-is:
  - Screen lives at $C000–$C3FF (1024 bytes) in both games.
  - Character set lives at $C800–$CFFF (2048 bytes) in both games.
  - The gap in between, $C400–$C7FF (1024 bytes), is empty and free in
    the main game — big enough to hold a saved copy of screen codes
    alone (1000 bytes), but not both screen codes and color data.
  - That same gap is NOT free in the demo — it's fully occupied by the
    raw `FG` array storage (this session's out-of-memory fix), so the
    demo would need a genuinely different location for either approach.
  - Color RAM ($D800–$DBE7) is a separate, fixed memory area that
    doesn't move with VIC bank switching — so the page-flip approach by
    itself only covers screen codes (characters), not their colors.
    Whichever approach is chosen, colors still need their own explicit
    save/restore step, since they can't be paged the same way.
- Open question for whoever picks this up: where a second copy should
  actually live given the above, since $C000–$CFFF is out for both
  games — needs a fresh, unused memory range worked out, not reused
  from what's already claimed.
- Built, tested, and ultimately reverted in the main game. Landed on
  $0400–$07FF (the default screen memory, freed up once the active
  screen moves to $C000) for a "copy mem" save/restore around the I and
  C screens. Two real bugs surfaced in the process: the fast restore
  only covered the narrow explored-tile range, leaving old instruction
  text visible outside it; and the room-name/title-badge row has its
  own redraw cache that needed an explicit reset to notice the screen
  underneath had changed. Both got fixed, but the result was reported
  as still visibly slower than the original @REDRAW it replaced —
  confirmed by re-examining what @REDRAW actually did: `PRINT CHR$(147)`
  is a hardware-fast screen clear, not a BASIC loop, so the replacement
  ended up doing more total interpreted loop iterations (a full blank
  pass plus a restore pass) than the original tile-by-tile approach it
  was meant to beat.
- Investigated whether color RAM could be paged/banked the same way
  screen memory can, to make a page-flip approach fully instant rather
  than needing a copy step for color. Confirmed, with direct technical
  sourcing, that it can't: color RAM is a physically separate chip with
  data pins wired directly to the VIC-II, entirely bypassing normal
  address-bus routing — it stays fixed at $D800 regardless of which VIC
  bank is active, on this hardware. No exception found for the Ultimate
  64 specifically. (One unrelated third-party hobbyist project,
  "UltiMem64" — a physical replacement chip, different product from a
  different maker — does support switchable color RAM pages, but that's
  not this hardware.) This means even a genuine page-flip implementation
  would only make screen codes instant; color would still need an
  explicit copy every time.
- A hand-written 6502 machine-code copy routine (POKEd in and invoked
  via SYS, the same pattern already used elsewhere in this game for the
  fast level-clear trick) could plausibly hit the 2-3ms figures often
  quoted for color RAM copies — but that figure specifically assumes
  hand-assembled code, not a BASIC PEEK/POKE loop, which is what was
  actually tried here. Not pursued this round: harder to verify without
  hardware access, and a wrong byte in hand-assembled code fails
  silently rather than with a catchable error, unlike BASIC. Left as a
  legitimate option for later, if revisited by someone who can test
  directly on hardware — correctly scoped from the start as "write real
  assembly for the copy," not "optimize the BASIC loop further."
- Reverted to the original @REDRAW for both I and C in the main game.
  Not attempted in the demo at all, given the outcome here.

- Fourth attempt: revisited using SYS 41964 (a BASIC ROM block-copy
  routine) plus a "clear ram area" step copied from a public bouncing-
  ball demo listing, after isolated testing seemed to confirm it worked.
  Integrated into the main game, it actively corrupted the running
  program — the "clear" step fills a fixed address range (~2000-9984)
  that overlaps where this game's own BASIC code is stored, so pressing
  I or C overwrote part of the program with blanks live. Reverted
  immediately; this is worse than the earlier slow/buggy attempts, not
  just another dead end.
- Shelved. If ever revisited: lowering BASIC's own memsiz pointer
  (POKE 55/56 + CLR, once at startup only, before any game state exists)
  would give a genuinely reserved safe address range instead of a
  hardcoded guess. But that only fixes where a copy could safely land,
  not why SYS 41964 needed that clear step to avoid corrupting the
  statement right after it — that mechanism is still not understood, and
  is the harder, unresolved half of this idea.

## Quick Memcopy for the Font, Integer Arrays, Safer Array Nulling — IMPLEMENTED
- Merged in a contributed improvement: the font is now copied into
  redefinable character memory with a single `SYS 41964` call (a BASIC
  ROM fast block-copy routine) instead of a byte-by-byte `FOR...NEXT`
  loop — same destination and result, much faster startup.
- `MA`, `RM`, and `FG` (the three largest dungeon-tracking arrays)
  switched from default floating-point to integer type (`MA%`, `RM%`,
  `FG%`), freeing up meaningful memory.
- Replaced the `SYS 45762`-based trick previously used to quickly null
  those three arrays between levels with a plain `FOR...NEXT` loop — the
  `SYS` version is known to break compiled builds, the loop version
  doesn't.
- Since replaced again: array clearing is now done by a small machine
  code routine in the music player (`POKE 780,n:SYS ...`), which zeroes
  the array data in place. Practically instant, and avoids the old
  `SYS 45762` trick entirely.

## Bug Fix: Monsters (and Stairs) Invisible in the Dark — FIXED
- Found and fixed a real bug where monsters revealed by a room's
  static/fog-of-war reveal logic never actually got drawn to the screen
  while the dungeon was still dark (before reaching Alley Rat) — a
  single-line `IF...THEN` in C64 BASIC had the actual `POKE` draw
  statement nested inside an `IF XP>=50 THEN` color check, so it
  silently never ran pre-Alley-Rat. Split into two lines (one sets the
  color, one always draws) at both places this pattern occurred. Fog-of-
  war gating itself (`ML`, `RM%`/`FG%` checks) was untouched and intact.
- Stairs were not actually affected by this particular bug — their draw
  routine was already correctly split. Any apparent stairs invisibility
  pre-Alley-Rat is the existing, intentional one-tile-ahead lookahead
  limit on Keen Eyes, not a bug.

## Background Music: "Dungeoneering" — IMPLEMENTED
- Original 3-voice SID tune (drums, octave bass, lead and arpeggio)
  played from a raster interrupt, so it holds tempo during gameplay
  without touching the game's TI-based timing.
- Loaded automatically from disk at startup by both the game and the
  demo; top of BASIC is lowered (`POKE 55/56` + `CLR`) to make room.
- Mixed quietly through the envelopes so sound effects stay audible.
- Sound effects borrow voice 1 and hand it back afterwards; the music
  resumes on that voice's next note.
- Music is stopped cleanly when quitting to BASIC.

## Separate Music and Sound Effect Toggles — IMPLEMENTED
- M toggles music, E toggles sound effects (M used to be the sound
  mute). Instructions screen updated in both the game and the demo.

## Faster Level Generation — IMPLEMENTED
- Array clearing between levels moved to machine code (game and demo;
  the demo's fog map at $C400 too).
- Corridor walls placed while digging corridors instead of a separate
  full-map scan.
- Room types (treasure room/apothecary) recorded when contents are
  placed instead of rescanning every room tile by tile.
- Verified identical dungeons to the old generator over 5,000 layouts.

## Fight Music: "Assailing" — IMPLEMENTED
- Music data converted to reusable patterns with transpose: both songs
  now take 2KB, down from nearly 3KB for one, freeing 1KB for BASIC
  (player now at $9800, state in the cassette buffer).
- Short, scary fight loop: heartbeat kick, grinding bass, sinking
  diminished chord.
- Plays while a living monster is in the player's room or the player is
  fighting one; switches in as you enter the room or attack, before the
  monster acts.
- Switches back when the monster dies or you leave the room, and
  "Dungeoneering" resumes exactly where it paused.
- A new level always returns to "Dungeoneering".

## Bug Fixes: Key Buffer After Kills, Doorway Disappearing — FIXED
- Keyboard buffer is cleared once a kill finishes (like bumping a wall),
  so keys mashed during a fight no longer send the player running.
- Attacking from a doorway into an unrevealed room redrew the doorway
  over the player, leaving them invisible until their next move. The
  room reveal now redraws the player.

## Redrawn Glyphs: Chest, Golem, Goblin, Imp — IMPLEMENTED
- New 8x8 designs for the treasure chest (screen code 36), Golem (65),
  Goblin (88), and Imp (90), in both the game and the demo. Only the
  POKE values changed (lines 156-159 and 166-169); character slots and
  colors are unchanged.

## Music Timing — IMPLEMENTED
- To fix:
  1. When eyes adjust right after a fight, the fight music keeps playing
     through the "MY EYES HAVE ADJUSTED!" pause and recolor. It should
     switch to "Dungeoneering" as soon as the fight ends. (Cause: the
     eyes-adjust step runs in the kill path before the music check.)
- To change:
  1. After a fight ends, the music stops, and "Dungeoneering" starts
     again when the player moves.
  2. Music stops while resting and starts again when the player starts
     moving.
  3. Music starts as soon as the first level starts being created
     (descending to level 1). Currently there's no music while level 1
     is built; it only begins after the game is drawn the first time.
- Done, all four, using new pause/unpause routines in the music player:
  - The fight check now runs the moment the monster dies, before the
    eyes-adjust pause.
  - When a fight ends, the music goes silent and Dungeoneering continues
    (from where it paused) on the next step.
  - Resting pauses the music; moving starts it again. A new fight always
    starts its music straight away, even mid-rest.
  - Music starts before level 1 is built and plays during every level
    build, then pauses once the level is ready until the player moves.

## Level Loading Progress Bar — IMPLEMENTED
- When descending to a new level, draw a progress bar under the
  "DESCENDING TO LEVEL..." text while the level is generated.
- The bar is made of `.` characters, shaded from lightest to darkest:
  white, then the C64's three greys (light grey, medium grey, dark grey).
- Built as three dots after "PLEASE WAIT ..." whose colors cycle left to
  right through white, light grey, medium grey, dark grey while the level
  is generated, stepping about 7 times a second off the jiffy clock.
- The startup message is now "BUILDING THE DUNGEON, PLEASE WAIT ..." and
  shows while the music loads (dots still during the load itself).
- Lesson learned: poking the dot colors into color RAM never showed up
  on screen; printing the dots with color codes at the saved cursor
  position does.

## Separate Music for NTSC and PAL — IMPLEMENTED (partly)
- Use different versions of the songs on NTSC and PAL machines.
- Current state: both songs sound right on PAL. On NTSC:
  - "Dungeoneering" plays too fast.
  - "Assailing" plays very fast, the sound is choppy, and it seems to
    cause problems with the sound effects.
- Notes for when this is built: the player runs once per screen frame,
  which is 50 times a second on PAL but 60 on NTSC, so everything plays
  20% faster there. NTSC's different clock speed also shifts every note
  slightly sharp unless it gets its own note table. The choppiness and
  the clash with sound effects in "Assailing" still need to be tracked
  down on NTSC.
- Done: the game, demo, and glyph showcase check `PEEK(678)` at startup
  and load `musicpal` or `musicntsc`. The NTSC build has its own note
  table and stretched bars, so both songs keep their PAL tempo and pitch.
  Same player code and size, so every SYS address is unchanged.
- Still open: the "Assailing" choppiness and sound-effect clash on NTSC.

## Machine Type on the Instructions Screen — IMPLEMENTED
- The instructions screen's last line now reads "PAL - PRESS ANY KEY TO
  CONTINUE" or "NTSC - PRESS ANY KEY TO CONTINUE", using `PEEK(678)`.

## Music Mood: "Lamenting" — IMPLEMENTED
- Third song, "Lamenting": slow, sparse, sad version of Dungeoneering's
  opening phrase (Am - F - Dm - E), about 10 seconds, looping.
- Plays when it's very dark (before Alley Rat, XP under 50) or near death
  (HP below a quarter of max). Dungeoneering otherwise. Dark areas from
  the Darkness Mechanic are to be added when that is built.
- Dungeoneering and Lamenting each keep their own place and continue
  where they left off. Fights switch to Assailing and return to the
  current mood.
- The music player moved down one page to $9700 to fit the new song
  (POKE 56,151); every SYS/POKE address dropped by 256. New entry:
  POKE 780,0 or 1 then SYS 38690 sets happy or sad.

## BLITZ! Compilation — PLANNED
- Goal: compile the game (and the demo) with the BLITZ! BASIC compiler.
  Moving the music player out of BASIC memory to $C000-$CFFF comes
  first, so the compiled program gets all of BASIC RAM and nothing
  depends on BASIC's own memory layout.
- BLITZ! memory layout:
  - The runtime lives at $0801-$1F92.
  - The compiled p-code lives at $1F93 onward.
  - Variables and arrays are created dynamically in the RAM directly
    after the end of the compiled program data; the runtime manages
    variable storage itself.
  - To keep as much RAM as possible for large programs, the runtime
    takes space down from the top-of-BASIC pointer for its machine
    language routines and variables.
  - When necessary it swaps boundaries with the C64's own input buffers,
    so its routines and compiled arrays don't collide with active system
    memory.
- Current use of $C000-$CFFF: screen at $C000-$C3FF, custom font at
  $C800-$CFFF. $C400-$C7FF is free in the game but holds the fog map
  (`PEEK(50176+IX)`) in the demo. The player is 2,269 bytes, so it does
  not fit as things stand.
- Making room:
  - Move the custom font to $F000-$F7FF, under the KERNAL ROM. The VIC
    reads the RAM there and the CPU only ever writes to the font, so the
    font copy and glyph POKEs work unchanged apart from the address.
    `POKE 53272,3` becomes `POKE 53272,12`. The screen stays at $C000.
  - That frees $C400-$CFFF (3KB) for the player.
  - In the demo, move the fog map from $C400 to $0400-$07E7 (the old
    screen area, unused since the screen moved to $C000).
- Music player:
  - The real source (player.asm, compose.py, build.py) is recovered and
    rebuilds musicpal.prg and musicntsc.prg byte for byte, and already
    assembles at $C400.
  - Reassemble with BASE=$C400. Every SYS entry point moves (38662 ->
    50182, etc.) in the game, demo and glyph showcase.
  - Move the player's state (`vstate`, now $033C-$03D3 in the cassette
    buffer) into the $C400 block too, in case BLITZ! uses the cassette
    buffer.
  - Verify the moved player against the old one: same SID writes every
    frame for all three songs, PAL and NTSC.
- Things that would break under BLITZ!:
  - The array-clear helper (`SYS 38672`) walks BASIC's variable tables
    via $2F/$30. BLITZ! stores variables its own way, so this must be
    replaced (plain FOR loop or another method).
  - `LOAD F$,DV,1` inside the program (line 60) relies on interpreted
    BASIC restarting the program after the load. Replace with a tiny
    uncompiled loader that loads the music, then loads and runs the
    compiled game.
  - `POKE 55/56` + `CLR` (line 20) only protects the player at $9700 and
    can be removed once it lives at $C400.
- Not started: waiting on a full plan with every changed line before any
  code is written.

## Optimization Pass — IN PROGRESS
- Glyph setup as DATA/READ — IMPLEMENTED (game, demo, glyph showcase):
  the 11 custom glyphs are one DATA line each, written by a short READ
  loop instead of 88 POKEs. Same bytes; each program 533 bytes smaller.
- Integer arrays — IMPLEMENTED (game and demo): the 13 remaining
  floating-point arrays (`RX`, `RY`, `RW`, `RH`, `RV`, `RT`, `MX`, `MY`,
  `MH`, `MP`, `ML`, `MK`, `MQ`) and the demo's trail array `V` are now
  integer arrays (`RX%` etc.). Every value they hold is a whole number
  well inside -32768..32767. Each element drops from 5 bytes to 2: 354
  bytes of array space saved in the game, 375 in the demo; the extra `%`
  in every use adds 153 / 189 bytes to the program, so the net gain is
  about 200 bytes free in the game and 186 in the demo. Speed is about the
  same (BASIC converts integer elements to floating point when reading).
  The array-clear helper is unaffected (it still clears the first 3 / 2
  arrays: MA%, RM%, FG% / MA%, RM%).
- Integer scalar variables — NOT DONE, on purpose: in interpreted BASIC
  V2 every simple variable takes 7 bytes whether it is `A` or `A%`, and
  BASIC converts `%` values to floating point for every calculation, so
  converting them saves no memory and runs slower — against both goals of
  this pass. Revisit under BLITZ!, where integer variables may compile to
  real integer maths.
- Fewer IFs — IMPLEMENTED (game and demo):
  - Tile drawing (game 4280-4360, demo 4240-4320): reads the tile once
    (`T=MA%(IX)`), draws floor first, weapons second, and jumps straight
    to the right line with `ON T+1 GOTO` instead of up to 12 IF lines
    that each looked the tile up again. The "dark or lit" color is worked
    out inline (`K1-(XP>=50)*(color-K1)`), so each tile type is one line.
    Checked against the old code for every tile value, dark and lit.
  - Monster and weapon stats: loaded once at startup from DATA tables
    (end of each listing) into small integer arrays (`MG%`, `MZ%`, `HB%`,
    `MB%`, `XB%`, `KB%`, `SF%`, `MN$` / `WG%`, `WZ%`, `WA%`, `WD%`, `WX%`,
    `WM%`, `WN$`, `WE$`). The lookups (game 4930 and 5320, demo 4890 and
    5140) are now one line each instead of 6 and 5 IF lines. Row 0 holds
    the leech / dagger, matching the old default. Checked value for value
    against the old IF chains.
  - Keen Eyes (game 3870-3930, demo 3830-3890): works out the step and
    side offsets for the direction once, then checks each square through
    one small reveal routine (game 4260, demo 4220) — about 12 lines run
    per step instead of about 40. Reveals the same squares in the same
    order for every position, direction and title (checked exhaustively).
  - Title tier: `TT` is one expression,
    `TT=-(XP>=50)-(XP>=150)-(XP>=300)-(XP>=600)`, in the three places it
    was a block of five lines, and the title names come from a `TL$`
    table instead of IF chains (character sheet, new-title message, HUD).
  - Hot new variables (`T`, `EB`, `ES`, `EP`) are created early on the
    variable setup line so BASIC finds them quickly.
  - Demo only: the AI's move choice (6570-6700) returns as soon as a move
    is picked instead of testing every remaining line. It now skips one
    `RND(1)` call it used to make after a move was already chosen, so the
    demo's random sequence differs; behaviour is otherwise the same.
  - Result: each program about 1.5KB smaller (game 22,948 -> 21,457
    bytes, demo 24,706 -> 23,002), minus about 360 bytes for the new
    tables while running.
  - Not changed: key handling and the turn-message builder (run once per
    turn, little to gain); the `IF XP>=50 THEN CW=...` color picks
    elsewhere (a flag would test just as slowly as `XP>=50`); the glyph
    showcase (none of these routines are in it).
- HUD and message lines as one PRINT — IMPLEMENTED (game and demo):
  - HUD (game 5460-5510, demo 5240-5290): first compares the five values
    it shows (HP, max HP, XP, level, coins) with copies from the last
    draw and does nothing if none changed. Otherwise it builds one string,
    `H$`, holding the cursor-home code, the label/value colors (`{GRY3}` /
    `{WHT}`) and padding to 40 visible characters, and prints it with a
    single `PRINT H$;`. Replaces the old routine that POKEd every
    character and blanked the rest of the row one cell at a time.
  - Message lines (game 5380-5400 and 5420-5440, demo 5200-5220): each
    builds one string with its cursor and color codes and padding
    (`M1$`, `N1$`) and prints it only if it differs from what was last
    printed (`M2$`, `N2$`).
  - Wherever the screen is cleared and redrawn (new level, death screen,
    return from the I/C screens) the copies are reset (`HF=1:M2$=""`,
    and `N2$=""` in the game), so the HUD and messages always come back.
  - Padding is skipped if a line would ever be longer than 40 characters,
    so an unusually long value can't cause an error.
  - The room-name/title row is unchanged (it already printed on change
    only).
- Hot routines moved to the top — IMPLEMENTED (game and demo):
  - Why: for `GOSUB`/`GOTO` to a higher line number BASIC walks forward
    line by line from the current line; to a lower one it walks from the
    first line of the program. Routines in the middle of a 630-line
    program cost hundreds of lines walked per call.
  - Lines 10-80 (boot, music load, jumps) still come first. The routines
    called most often follow, most frequent first; then the main loop
    (and the demo's AI move choice right after it); then everything else
    in its original order; then the level build, the one-time startup
    setup and the DATA tables at the end (the glyph DATA still comes
    before the monster/weapon/title DATA, so READ order is unchanged).
  - The whole program is renumbered in steps of 10.
  - Lines walked: a plain move 1,888 -> 874; each tile of a room reveal
    133 -> 9; each moving monster 415 -> 35; each revealed square's wall
    check 141 -> 2; HUD from combat 328 -> 31; level build corridor walls
    462 -> 167 per square.
  - Audited with a script against the previous listing: same line count,
    every line's text identical apart from line numbers, every
    GOTO/GOSUB/THEN/ON target maps to the same statement as before and
    exists, every line that can fall through still falls through to the
    same line, DATA in the same order, numbering strictly 10, 20, 30....
    Both listings tokenize and round-trip cleanly.
  - Line numbers mentioned elsewhere in this section are from before the
    renumber. Where the moved routines are now:

  | Routine | Game (old -> new) | Demo (old -> new) |
  |---|---|---|
  | Tile draw | 4280-4360 -> 90-170 | 4240-4320 -> 90-170 |
  | Reveal one square (Keen Eyes) | 4260-4270 -> 180-190 | 4220-4230 -> 180-190 |
  | Corridor-wall reveal | 6200-6250 -> 200-250 | 6920-6970 -> 200-250 |
  | Monster lookup | 4930 -> 260 | 4890 -> 260 |
  | Player weapon stats | 5050-5070 -> 270-290 | 5040-5060 -> 270-290 |
  | Weapon lookup | 5320 -> 300 | 5140 -> 300 |
  | HUD | 5460-5510 -> 310-360 | 5240-5290 -> 310-360 |
  | Room-name/title row | 5670-6080 -> 370-690 | 5450-5860 -> 370-690 |
  | Message line | 5380-5400 -> 700-720 | 5200-5220 -> 700-720 |
  | Second message line | 5420-5440 -> 730-750 | — |
  | Fight-music check | 6330-6400 -> 760-830 | 7050-7120 -> 730-800 |
  | Mood-music check | 6470-6480 -> 840-850 | 7190-7200 -> 810-820 |
  | Sound effects | 2840-3030 -> 860-1050 | 2780-2970 -> 830-1020 |
  | Potion sound | 3770-3790 -> 1060-1080 | 3730-3750 -> 1030-1050 |
  | Coin sound | 3840-3860 -> 1090-1110 | 3800-3820 -> 1060-1080 |
  | Monster movement | 2110-2300 -> 1120-1310 | 2140-2330 -> 1090-1280 |
  | Keen Eyes | 3870-3930 -> 1320-1380 | 3830-3890 -> 1290-1350 |
  | Room reveal | 2720-2830 -> 1390-1530 | 2660-2770 -> 1360-1500 |
  | Turn message | 3370-3490 -> 1540-1660 | 3340-3460 -> 1510-1630 |
  | Corridor walls (level build) | 6110-6190 -> 1670-1750 | 6830-6910 -> 1640-1720 |
  | Loading dots | 401-402 -> 1760-1770 | 421-422 -> 1730-1740 |
  | Main loop | 1370-2100 -> 1780-2540 | 1390-2130 -> 1750-2520 |
  | Level build | 410-1360 -> 4590-5560 | 430-1380 -> 5290-6260 |
  | Startup setup | 40-400 -> 5570-6130 | 40-420 -> 6270-6830 |
  | AI move choice | — | 5870-6820 -> 2530-3480 |

## Bug: No Fight Music After an Ambush — TO DO
- Reported from hardware: fight music doesn't seem to start when a
  monster ambushes you while resting.
- Likely causes, from the code (not fixed yet):
  - The ambush (3710-3820) never runs the fight-music check (760). The
    check only runs after all 10 rest turns are over (2760), so the
    ambusher attacks during the rest with no fight music.
  - If you rest in a corridor, the fight-music check only counts monsters
    inside rooms (770: `IF RQ=0 ... THEN 800`), so a corridor ambush never
    switches to fight music. The monster movement loop also skips
    monsters that aren't in a revealed room, so a corridor ambusher just
    stands there.
- Possible fix: run the fight-music check straight after the ambush
  message, and decide how monsters in corridors should count.
- Same code in the demo (ambush 4570-4680).

## Ambush Message Wording — IMPLEMENTED
- "A MONSTER AMBUSHES YOU!" is now "A MONSTER AMBUSHED YOU!" (game line
  3810, demo line 4670).

## Resting Shows Cycling Dots — PLANNED
- While resting, show "RESTING ..." with the same color-cycling dots used
  for "PLEASE WAIT ..." during level builds (white, then the three greys,
  left to right), instead of the plain "RESTING..." message.
- Resting currently prints "RESTING..." on the message line (game 2570,
  demo 3490), then waits before the rest turns run: about 4 seconds in
  the game (240 jiffies), 1 second in the demo (60 jiffies). The dots
  would animate through that wait.
- Game only. Not for the demo: its rest wait is only 1 second, too short
  for the dots to be worth it.

## Second SID for Music — IMPLEMENTED
- The music player checks for a second SID at $D420 the first time the
  music starts, using voice 3's oscillator readout (the test bit stops a
  real second chip but not a mirror of SID 1). Boards where SID 1 also
  answers at $D420 fall back to one SID.
- Second SID found: the music's three voices move to $D420 and the sound
  effects have SID 1 to themselves (no more voice-1 hand-off).
- One SID: unchanged behaviour (voice-1 hand-off), but at full volume.
- The music is now always the full, original mix (same as the .sid
  files); the quiet mix and its note clicks are gone.
- Result is in PEEK(38693): 1 = one SID, 2 = second SID at $D420.
- The music file now loads at $9600 (POKE 56,150); the jump table stays
  at $9700, so every SYS address is unchanged.
- Music now starts just before the first instructions screen, so the
  check has already run there; its bottom line reads "PAL 2SID - ..."
  (or "NTSC 2SID - ...") when a second SID is found.

## Volume Control — IMPLEMENTED
- One SID: M mutes the music, E mutes the sound effects (each on its
  own, as before), and V cycles the shared volume HIGH (15) -> MEDIUM
  (10) -> LOW (5) -> HIGH, shown as "VOLUME HIGH" etc. Starts at HIGH.
  The volume is put back after M stops or restarts the music, since the
  player resets it to 15.
- Two SIDs: separate volumes, no mute and no V key.
  - M cycles the music (SID 2, $D438): MEDIUM -> LOW -> OFF -> HIGH.
    Starts at MEDIUM. OFF only turns the volume to 0, so the tune keeps
    its place.
  - E cycles the sound effects (SID 1, $D418): HIGH -> MEDIUM -> LOW ->
    OFF. Starts at HIGH. At OFF the effect routines are skipped too.
  - Shown on the message line under the HUD: "MUSIC MEDIUM",
    "SOUND FX OFF" etc.
- Instructions line: "M - MUSIC  E - EFFECTS  V - VOLUME" with one SID,
  "M - MUSIC  E - EFFECTS" with two.
- NS = number of SIDs (PEEK(38693)), set on line 6040 when the music
  starts. M and E use ON NS GOSUB (one SID: 3330/3400, two SIDs:
  6330/6340); MV=1-MV and MU=1-MU moved into 3330/3400.
- New lines after the DATA, so no renumbering: 6310-6320 (V, one SID),
  6330 (music, two SIDs), 6340 (effects, two SIDs). V check on the end
  of key line 1780; VL=15:VM=10:VF=15 on line 6100, where the music used
  to start (now on 6040).
