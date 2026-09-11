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
  - Heart (green) — baseline difficulty
  - Club (yellow)
  - Diamond (orange)
  - X-in-box (light red)
  - Cross (red)
  - Solid Block (purple) — toughest
- Monster type is chosen randomly (uniform across all 6) each time a
  monster spawns, including ambush spawns during rest.
- Still to come later: monster types with genuinely different behavior
  (e.g. a stationary wall-mimic, a ranged elemental) — these need their
  own AI branching rather than sharing `@MONSTERSTEP`, and were
  deliberately deferred as a separate, larger piece of work.

## Weapon Pickups — IMPLEMENTED
- Starting at dungeon level 2, and only once the player has reached Alley
  Rat, monster kills have a flat 8% chance to drop a weapon on the tile
  where the monster died.
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

## Room Names
- Certain rooms get a name, displayed bottom-left (mirroring the
  existing title badge, which sits bottom-right).
- Normal rooms have no name.
- The stairs room is named "STAIRS LEVEL X" (X = the current dungeon
  level).
- A corridor that's 2 spaces wide is called "GRAND HALLWAY".
- More named room types still to be decided.
- Dependency to note for later: dungeon generation currently only ever
  produces 1-cell-wide corridors, so the "GRAND HALLWAY" naming implies
  variable-width corridors need to exist first (or at least occasionally
  be generated) before this name would ever actually appear.

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
