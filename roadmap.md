# PETSCII Pit — Game Plan / Roadmap

Future features and mechanics for the game. Nothing here is implemented yet —
this is a planning reference for when we're ready to build each piece.

## Win Condition
- Reaching Shadow Hand is required to win the game.
- A specific dungeon level (not yet decided which) requires the player to
  modify the game itself in order to exit — a meta win condition.
- Guaranteed hints appear at certain dungeon levels (not yet decided which),
  but their placement within the level is random each time.

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

## Softer Death, Starting at Level 5
- Starting at dungeon level 5, dying and choosing to keep XP no longer
  sends you all the way back to level 1 — instead you resume one level
  below where you died, keeping the same XP (die on level 5, resume on
  level 4).
- You do not keep your weapon on this kind of death.
- This is a new, separate option on the death screen (not a change to the
  existing K or N choices), available only once you've died at dungeon
  level 5 or deeper. "K - KEEP XP AND TRY AGAIN" and "N - NEW GAME FROM
  ZERO" behave exactly as they do today regardless of depth; this is a
  third choice that only appears when eligible.

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

## Dungeon Density
- Maps should feel slightly more dense than they currently do — more
  packed with rooms/corridors relative to the available space. Only a
  small increase, not a major overhaul of generation.

## Remaining Backward-GOSUB Speed Fixes
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
- Also found, lower priority (less frequently called, not yet
  investigated in detail): a handful of smaller backward-call cases
  still remained in the last full sweep, roughly matching the
  subroutines that begin near "T2=TI+240" (part of `@REST`), a
  `FOR C9=-1 TO 0` polling block reused via GOSUB from several menu
  screens, and `@MONSTERSTEP`'s loop start. Worth a fresh sweep to
  re-locate these precisely before fixing, since moving other
  subroutines shifts everything after them.

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

## Split Keen Eyes Into Two Levels
- Currently Keen Eyes is a single skill, granted all at once at Alley
  Rat: the base 6-square ring around you, plus seeing 1 extra tile
  straight ahead in your direction of travel.
- Planned change: split this into two tiers.
  - "Keen Eyes (Level 1)" — granted at Alley Rat (as now, XP 50) — just
    the base 6 squares around you, no forward extension.
  - "Keen Eyes (Level 2)" — granted at Basic Burglar (XP 150), in
    addition to that title's existing Nimble Fingers skill, not
    replacing it — adds seeing 2 tiles ahead in your direction of
    travel instead of 1, while keeping the same 6-square ring from
    Level 1.

## Confirm Before Descending Stairs
- Currently, stepping onto the stairs tile immediately triggers
  descent (with the existing "STAIRS FOUND! DESCENDING..." message and
  pause) — no way to back out.
- Planned change: stepping onto stairs should instead ask whether you
  want to descend, rather than descending automatically. Reasoning:
  rooms can have more to them than just the stairs (other doors/exits
  to explore), and a player might want to keep exploring the level
  before heading down.
- Open questions for when we build this: if you decline, do you just
  stand on the stairs tile normally (free to walk off), and does
  stepping onto it again later re-ask, or only ask once per visit?

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
