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

## Hidden Holes / Trap Tiles — IMPLEMENTED
- From dungeon level 5, a level may have one hole: 20% chance on level 5,
  40% on 6, 60% on 7, 80% on 8, and always from level 9. Never more than
  one. It sits on a random floor square inside a room, never in the
  entry room or the stairs room, never on an item or a room's centre.
- Glyph: PETSCII 119 (screen code 87), light grey, distinct from the
  planned teleportation circle (PETSCII 113).
- Hidden by default. The first time its room is revealed, a player with
  Keen Eyes gets one roll to spot it: 25% x Keen Eyes level (1 or 2)
  + 2% x character level, capped at 90%. No Keen Eyes = never seen. If
  the roll fails it stays hidden until you fall in.
- Falling in (stepping on it, seen or not): "AAAAH! YOU FELL INTO A PIT!",
  a 2-second pause, the DESCENDING screen, and you land on the next
  level, taking INT(MAX HP/10) + INT(LEVEL/2) damage (never below 1 HP,
  no stairs heal). "THE FALL HURT! -n HP" is shown. Lamenting plays
  until you move.
- Lines: hole placement 6420-6450 (called from 5390), spotting 6460-6470
  (called from the room reveal at 1440), fall 6380-6410 (from 2350),
  hole drawing 6370 (12th entry of the tile ON GOTO at 110). The hole's
  square is kept in HZ; a seen hole is MA% = 11, a hidden one stays
  floor. QP=1 makes the mood check (840) choose Lamenting; moving clears
  it (2440).

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

## Monster Scaling, Groups, Character Levels, Random Weapons — IMPLEMENTED
- Worked out with a Python simulation of 400 runs through levels 1-30
  using the game's real rules (option "C"). The old game stopped being
  dangerous after level 5 (2-7% of max HP lost per level); now each
  level costs roughly 40-80% and it keeps getting harder.
- Monster HP: 5 + LEVEL + 2 x type bonus (was 6 + LEVEL/3 + bonus).
  Monster attack: 2 + LEVEL/4 + type bonus (was LEVEL/8). Lines 5190,
  3780 (ambush).
- Hit-back when you attack is now random from 0 up to that monster's
  attack (was a flat 0-3), still halved by Nimble Fingers and reduced
  by the Mace and dodge. Line 2110.
- Monster groups: from dungeon level 3 a map monster can be a group,
  fought one after another on the same square. Max size 1 + (LEVEL+1)/4,
  capped at 5 (levels 3-6: up to 2, 7-10: 3, 11-14: 4, 15+: 5); the
  size is rolled when the level is built (GS%, GK% arrays). When one
  dies and more are left, the next one stands up at full HP and the
  message reads "ANOTHER GOBLIN! +6XP +3GP". Weapons only drop when the
  last of the group dies. Ambush monsters are always single.
- Group rewards: coins in full for every monster; XP full for the
  first, half for the second, a quarter for each one after.
- Character levels: level N needs 25 x N x (N+1) XP (50, 150, 300, 500,
  750, 1050, 1400, 1800, 2250, 2750...). Each level up raises max HP by
  5 x the new level (+5, +10, +15...). Replaces +5 max HP every 50 XP.
  Lines 2210-2220. The character sheet shows the XP for the next level;
  the instructions now read "LEVEL UPS RAISE MAX HP MORE EACH TIME".
- Titles stay at 50 / 150 / 300 XP; Shadow Hand moved from 600 to 750 XP
  (character level 5).
- Random weapon stats: a dropped weapon gets its type's base attack plus
  a random 0 to LEVEL/3. The roll is stored with the weapon on the
  floor (map value 19 + type + 10 x roll), shown in the compare message
  and on the character sheet, and kept when you equip it (WR).
- The demo has all of this too.

## Combat Difficulty / Balance
- Update: monster scaling and weapon strength are now addressed — see
  "Monster Scaling, Groups, Character Levels, Random Weapons" above.
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
- Every volume key steps 0 -> 3 -> 6 -> 9 -> 12 -> 15 -> 0 (0 = mute,
  then 5 steps). The setting shows on the message line under the HUD as
  a slider: the name, then one solid (reversed space) block per step and
  checkered blocks for the rest, e.g. "MUSIC" + 3 solid + 2 checkered.
- One SID: M mutes the music, E mutes the sound effects (each on its
  own, as before), and V steps the shared volume (both registers).
  Starts at 9. The volume is put back after M stops or restarts the
  music, since the player resets it to 15.
- Two SIDs: separate volumes, no mute toggles and no V key.
  - M steps the music (SID 2, $D438). Starts at 3. At 0 the tune keeps
    playing silently, so it keeps its place.
  - E steps the sound effects (SID 1, $D418). Starts at 15. At 0 the
    effect routines are skipped too.
- Instructions line: "M - MUSIC  E - EFFECTS  V - VOLUME" with one SID,
  "M - MUSIC  E - EFFECTS" with two.
- NS = number of SIDs (PEEK(38693)), set on line 6040 when the music
  starts. M and E use ON NS GOSUB (one SID: 3330/3400, two SIDs:
  6330/6340); MV=1-MV and MU=1-MU moved into 3330/3400.
- New lines after the DATA, so no renumbering: 6310-6320 (V, one SID),
  6330 (music, two SIDs), 6340 (effects, two SIDs), 6350 (builds the
  slider, padded to the full 40 columns so it clears longer messages).
  V check on the end of key line 1780. Line 6040 starts the music, sets
  VL=9:VM=3:VF=15 and the starting volumes, once. Old lines 6090 (SID
  volume 15 and voice-1 envelope) and 6100 (music start) are removed:
  the player's start sets the volume and clears the SID, and every sound
  effect sets voice 1's envelope through SYS 38668.
- Glyph showcase: V steps the music volume the same way, starting at 15,
  with the slider on row 24. It sets both $D418 and $D438 without
  checking for a second SID (no sound effects; on one SID $D438 is a
  mirror of $D418). Lines 540 (key line), 545 (VL=15), 554 (V check:
  ON -(A$="V") GOSUB 610), 610-620 (volume and slider).

## Demo AI Door Finding — IMPLEMENTED (demo only)
- The demo's AI now records the corridors and doors while the level is
  built and routes through them (details in roadmapdemo.md, "AI Misses
  Doors"). The game itself is unchanged.

## Faster "My Eyes Have Adjusted" Recolor — IMPLEMENTED
- The recolor when Keen Eyes arrives (lines 4420-4510) used to check all
  1000 screen squares. It now only checks the rows already explored
  (YL to YH, the same limits the redraw at 3220 uses), so the pause after
  "MY EYES HAVE ADJUSTED!" is much shorter early in the game. Every square
  seen so far is still recolored. Line 4420 only.

## Instructions Screen Wording for Two SIDs — IMPLEMENTED
- With two SIDs the key line reads "VOLUME  M - MUSIC  E - SOUND EFFECTS";
  one SID keeps "M - MUSIC  E - EFFECTS  V - VOLUME" (game line 3040).
  The demo shows the same "VOLUME" prefix with two SIDs (line 3900).

## Animated Characters (Player and Monsters) — IMPLEMENTED
- Sid drew a second frame for every monster and three extra frames for
  the player. They live in the reversed half of the character set:
  each monster's second frame is its screen code + 128 (Golem 193, Leech
  211, Guard 214, Goblin 216, Imp 218, Cultist 219); the player has 128
  (fighting), 129 and 130 (walking). Added to the glyph DATA lines
  (5730-5830), loaded with the others (now 20 glyphs, line 5710).
- Monsters flip between their two frames every time they move or
  attack, and when you hit them. Each monster keeps its own frame
  (XF%, 0 or 128), so two of the same kind can be out of step.
- Player: walking alternates 129 and 130 on every step; attacking shows
  128; after about 1/3 second with no key pressed he goes back to
  standing (0). The key wait at 1780 now times out after 20 jiffies and
  then 6480 puts the standing frame back and keeps waiting. Each new
  level starts standing.
- Side effect: reversed "@", "A", "B" and a few reversed graphics
  characters now draw these frames. The game only uses a reversed space
  (the volume slider), which is unchanged.
- Demo: same frames; the player shows the standing frame when the AI
  rests and on each new level. Glyph showcase: the player and monsters
  animate (player cycles stand, walk, walk, fight).

## Demo Speed-up — IMPLEMENTED (V14, demo only)
- The demo's AI was made much faster without changing its decisions;
  details in roadmapdemo.md.

## Loader and Title Screen — IMPLEMENTED (V15)
- New first file on the disk, "PETSCII PIT" (source petsciipitloader.bas).
  LOAD"*",8 and RUN loads it. It loads the music (PAL or NTSC), copies the
  font and the 20 custom glyphs into RAM, sets up the screen, starts the
  music and checks for a second SID. All of this used to be repeated at
  the start of the game, the demo and the glyph showcase.
- Title screen: the player and the six monsters blown up so each pixel is
  a character (8x8 characters each), dancing between their two frames and
  scrolling right to left, with the version, PAL/NTSC and 2SID, and a
  menu: P play, D demo, G glyph showcase, I instructions, C credits.
  The big pixels use screen code 94 (pi), redefined as a solid block.
- Title animation (V18): four pre-built string sets (T$(3,7)); the player
  cycles stand/walk/walk/fight, monsters alternate their two frames; the
  scroll moves 2 columns per step, all 8 rows in one PRINT with colour
  codes (lines 390-500 of the loader).
- Double buffering (V18): the title is drawn on two screens, $C000 and
  $C400 (the demo's fog map, unused while the loader runs). Each step
  points PRINT at the hidden one (POKE 648,192 or 196), prints the 8 rows
  there, then shows it with one POKE 53272 (3 or 19). The static text is
  drawn on both screens; instructions, credits and loading switch back to
  $C000 first. Loader lines 460-490, 540-570.
- Play and Demo load straight to "DESCENDING TO LEVEL 1, PLEASE WAIT ...";
  the music keeps playing from the title screen. Quitting the game (Q,
  confirmed), the demo (hold Q) or the showcase (Q) loads the loader and
  returns to the title menu.
- The game, demo and showcase now require the loader and print "PLEASE
  LOAD PETSCII PIT FIRST" otherwise. They check a 2-byte signature the
  loader writes at 38654-38655 (in the free end of the music file's
  first page), then fix BASIC's variable pointer after being loaded from
  another program (POKE 45,PEEK(174):POKE 46,PEEK(175):CLR).
- Instructions screen: the loader draws it once (with the version,
  PAL/NTSC, 2SID and the right key line) and stores a copy of the
  characters and colours in the RAM under the KERNAL ROM ($E000-$E7FF),
  which BASIC can write but nothing else uses. Two small machine-code
  routines in the free part of the music file's first page copy it:
  SYS 38576 stores the screen, SYS 38512 shows it again (a fraction of
  a second). The I key in the game and demo now just does SYS 38512, so
  the instruction text is no longer in either program. The version now
  lives in the loader's instructions screen and title screen.
- Memory won back: game 23511 -> 20964 bytes (about 2.5 KB), demo 25897
  -> 23569 (about 2.3 KB), glyph showcase 2867 -> 1819.
- All three programs were renumbered in steps of 10 again. Main places in
  the game now: main loop 1760, instructions 2970, level build 4340,
  startup 5320, volume routines 5740-5780, groups 5790, hole drawing
  5800, fall 5810-5840, hole placement 5850-5880, hole spotting 5890,
  idle standing frame 5910.
- V17: the loader stops the music (SYS 38665) before loading a program;
  the game (5500) and demo (6300) start it again (SYS 38662) as they head
  down to level 1, and the showcase starts it on its own screen.
- V18 fix: the loader also resets BASIC's end-of-program pointer
  (POKE 45,PEEK(174):POKE 46,PEEK(175):CLR on line 30) when another
  program loads it; returning from the shorter glyph showcase used to
  crash with ?UNDEF'D STATEMENT ERROR IN 500.
- Quitting any program (Q) now stops the music (SYS 38665) before loading
  the loader, to avoid glitches during the load.
- Loading screens: for Play and Demo the loader prints exactly the game's
  "DESCENDING TO LEVEL 1, PLEASE WAIT ..." line; for other programs
  "LOADING <NAME> ..." (e.g. LOADING GLYPH SHOWCASE). The three dots are
  shown in the cycling colours but stay still during the disk load; the
  loaded program prints the same line, then starts the dot cycling and
  the music. Loader lines 510-530 (texts) and 570.
- The game and demo no longer clear the screen during their startup, so
  the loader's "DESCENDING TO LEVEL 1" screen stays up until the level
  build reprints it and starts the dots and the music.
- Credits (V16): design, code and graphics by m0nde; music by m0nde;
  thanks to Ricky Derocher, Eyvind Ebsen and Bobby Brightling;
  https://m0nde.itch.io/petscii-pit; (C)2026 m0nde - CC BY 4.0.
- The RAM under the KERNAL ($E800-$FFFF) is still free for later: level
  files and story text can be kept there without using BASIC memory.

## Version Numbers — IMPLEMENTED
- Every build has a 2-character version, starting at 12 (Sid had pushed
  11 builds before). Order: 00-99, then 0A-0Z, 1A-1Z ... 9A-9Z, then
  A0-AZ ... Z0-ZZ, then combinations with "!".
- The .d64 is always titled PETSCII PIT and its disk ID is the version.
- The version shows on the top line of the instructions screen in the
  game (2990) and demo (3850), e.g. "PETSCII PIT V12 - HTTPS://M0NDE.ITCH.IO",
  and in the glyph showcase title (340). Updated on every build.
- Zips are named "petscii-pit-all-<version>.zip"; SID-only zips are
  "petscii-pit-sids-<version>.zip" (no spaces in file names).

## Battle Screen — IMPLEMENTED (V19)
- Every fight switches to a battle screen: the player and the monster
  drawn big (8x8 blocks, like the title), the HUD on top, names and HP
  bars under them (player green, monster red), the group count under the
  monster ("2 MORE GOBLINS"), and the hint line
  "W/A/S/D/SPACE - ATTACK   F - FLEE".
- Sides follow the map: whoever is above or to the right is on the right.
  Attacking from above or from the right puts the player on the right;
  from the left or from below, on the left. The same rule applies when a
  monster attacks first.
- Each hit is a lunge: the attacker jumps one column toward the other and
  back, and the damage ("-5", or "MISS") shows above the target until the
  next hit. Monster hit-backs that do damage get their own lunge.
- Killing the last monster of the group wipes it from the screen, pauses
  for half a second and returns to the map. A group refills the HP bar
  and counts down "n MORE ...".
- Fleeing (F): 50% chance, 75% with Shadowstep (Shadow Hand). Success:
  the monster and its whole group vanish, you lose 10% of your coins (at
  least 1 if you have any; none with Shadowstep) and the turn goes on
  ("YOU FLED! -nGP" / "YOU SLIPPED AWAY!"). Failure: "COULDN'T ESCAPE!",
  the turn is lost and the monster attacks.
- During a battle only attacking, fleeing and the volume keys work
  (I, C and Q wait until the fight is over). Other monsters still move
  and can hit you; only the one you are fighting is shown.
- How it works: the battle screen is the RAM under the KERNAL at $E800
  (59392), shown with POKE 53272,163, and PRINT goes there during the
  fight (POKE 648,232), so the HUD and message code is unchanged. The
  map's colour memory is saved to $EC00 (60416) on the way in and
  restored on the way out, and while the fight is on CB points at the
  saved copy, so anything drawn on the map lands in the right place. The
  screen is blanked for the moment of switching (POKE 53265).
- Machine code (195 bytes at $9500 = 38144, loaded by the loader from its
  DATA at 1010-1130; the top of BASIC is now POKE 56,149):
  SYS 38144 saves the colour memory, SYS 38174 restores it, SYS 38214
  draws one big glyph (POKE 38335 glyph, 38336/38337 screen address,
  38338 colour).
- Game lines: enter 5920-5940, bars and group line 5950-5980, glyph and
  colour 5990-6000, big glyph 6010, player lunge 6020, monster lunge
  6030-6060, monster attack hook 6070-6090, kill 6100, exit 6110, keys
  6120, flee 6130-6160, attack direction 6170. Hooks: 390 (footer waits
  until the fight is over), 1240, 1520 (flee message), 1790, 1880, 2020,
  2080, 2130, 2160, 2770 (game over leaves the battle first), 5790.
- Memory: the game grew by about 2 KB (22964 bytes now) and the demo by
  about 1.6 KB (25176), plus the 256 bytes for the machine code.

## Disk File Names — IMPLEMENTED (V19)
- On the .d64: loader PETSCIIPIT (first file), game GAME, demo DEMO,
  glyph showcase SHOWCASE, music MUSICPAL / MUSICNTSC. The local .bas/.prg
  files keep their names (petsciipitloader, petsciipit, petsciipitdemo,
  glyphshowcase).
- Loader lines 510-530 load GAME / DEMO / SHOWCASE; the game (2910, 3910),
  demo (1730) and showcase (350) load PETSCIIPIT to quit. Their "please
  load first" message (line 20) names PETSCIIPIT.

## Disk Directory Art — IMPLEMENTED (V19)
- Every game disk uses the same directory layout: PETSCIIPIT first (so
  LOAD"*",8 still loads it), then a blank line, the player's standing
  glyph as eight 0-block DEL entries and another blank line, then GAME,
  DEMO, SHOWCASE, MUSICPAL, MUSICNTSC, then "C64.M0N.DE", the chest glyph
  and "M0NDE.ITCH.IO", all as 0-block entries.
- The art is drawn with the CBM-+ checkerboard, two characters per pixel.
- Built by c1541 as before, then a script rewrites the directory from a
  saved template (block counts of the real files come from the new build).
  Don't VALIDATE the disk; it can remove the art entries.

## Titles, Glyph Lore, Keen Eyes 3 and 4 — IMPLEMENTED (V19)
- Titles (TL$(1-5), DATA 5730): ALLEY RAT 50 XP (Keen Eyes 1), BASIC
  BURGLAR 150 (Keen Eyes 2, Nimble Fingers), DELVER OF THE DEPTHS 300
  (Glyph Lore, Keen Eyes 3), SKILLED SKEEVE 500 (Sneak Attack, Keen Eyes
  4), SHADOW HAND 750 (Shadowstep). TT=-(XP>=50)-(XP>=150)-(XP>=300)-
  (XP>=500)-(XP>=750) in 350, 2220, 3610, 6260. Sneak Attack now XP>=500
  (2060); Shadowstep TT>=5 (rest 2610, flee 6130-6140). The title message
  drops "YOU ARE " when it would be longer than 40 (3860).
- Keen Eyes 1 and 2 are unchanged (1300-1360).
- Keen Eyes 3 (XP>=300): room walls coloured by the room: treasury = chest
  colour (8), apothecary = potion colour (5), others unchanged (12); a room
  whose pit has been spotted = dark grey (11). Wall routine 6400-6450
  (room in QR, colour KZ), all revealed rooms 6370-6380, hooks: room
  reveal 1430, redraw 3020, pit spotted 5900 -> 6390. Reaching 300 XP
  shows "I CAN SENSE WHAT THE ROOMS HOLD!" and recolours (2250 -> 6490).
- Keen Eyes 4 (TT>=4): also reveals 4 squares ahead and the squares either
  side 2 ahead, only on map rows 3-23 (1350, 1360 -> 6460-6480).
- Character sheet: one Keen Eyes line with the current level (3750),
  Glyph Lore (3770), Sneak Attack and Shadowstep (3780), LAST RUNE (3790).
- Demo: same titles, Keen Eyes 3 and 4 (wall routine 6890-6940, all rooms
  6860-6870, pit 6880, Keen Eyes 4 6950-6970, message 6980; hooks 1320,
  1330, 1400, 2230, 3980, 6640). No runes or Glyph Lore.

## Descent Runes (Save Codes) — IMPLEMENTED (V19)
- Rune stones: from level 3, one per level in a random room (not on a room
  centre or the hidden pit), placed by 6300-6330 (called from 5140), map
  value MA%=7, drawn by 6340 with screen code 38 (the "&" character,
  redefined by the loader, DATA line 230), white after Keen Eyes. A weapon
  can't drop onto a rune (2170).
- Stepping on one (2360 -> 6350): under 300 XP "A STRANGE RUNE... I CAN'T
  MAKE IT OUT." and it stays; with Glyph Lore the rune is read (6360),
  the stone is used up, "YOU READ THE RUNE: XXXX-XXXX-XXXX" shows and RU$
  keeps it for the character sheet.
- The code: 12 characters (3 groups of 4, from ABCDEFGHJKLMNPQRSTUVWXYZ
  23456789: no 0/O or 1/I) for your stats when you read it. It saves
  level (up to 127), XP (32767), HP (2047), coins (16383), weapon type
  (0-5) and weapon roll (15). Max HP, character level, title and skills are
  worked out again from XP. Resuming starts that level freshly built.
- Packing: three 20-bit groups. Group 1 = level + 128*(weapon + 8*(roll +
  16*check)); group 2 = XP + 32768*(HP/64); group 3 = (HP mod 64) +
  64*coins. Each group is written as 4 base-32 digits, low digit first.
  Every character is scrambled with its position and the character before
  it. The check value is (level*7 + XP*3 + HP*5 + coins*11 + weapon*13 +
  roll*17 + 23) mod 61; about 1 typo in 400 still slips through. Encoding
  6180-6220.
- Loader: title menu R - RESUME THE DESCENT (610, other menu lines moved
  down one row; key at 560). Entry and checking at 1140-1330; DEL rubs
  out, RETURN with nothing typed goes back. A good rune is passed to the
  game in the spare bytes after the battle helper: 38339 = 82 (flag),
  38340 level, 38341/38342 XP, 38343/38344 HP, 38345/38346 coins, 38347
  weapon, 38348 roll. P clears the flag. The loader then loads GAME with
  "DESCENDING TO LEVEL n". The game picks it up at startup (5530 ->
  6240-6260). "IT'S SO DARK!" at the start only shows under 50 XP.
- The demo doesn't use runes.

## Memory Slim-down — IMPLEMENTED (V19)
- Game: the fog map (which squares you've seen) moved out of the FG%
  array into the free 1 KB at $C400 (50176+cell, PEEK/POKE), the way the
  demo already does it. It is cleared with the music player's map clear
  (POKE 781,0:POKE 782,196:SYS 38675) at the level build (4420), and the
  array clear there now does 2 arrays (MA%, RM%). Saves about 2 KB.
- Dead REM lines removed: game 4400-4450, demo 5190-5230 (old FRE(0) and
  array-clearing experiments). The header and table REMs stay.
- The title formula is one subroutine: game 6500 (used by 350, 2220,
  3610, 6260), demo 6990 (350, 2200, 4560).
- Result: game program 24711 bytes with about 5 KB left for strings and
  working space; demo 25613 bytes with about 3.2 KB left.

## Game Parts Linked by a Passage Rune — FUTURE (when memory or speed runs out)
- When the game outgrows BASIC memory or gets too slow, it splits into
  parts: separate programs on the disk (e.g. GAME, then GAME2). Only one
  is in memory at a time, so each part gets the full ~36 KB.
- The shared engine (movement, combat, battle screen, HUD, level
  builder) is copied into each part; what each part saves is its own
  monsters, story text, designed levels and skills.
- Part 1 launches part 2 directly at the end of part 1, passing the state
  and completion flags through the spare bytes after the battle helper
  (38339 onwards), the same way the loader passes a rune to the game. No
  typing needed.
- The rune grows to carry:
  - which part (game program) to go to: the loader reads it and loads the
    right program, so R - RESUME THE DESCENT works for every part.
  - completion flags showing what was done in earlier parts (e.g. boss
    beaten, hidden room found, runes read).
  - Option: 16 characters (a fourth group of 4 = 20 more bits, room for
    the part number and ~16 flags), or a separate "passage rune" just for
    part and flags. Either way checked and scrambled like now.
- A part started from the menu, or a returning player, is asked for the
  rune when it's needed.
- Before splitting: story text and designed levels can live outside BASIC
  (the RAM under the KERNAL, about 4 KB still free there, or loaded from
  disk), which may keep the game in one program for longer.

## License and Instructions — IMPLEMENTED (V21)
- License: CC BY-NC-SA 4.0 (LICENSE file is the full legal code). Others
  may share and adapt with credit, non-commercially, under the same
  license; commercial use needs m0nde's permission. Credits line 760.
- Instructions screen: 910 merges monster coins and treasure, 920 explains
  F - flee, 940 merges potions and stairs, 950 explains runes and R on the
  title. Same number of lines as before, so it still fits the screen.
- Player download for itch.io: petscii-pit-<version>.zip with the .d64,
  README.txt and LICENSE only (not the development files).

## Fast Room Reveal and Instant Menus — IMPLEMENTED (V22)
- Machine code from tools/gfx.asm, installed by the loader (line 380, DATA
  2700-2910) after the SID model check has run, so it can reuse $0720.
  Zero page $57-$5F during the SYS only.
- SYS 1824 FILL ($0720): finds the integer array MA% by name, writes the
  character for every map cell (rows 3-24) to $C000 and sets its colour to
  black. Called once per level after everything is placed (game 5230,
  demo 6020). Character table 2018-2037 (MA% 0-19), weapons 2038-2042
  (WT 1-5), filled at start-up (game 6540-6550, demo 7030-7040).
- SYS 1398 REVEAL ($0576): POKE 1516/1517 start cell, 1518 width, 1519
  height. Sets the fog bytes at $C400 and colours each cell from a
  character -> colour list (characters 1492-1503, colours 1504-1515).
  Anything not in the list (player, monster) keeps its colour. Used for
  rooms (game 1370, demo 1340). The list's colours are set by game 6520-6530
  / demo 7010-7020 at every level start and when Keen Eyes arrives.
- Not changed: corridor reveal (160/180) and the one-off 50 XP recolour
  (4200), because corridor walls and room walls share character 102 and
  have different colours. Could use a look-alike corridor-wall glyph later.
- I and C: the map colours are saved to $A000 (SYS 1541), the page is shown
  on the battle screen at $E800 (53272=163, 648=232), and coming back
  switches to $C000 and copies the colours back (SYS 1575, 25 rows per
  frame). The instructions routine at 1280 now writes to $E800 ($E8-$EB),
  in the loader too (540 shows it with 53272=163). The full map redraw
  (game 2990-3100) is gone. Game 2970/2980/3620, demo 3930/4570/7050.
  The demo's quit prompt still uses its old redraw (3940).
- Fights: the key buffer is cleared when a fight starts (5940), after every
  fight round (2520) and when it ends (6110). Walking keeps type-ahead.
- Red battle wipes (tools/wipe.asm): two new ops, 2 = red blocks (reverse
  space 160 in red on the screen page at 38349) and 3 = copy characters
  (buffer page at 38350) and colours back. The per-cell code moved partly
  to 38144-38188 (the old colour save/restore) and SYS 38356 copies 4
  pages from 38351 to 38352 with the ROMs switched out.
  - Going in (5920-5940): map characters saved to $A800, the map sweeps to
    red in the direction you came from (original speed, 5 rows or 8
    columns per frame), the battle is drawn blanked, its characters saved
    to $AC00, $E800 filled red, then the battle sweeps in over the red.
  - During the fight SB points at $A800 (like CB at $A000), so monsters
    moving or dying update the saved map.
  - Leaving (6110): the map screen is filled red at once, shown, and opens
    from the middle out (shutter, 3 per frame) to the map.
- V23: no red anywhere (border flash gone too). Going in: map saved,
  display blanked (black) while the battle is drawn on $E800 and saved
  ($AC00 characters, $A400 colours), map colours put back, then the battle
  sweeps straight onto the map screen in your direction (5 rows or 8
  columns per frame), and the display switches to $E800 at the end (game
  5920-5940 and 6670, demo 6650-6670 and 7060). Leaving: the battle is
  copied onto the map screen (SYS 38356), shown, and the map opens from
  the middle out over it (shutter, 3 per frame, 6110 / demo 6840). Speeds
  are the fastest for now; to be tuned after testing.
- The sweep always travels from the player toward the monster: when a
  monster starts the fight, its approach direction is flipped (game 6070,
  demo 6800: BH=-EX, BI=-EY).

## Battle Moves and Monster Tells — IMPLEMENTED (V23)
- Each key is a different move. Cursor keys match WASD; SPACE = Hit.
  - D / right / SPACE: Hit, as now.
  - A / left: Jab, always hits, half damage (rounded up).
  - W / up: Heavy, 60% chance to hit, double damage.
  - S / down: Guard, no attack, damage taken this round halved, 25% chance
    of a counter for half damage.
- Tells: after each round, 40% chance the monster shows its next move on
  the empty battle row under the group line:
  - "THE GOLEM WINDS UP...": next hit does double; Guard blocks it
    completely and always counters.
  - "THE IMP IS DARTING AROUND...": Heavy always misses, Hit misses half
    the time, Jab does full damage.
  - "THE CULTIST IS OFF BALANCE!": Heavy always hits, the monster does half
    damage this round.
- Guard and tells apply to all damage taken that round (the monster in
  the fight currently hits twice a round: its counter at 2090 and again in
  the monster loop at 1240).
- Key help: "W HEAVY A JAB D HIT S GUARD F FLEE". Instructions line 920:
  "FIGHT: W HEAVY, A JAB, S GUARD, F FLEE". Demo keeps the plain attack.
- Lines (game): move from the key 6170 (JM 1 hit, 2 jab, 3 heavy, 4
  guard), your damage 6590-6630 (called from 2080; no lunge on a guard
  without a counter), damage-taken factor JG 6640 (used at 2110 and 1240,
  reset to 1 each round at 2520, on a kill 6100 and a flee 6160; flee
  attempts use 6640 with JM=0), tells JT rolled and shown on row 19 at
  6560-6580 after each fight round (2520), key help and fight start
  6660 (from 5940). JG=1 at start-up (5520).

## Priority (decided)
1. Battle wipes (V23): tested, working.
2. Battle Moves and Monster Tells (V23).
3. Two Games: STORY and ENDLESS: steps 1-3 done (V24, waiting for
   testing), step 4 (notes and story features) when we decide.

## Two Games: STORY and ENDLESS — PLANNED (after V23, priority 3)
- Two games loaded from the loader instead of one:
  - STORY: 100 pre-made levels read from disk, all story features (runes
    found on the floor, notes in levels, more later). Ends at level 100
    with an ending screen, then back to the title. No level generation
    code at all (so no random levels after 100).
  - ENDLESS: the current game, randomly generated, endless, no story
    features. Runes come from dying.
- The demo stays on the random engine. Music player, wipes, SID setup and
  charset unchanged.
- Note: the current game has no level limit (it keeps going; runes store
  levels up to 127), so the level 100 ending is new.

### Disk (one disk, all files after MUSICNTSC)
- PETSCIIPIT (loader), STORY, ENDLESS, DEMO, SHOWCASE, MUSICPAL,
  MUSICNTSC, then LEVELS and LEVELIDX, then the existing art.
- LEVELS: all 100 packed levels plus their note text, in one file.
- LEVELIDX: track/sector of each level's blocks (about 2 blocks), loaded
  once when STORY starts.
- Space: about 349 blocks free in V22; second game about 95, levels and
  notes about 150-170, leaving roughly 80-100. Check when built.

### Level data (packed)
- Header (about 40 bytes): room count and each room's x/y/width/height,
  stairs room, hole position or none, rune position or none, note
  position and number or none.
- Map: rows 3-24 as runs, one byte per run (4-bit cell type, 4-bit
  length), about 250-400 bytes. Note text (up to two 38-character lines)
  stored with the level, so story text stays outside BASIC.
- Fixed in the level: walls, corridors, potions, chests, stairs, holes,
  runes, notes.
- Random every time: monsters (type, group size, room and cell), weapon
  drops as now, room names (from the monster types, as now).
- Reading: STORY reads only that level's 2-3 blocks with the drive's
  block-read command (U1), using LEVELIDX. No directory search and no
  100 directory entries. Real 1541 and the Ultimate's 1541 emulation
  support U1; SD2IEC should too (confirm in testing).
- Speed: about 1.5-2 s per level on a stock 1541 (well under a second on
  Ultimate / SD2IEC fast loading), plus about 0.1 s unpacking and
  0.1-0.2 s placing monsters. Faster than generating a level now.

### Level tool: tools/pitlevels.py
- Makes the 100 levels with the game's rules (5-7 rooms, L-shaped
  corridors room to room, potions and chests by level, holes from level
  5) and checks each one can be completed.
- Reads levels.txt for per-level extras (notes, runes, hand-placed items)
  that we decide later.
- Packs each level, checks it fits its blocks, writes LEVELS, then reads
  the built d64 back to make LEVELIDX (run from build_d64.sh).
- Makes a preview page of all 100 maps to review; any level can be
  regenerated.

### STORY game (from the current game)
- Removed: level generation (about 1650-1720, 4460-5230) and random hole
  and rune placement (5850-5880, 6300-6330): roughly 3-4 KB of BASIC freed
  for story features.
- New level start: read the level's blocks into $B000 (RAM under the BASIC
  ROM), BASIC reads the header, one SYS unpacks the map into MA% and RM%,
  monsters placed at random, rooms named, then black fill and first room
  reveal as now.
- Machine code: unpack routine in the RAM under the KERNAL at $EC00. The
  block-read stub needs the KERNAL, so STORY lowers the top of BASIC by one
  page (POKE 56,148) and puts it at $9400 (256 bytes, covered by the space
  saved).
- Notes: a new map cell type. Walking onto one shows its text on a page on
  the $E800 screen (like I and C, so returning is instant).
- Floor runes: where the level puts them. Reading them needs Glyph Lore
  (300 XP) and gives a story rune.
- Level 100: ending screen (text on disk), then back to the title.

### ENDLESS game (the current game)
- Random generation and endless levels as now. Floor runes removed
  (placement and reading).
- Death: game over keeps K, N and S as now and also shows a descent rune
  for the run (level, XP, max HP, coins, weapon, same fields as now).
  Glyph Lore decides whether you can read it: without it the rune shows
  as ????-????-???? with a line saying you can't read it; with it the
  real code shows and R on the title resumes.

### Loader
- Menu: separate lines for STORY and ENDLESS; other keys unchanged.
- R resume works for both: story and endless runes use different
  checksums, so the loader knows which game to load (same 12-character
  format).
- Instructions and credits updated for the two games.

### Order of work
1. pitlevels.py, the LEVELS / LEVELIDX format and the preview page;
   review the maps.
2. STORY game (levels, random monsters, ending), reader and unpack code.
3. ENDLESS changes, loader menu and resume.
4. Notes and other story features, once we decide how to use the levels.
Docs, TESTING.txt, d64 and zips with each step.

## STORY Game, Steps 1-2 — IMPLEMENTED (V24, waiting for testing)
- Level 0 is the tutorial (STORY starts there; dying and K/N restart at
  level 1, so the tutorial is never repeated). Level 0 shows TUTORIAL in
  place of LVL on the HUD (310), on the character sheet (3640), the game
  over screen (2800) and the loading line (4380); the loader says
  ENTERING THE TUTORIAL for P. LEVELS holds records 0-100 plus the ending
  (102 index entries, $9200-$9331), so the reader moved to $9334-$9429
  (SYS 37684 read block, 37687 unpack; 37690/37691 buffer, 37692/37693
  link, 37694/37695 map start; name "LEVELIDX" at $942A). Level 1 is the
  generated level 1 again.
- P and E on the title ask HAVE YE A RUNE? Y/N (row 22, loader 1360):
  Y goes to the rune screen (1150), anything else starts that game. R
  still goes straight to the rune screen. The rune decides which game
  loads (checksum 23 ENDLESS, 29 STORY).
- Tutorial (level 0), 8 rooms: ENTRY WAY, APOTHECARY, TREASURY,
  DORMITORY, GOBLIN ROOM, STUDY, GLYPH LORE CHAMBER, STAIRWAY TO LEVEL 1.
  The GLYPH LORE CHAMBER has a note (READ RUNES TO SAVE YOUR DESCENT /
  THIS ONE NEEDS NO GLYPH LORE) and a rune that can be read without
  Glyph Lore and always gives the code for story level 1 with starting
  stats (6350, 6360 -> 6860), so the tutorial can be skipped. Secret: a
  passage north out of the stairs room ends in a hidden hole that drops
  to level 1. STORY's room arrays now hold 8 rooms (5390-5400). The
  tutorial packs to 756 of the 762 bytes a level can use (3 blocks), so
  longer tutorial text needs a 4-block level (the fog-map buffer holds
  1000 bytes, so that needs a different buffer).
- Step 3, ENDLESS: floor runes removed (placement 6300-6330 and reading
  6350-6360 gone, 2360 and 5140 updated). The game over screen shows a
  descent rune for the run (6300-6310 from 2810): level, XP, full HP,
  coins and weapon, checksum 23 so R / P / E load ENDLESS. Without Glyph
  Lore (300 XP) it shows ????-????-???? and YOU CAN'T READ THE RUNE (and
  LAST RUNE on the character sheet keeps the previous one); with it, the
  code and R ON THE TITLE TAKES YOU BACK HERE. The character sheet's
  Glyph Lore line reads GLYPH LORE - READ YOUR RUNE WHEN YOU DIE.
- Runes in STORY are light green (13) after Keen Eyes (6340 and the
  reveal colour list 1509); dark grey before, as everything else.
- Falling into a hidden hole: the cell shows the hole character (87,
  light grey) as you fall, instead of the player (5820, STORY and
  ENDLESS).
- Music volume at start: the player used to start (and stop) at full
  volume, and the game set the saved volume a moment later, so the music
  jumped down. The player now sets both chips from the saved volumes
  itself (sidtune/player.asm setvol: 38641 music, 38642 effects, each +1;
  0 = the loader's defaults, 3/15 with two SIDs, 9 with one), at start and
  at stop. musicpal.prg and musicntsc.prg rebuilt with build.py; the SYS
  addresses are unchanged.
- Changes from the plan above, decided while building:
  - Level buffer: the fog map at $C400 (normal RAM, so BASIC can PEEK it;
    cleared again after unpacking), not a buffer under the ROMs.
  - STORY lowers the top of BASIC to $9200 (line 30: POKE 56,146), 768
    bytes, not 1.25 KB. $9200-$932E LEVELIDX (loaded at start-up with the
    KERNAL LOAD, 6780-6790, name at $9426), $9330-$9425 the reader.
  - The reader (tools/story.asm, 246 bytes) is installed by the loader
    just before it loads STORY (loader 570 -> 1350, DATA after the gfx
    DATA), so it costs the STORY game no BASIC memory. SYS 37680 reads a
    block from channel 2 (after a U1), SYS 37683 unpacks the map into MA%.
  - Room names can be set per level (levels.txt "name"), stored with the
    level. The tutorial: ENTRY WAY, APOTHECARY, TREASURY, DORMITORY, GOBLIN
    ROOM, STUDY, STAIRWAY TO LEVEL 2.
  - The ending is the last record of LEVELS (levels.txt "ending" lines,
    up to 10): SOMEHOW... / YOU HAVE REACHED THE BOTTOM / OF THE PIT. /
    (blank) / BUT THERE'S MORE TO COME!
  - Source files: petsciipitstory.bas (STORY) and petsciipitendless.bas
    (ENDLESS, the old petsciipit.bas, unchanged apart from the colour list
    addresses). On disk: STORY and ENDLESS; GAME is gone.
- Level format (pitlevels.py): rooms, room types, hidden hole, notes (cell
  and two lines of up to 39), fixed monsters (cell, type, group size), room
  names, then the map runs. Up to 3 blocks a level, up to 8 notes.
- STORY level start: 4460-4650 (read with U1 via 6700-6720, parse the
  header with PEEKs and 6730-6740 for text, unpack, RM% for room interiors,
  clear the fog, monsters, room names), then the fill and first room as
  before. Level 1 is the hand-made tutorial with a fixed goblin; other
  levels put one monster group on a random free floor cell in each middle
  room. Middle rooms with no monster are QUIET ROOM / QUIET TREASURY /
  QUIET APOTHECARY. Removed: corridor walls 1650-1730, generation
  4460-5230, random hole 5850-5880, random rune 6300-6330.
- Notes: map type 8, screen code 167 (Sid's scroll in the loader DATA line
  230 and petscii-pit.pf), light grey before Keen Eyes and white after
  (6770; the reveal colour list is now 13 entries: characters 1492-1504,
  colours 1505-1517, room settings 1518-1521, in all three games).
  Walking onto one shows its two lines (2340 -> 6750-6760); the second
  line clears with the first (1630).
- Story runes use checksum constant 29 (6190; ENDLESS keeps 23). The
  loader's R tries both and loads STORY or ENDLESS (1290, 1320).
- Level 101 = the ending: 4340 jumps to 6800-6830 (from the stairs on 100
  or the hole), shows the text, PRESS ANY KEY, back to the title.
- Loader: P - PLAY THE STORY, E - PLAY THE ENDLESS PIT (menu rows 13-21),
  scroll glyph added (110 reads 22 glyphs).
- Disk: LEVELS (115 blocks) and LEVELIDX after MUSICNTSC; build_d64.sh runs
  pitlevels.py and dirlayout24.bin (the V23 build is build_d64_v23.sh).
  122 blocks free.

## Serpent — IMPLEMENTED (V25, waiting for testing)
- New monster by Sid: SERPENT, glyph 84 / 212 (loader DATA line 190,
  110 now reads 24 glyphs; petscii-pit.pf). Green (5) after Keen Eyes.
  HP bonus 3, attack bonus 2, XP bonus 6, coin bonus 3, hit sound -5.
- Monster types are now 1 leech, 2 goblin, 3 imp, 4 serpent, 5 guard,
  6 cultist, 7 golem (monster table DATA 5620-5630 / demo 6410-6420,
  arrays DIM 7, read loop 0-7). The serpent arrives at level 5 and the
  others keep their levels (imp 4, guard 8, cultist 12, golem 16):
  MW=2+INT(LV/4)-(LV>=5), at most 7 (STORY 3540, 4530; ENDLESS 3540,
  4920; demo 4490, 5710).
- Glyph showcase: 5 per row (DATA 170-230, 14 glyphs): player, floor,
  potion, treasure, stairs / leech, goblin, imp, serpent, guard /
  cultist, golem, rune (light green), note (white); the monsters animate.
- Title screen: the serpent dances after the imp (tools/titlestrips.py
  MON list, strips 1400-1710 now 80 characters a cycle, line 470 wraps
  OF at 80). pitlevels.py: map letter E for a fixed serpent.

## Memory Optimization — IMPLEMENTED (V25, steps 1-2)
- Step 1, crunching: the .prg files are built from the .bas listings by
  tools/crunch.py (run by tools/buildprgs.sh): every space outside quotes
  and every REM text is removed (a REM-only line keeps its number and a
  bare REM). It tokenizes both versions and stops the build if any line
  would mean something different. The .bas listings stay readable.
  Saved about 2.2 KB per program: STORY 25815 -> 23665 bytes, ENDLESS
  25985 -> 23820, demo 26856 -> 24467, loader 21667 -> 19230. Free
  memory while playing: STORY about 11,660 bytes, ENDLESS about 12,280.
- Step 2, merging repeated code (STORY and ENDLESS): the wait loops at
  2570, 3820, 6050 and 6100 use the one at 4310; the key waits at 2900
  and 5910 use 4180; quitting to the title (2910, 3910, and the ending)
  goes through 6830. The game over S line is one PRINT with its colours
  picked by SD (2860; 2870 removed).
- Decided not to do: shorter or moved messages (all the text is about
  1 KB) and wipe presets in machine code (about 200 bytes after crunching,
  and no clean place left for the code).

## V26: Keyboard Stops, Message Colours, Rune Loading Fix — IMPLEMENTED
- Loader: STORY loads failed (?FILE NOT FOUND) when the file name F$, a
  joined string at the top of string memory, sat where 1350 writes the
  level reader ($9334-$9429). 570 now checks F$ first and jumps to 1350,
  which installs the reader and loads "STORY" by a fixed name.
- 6870 (STORY and ENDLESS): waits until no key is held (PEEK(197)=64),
  then clears the buffer. Used by every key wait (4180: I, C, Y/N
  prompts, stairs, game over, quit, weapons, the ending) and by notes
  (6750) and runes (6350/6360). Each new level clears the buffer (5290).
- Rune messages light green (the rune's colour): A STRANGE RUNE... or
  YOU READ THE RUNE: code / WRITE IT DOWN! PRESS C TO SEE IT AGAIN, shown
  like a note (both lines together).
- Notes: light grey before Keen Eyes, light blue (14) after (6770 and the
  reveal colour list 1517); note text is always light blue.
- Glyph showcase shows the note in light blue.

## Monster Battles — MAYBE
- Per-monster quirks: each monster reacts differently to the moves (the
  leech drains you if you guard too long, the golem shrugs off jabs, the
  guard counters heavy strikes). Mostly data, like the MZ% tables.
- Timing strike: a marker sweeps a short bar on the battle screen; press
  at the right moment for a critical hit. Most code, and BASIC timing
  differs between PAL and NTSC.

## Design Rules (decided)
- Story text and designed-level data live outside BASIC: in the RAM under
  the KERNAL or loaded from disk, never as PRINT strings or DATA in the
  game. BASIC only holds the code that shows them.
- The demo skips features that only matter to a human player. It already
  skips runes, Glyph Lore and fleeing. Every new feature is marked "game
  only" or "game and demo" when it is planned.

## Loader Start-up Order — IMPLEMENTED (V20)
- The very first thing the loader does is set a black border and
  background (line 20), so a freshly reset machine's blue screen goes
  straight away. The display is switched off (POKE 53265,11) while the
  loader moves the screen to $C000, checks the SIDs and draws the title
  (360-370); before, the uncleared new screen memory could flash up as
  light-blue garbage.
- Start: the music starts and the title menu is drawn at once (370), then
  the scrolling strips are built (390-450) and the hidden buffer screen
  drawn, then the animation loop starts (470). I and C still return to
  460, which redraws both screens.
- The instructions screen is no longer built at start-up (old line 380).
  It is built with the display switched off (POKE 53265,11), saved to the
  RAM under the KERNAL (SYS 38576) and the "loader has run" signature
  (38654/38655 = 80) set by 1340, called the first time a program is
  launched (570) or I is pressed (540). After that it's never rebuilt.
- The title strips are no longer built from the glyphs at start-up: the
  32 finished rows (4 animation sets x 8 rows, each 70 columns plus the
  first 40 again so it wraps) are string literals at 1400-1710, called by
  410. "~" is PETSCII 255 (pi), which the loader redefines as a solid
  block. BASIC uses literal strings straight from the program text, so
  this takes no time. The rows are generated from the glyph DATA
  (120-230) by a build script; after editing a glyph, the strips have to
  be regenerated to match.

## Battle Screen Transitions — IMPLEMENTED (V20)
- Going into a fight: the border flashes red (53280), the map's colours
  are saved, the map is wiped to black in the direction of the hit (rows
  down or up, columns right or left: the player's DX/DY, or the
  monster's EX/EY when it attacks first; BH/BI, BO/BP), the battle screen
  is drawn with the display off, its colours saved and blacked out, then
  it is wiped in the same way. Leaving: shutter (rows from top and bottom
  to the middle) to black, switch to the map, shutter open from the
  middle out of the saved map colours.
- 5 frames per wipe (5 rows, 8 columns or 3 shutter row-pairs per frame),
  about 0.08 s on PAL; nothing else is slower.
- Machine code (275 bytes) at $0600 (1536), the unused default screen
  memory, installed by the loader from DATA at 1730-1900. Parameters 1536
  kind (0 rows, 1 columns, 2 shutter), 1537 reverse, 1538 0 = to black /
  1 = from buffer, 1539 buffer page, 1540 steps per frame; SYS 1541 saves
  colour memory to the buffer, SYS 1575 runs the wipe. Buffers are in the
  RAM under the BASIC ROM: map colours $A000 (40960, CB during a fight),
  battle colours $A400. The wipe switches only the BASIC ROM out ($01=$36)
  so the KERNAL and the music keep running.
- The old colour save/restore at 38144/38174 and $EC00 are no longer used
  (the big glyph routine at 38214 still is).
- Game lines: enter 5920, 5940, exit 6110, wipe helper 6510, direction
  set in 2020 and 6070. Demo: 6650, 6670, 6840, helper 7000, 2000, 6800.

## SID Choice, Quit, Rune Message, Start Mood — IMPLEMENTED (V20)
- Title menu S - SIDS (key 560 -> 1350-1370, shown by 660): cycles AUTO,
  1, 2; the choice is kept in 38652 (in the music file's spare page, so
  it survives going into a program and back). Changing it stops the
  music, POKEs 38693 (0 = detect at the next start, or 1/2 forced),
  starts it again, re-applies the volumes and, if the instructions screen
  has been saved already, rebuilds it (with the display off until the
  title is redrawn, 460) so its volume line matches.
- Second-SID detection (player.asm, detect): the full check, as before:
  $D420 isn't a mirror of $D400, voice 3 at $D420 is running, and its test
  bit stops it. (A more lenient version without the last check was tried
  in V20 and taken out again.) The S choice 1 or 2 skips detection.
- Title menu Q - QUIT (1380-1390): "QUIT PETSCII PIT? Y/N"; Y stops the
  music and resets the C64 (SYS 64738).
- Menu rows: P 13, R 14, D 15, G 16, I 17, C 18, S 19, Q 20; NTSC/PAL 22,
  web address 23.
- Wrong rune (1330): the message stays for a second, then the key buffer
  is cleared before "PRESS ANY KEY", so a RETURN typed after the 12th
  character can't skip it.
- Music start mood: start reads 38653 (0 = Dungeoneering, 1 = Lamenting).
  The game (5500) and demo (6300) POKE 1 so they begin on Lamenting; the
  loader (370, 1350), showcase (290) and the music-on toggles (game 3130,
  demo 4090) POKE 0.
- The loader blacks out the colour of the screen cells under $0600 before
  installing the wipe code there (260), so its bytes don't show as
  garbage on the start-up screen.
- Battle wipes: moved their zero-page pointers from $FB-$FE to $57-$5A;
  the music IRQ uses $FB/$FC and could corrupt a wipe in progress.

## Two SIDs: Music on $D400, Effects on $D420 — IMPLEMENTED (V20)
- So SID-reactive lights (the Ultimate's follow the first SID) light up
  with the music. Before, two SIDs meant music on $D420 and effects on
  $D400.
- Player: the music voices always use $D400 (sidoff 0, 7, 14); setsid sets
  fxoff = $20 when sids = 2, and the effect routines (fxbegin, stop) set
  up voice 1 of that chip. With two SIDs an effect never takes a music
  voice (fxhold stays 0).
- Game and demo: SI (the effects' SID) is 54272, or 54304 with two SIDs
  (game 5500, demo 6300). Music volume is always POKE 54296 ($D418); the
  effects volume is POKE SI+24 ($D418, or $D438 with two SIDs). On one SID
  both are the same register. Game volume routines 5750-5760; loader 370
  and 1350 set the title volumes the same way.

## SID Model Check (6581 / 8580) — TEST BUILD (V20)
- The loader takes three readings of voice 3 on the chip at $D400 and the
  one at $D420 before it starts the title music (370), and shows them raw
  on row 21 (1950-1960): "#D400 A/B/C   #D420 A/B/C" (the $D420 group only
  with two SIDs). "#" is used because "$" is the treasure chest glyph.
  - A: classic check: test bit on with frequency $FFFF, sawtooth started,
    oscillator read 4 cycles later; the two models read back one step
    apart.
  - B: non-zero readings out of 256 with sawtooth+triangle combined.
  - C: the same with pulse+sawtooth combined (50% pulse).
- First readings on the Ultimate with the B check alone were 3 ($D400) and
  2 ($D420), too close to tell the models apart, hence the extra checks.
  Once known chips have been measured, the one that separates them
  becomes the label (6581 / 8580) and the raw numbers go.
- Machine code: 121 bytes at $0720 (1824), installed by the loader from
  DATA at 2000-2070. POKE 1824 with 0 or 32, SYS 1828, results in
  1825-1827. Kept in 38645-38647 ($D400) and 38648-38650 ($D420).
- Loader lines are now kept under 250 bytes each: BASIC can misbehave
  skipping past the end of a longer line. The REM at 250 was shortened
  and the S line split.

## SID Configuration Screen and Fresh Start — IMPLEMENTED (V20)
- Title menu: "S - SID SETUP (2 SIDS FOUND)" (660) opens the SID
  configuration screen (2100-2200):
  - FOUND: how many SIDs auto-detection found, and the model at each
    address, e.g. "$D400 8580" / "$D420 6581". Model from the sawtooth+triangle check: above 9
    is an 8580 (8580s read 12-14, 6581s 2-6 on the Ultimate).
  - Choices 1-4: AUTO DETECT, ONE SID, TWO SIDS MUSIC ON SID 1, TWO SIDS
    MUSIC ON SID 2. The current one is white with ">".
  - "MUSIC: 8580 $D400" and "SOUND EFFECTS: 6581 $D420" (or "(SHARED)"
    with one SID) show where each goes.
  - Choosing stops the music, clears both chips, starts it again on the
    chosen chip and sets the volumes; RETURN goes back to the menu (and
    rebuilds the stored instructions screen if it has been saved, so its
    volume line matches).
- Kept in the music file's spare page: 38644 SIDs found, 38645-38650
  model test readings, 38651 music chip (1 = $D420), 38652 mode, 38653
  start mood. Volumes for the title (2200): music 3 / effects 15 with two
  SIDs, both 9 with one.
- Player: setsid puts the music on $D400, or $D420 when mchip (38651) is 1
  with two SIDs, and the effects on the other chip (fxoff). Effects only
  borrow a music voice with one SID.
- Game (5500) and demo (6300): SI (effects chip) and VR (music volume
  register) follow the setting; M/E still set music/effects volume.
- The loader's instructions-screen routines moved from 38512/38576 to
  1280/1344 ($0500) to make room in the player's spare page. Game (2970)
  and demo (3930) call 1280.
- Fresh start vs coming back: the game, demo and showcase POKE 38643,82
  just before they load the loader; only then does the loader skip its
  set-up (line 30). Before, it looked at the "loader has run" signature,
  which survives a reset, so after a reset with a new disk it kept the
  old music player and machine code in memory (old music behaviour,
  e.g. Dungeoneering first, loud). Now every fresh RUN reloads the music
  and reinstalls everything.

## Glyph Map and Rule — IMPLEMENTED (V20)
- Rule: never redefine or use as a glyph any screen code from 0 to 63
  (letters, digits, punctuation): text needs them. Text may only use
  those, the reverse space (160, HUD bars and sliders) and the ROM
  checkerboard (102). No other reverse text.
- Screen codes in use (loader glyph DATA 120-230):

  | Code | Glyph | | Code | Glyph |
  |---|---|---|---|---|
  | 128 | player standing | | 83 / 211 | leech, 2 frames |
  | 129, 130 | player walking | | 86 / 214 | guard |
  | 144 | player fighting | | 88 / 216 | goblin |
  | 132 | treasure chest | | 90 / 218 | imp |
  | 158 | potion | | 91 / 219 | cultist |
  | 159 | floor | | 65 / 193 | golem |
  | 190 | stairs | | 94 | solid block (title strips, "~") |
  | 166 | rune | | 102 | wall (ROM checkerboard) |
  | | | | 87 | hole (ROM) |

  Weapons use the ROM characters / = < * % (47, 61, 60, 42, 37), not
  redefined.
- petscii-pit.pf: the whole character set exactly as the loader builds it
  (raw 2048 bytes, screen-code order, no header: ROM uppercase/graphics
  set + the glyph DATA + solid block at 94), for PETSCII editors. Kept in
  the repo, regenerated whenever the glyph DATA changes, and included in
  every full zip.
- Moved in V20 from the text range: player 0 -> 128, fighting 128 -> 144,
  treasure 36 -> 132, potion 30 -> 158, floor 31 -> 159, stairs 62 -> 190,
  rune 38 -> 166. Game constants 5480-5490 (FC, XC, PC, PT, TS), player
  frames 2080, 4370, 5910, big battle glyph 5990, rune 6340; demo 2060,
  3570, 5160, 6280-6290, 6720; showcase DATA 170-270 and 460; title strips
  regenerated.

## SID Screen: Volumes, Song and Sound FX Tests — IMPLEMENTED (V20)
- The screen is cleared and drawn in full only when it opens (2110). After
  that each key redraws just its part, with the cursor placed by 2600:
  volume bars (2430), song name (2160), sound fx name (2180); a new mode
  redraws the found/model lines (2120), the choices (2130) and the music
  and sound fx lines (2140) without clearing the screen.
- Bottom of the SID configuration screen (draw 2110-2200, keys 2240-2380):

      MUSIC    - 8580 $D400 [volume bar]
                 DUNGEONEERING
      SOUND FX - 6581 $D420 [volume bar]
                 BUMP

  The volume bars are drawn like the game's (2420): reversed blocks for
  the level, the checkerboard for the rest, steps off/3/6/9/12/15.
- Keys, in neighbouring pairs and rows on the keyboard: M next song
  (Dungeoneering, Assailing, Lamenting); C / V music volume down / up;
  D / F sound fx volume down / up (steps of 3, stopping at 0 and 15; with
  one SID both pairs move the shared volume); E play the sound effect, R
  play it over and over until a key is pressed, T next sound effect (bump,
  hit, step, kill, stairs, game over, potion, treasure; copies of the
  game's effects at 2500-2580); 1-4 mode; RETURN back. Key handling
  2240-2470.
- The volumes carry into the game and demo: kept in 38641 (music) and
  38642 (sound fx), stored +1 so 0 means "not set yet". Defaults (2400):
  music 3 and effects 15 with two SIDs, 9 with one. Choosing a mode resets
  them to that mode's defaults. The game (5500) and demo (6300) start at
  these volumes, and the game's M, E and V write their changes back
  (5750-5770), so the loader shows them on return.
