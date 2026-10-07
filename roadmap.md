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
- The main game is also reporting errors when compiled — not yet
  established whether it's the same black-screen symptom. If so, the same
  cause almost certainly applies here too, since the demo's boot sequence
  (including the character-ROM copy trick and the $D000-colliding "hidden
  RAM" relocation) was ported directly from this file — the same "hidden
  RAM off" fix would apply. Still waiting on the specifics of what the
  main game's error actually says to confirm.

## Show HP as Current/Max
- HUD currently shows "HP:X" (current health only). Change to "HP:X/Y"
  format, showing current health over max health (PM), matching how XP
  and level are already shown with more context.

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
