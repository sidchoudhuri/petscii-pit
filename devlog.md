# PETSCII Pit — Dev Log

## First Release
- Procedurally generated dungeon each run, revealed as you explore
- WASD or cursor key movement
- Bump into monsters to fight them
- Find the stairs to descend to a new level
- Sound effects with a mute toggle (M)
- Early bug fixes: doorways that didn't connect rooms, dungeons repeating between runs, occasional rendering glitches

## HUD Update
- Added a HUD showing Health, XP, Dungeon Level, and Coins (coins are a placeholder for a future treasure feature)
- Health now starts at 10
- Fighting a monster now costs you 0-3 health per hit, on top of the damage you deal
- Defeating a monster grants XP
- Added an instructions screen — press I anytime to bring it up

## Current Update
- Added a message line under the HUD that summarizes each turn (hits, kills, damage taken, sound toggle)
- Health potions now appear in the dungeon — walk into one to heal
- Health regenerates slowly over time even without potions
- Reaching the stairs heals you for a portion of your max health
- Every 50 XP raises your max health by 5
- Death screen now offers a choice: keep your XP and try again, or start fresh
- HUD colors improved — labels in grey, values in white
- Finding the stairs now shows a message and a short pause before you descend
- Fixed a bug where a room or the monster in it could appear before being fully drawn

## Latest Update
- Monsters now drop 1-5 coins when defeated
- Treasure now appears in the dungeon — more of it the deeper you go — worth 5-20 coins
- Fixed a bug where a potion's healing wasn't reflected on the HUD until your next action
- Fixed damage messages sometimes overstating how much health you actually lost
- Space now lets you rest for 10 turns instead of just waiting one — heals 3-5 health, but nearby monsters still get to act, so resting isn't risk-free
- Walking into a wall now shows a message: "CRASH! YOU BUMPED INTO A WALL"
- Dungeon generation, the death screen, and the instructions screen all clear much faster than before

## Thief Titles Update
- Monsters now scale with dungeon level — tougher and hit harder the deeper you go
- New: earn thief titles as you gain XP, each with a permanent skill that stacks with the ones before it:
  - **Alley Rat** — Keen Eyes: see more of your surroundings as you move
  - **Basic Burglar** — Nimble Fingers: take less counter-damage when you attack
  - **Skilled Skeeve** — Sneak Attack: bonus damage on your first hit against a monster
  - **Shadow Hand** — Shadowstep: immune to ambushes while resting
- Your current title is shown in the corner of the screen, and earning a new one is announced in the message line
- New: press C anytime to view your character sheet — title, level, health, XP, coins, and skills earned
- Resting now carries a small risk of a monster ambushing you, more likely the deeper you are (rare, capped, and Shadow Hand makes you immune)
- The instructions screen redraws faster
- Fixed a bug where potions could sometimes render as the wrong symbol
- Fixed a rare display glitch on the instructions screen

## Monster Variety Update
- 6 distinct monster types, each with its own glyph, color, and difficulty on top of the existing per-level scaling: Leech, Goblin, Imp, Guard, Cultist, Golem
- Tougher types unlock gradually with depth — early levels only spawn the easier ones, with the full roster available by level 16
- XP and coin rewards now scale by monster type instead of being flat across all monsters
- Combat messages now name which monster you fought and the actual reward, e.g. "KILLED CULTIST +18XP +9GP -TOOK 5DMG"
- Each monster type has its own hit/death sound pitch

## Screen & Performance Improvements
- Room placement now uses nearly the entire available screen instead of leaving several columns and rows unused around the edges
- The instructions screen (I key) now only redraws the portion of the dungeon you've actually explored, instead of always rescanning the whole map
- Several other under-the-hood speed fixes to dungeon generation and screen clearing

## Weapons Update
- Weapons now appear in the dungeon starting at level 2, once you've reached the Alley Rat title
- Five weapon types, each with its own attack bonus and perk: Dagger (small dodge chance), Sword (straightforward extra damage), Blade (bonus damage on your first hit), Mace (reduces counter-damage), Flail (bigger dodge chance)
- Walk into a weapon to equip it — or, if you're already carrying one, see a side-by-side comparison before deciding whether to swap
- Your character sheet (C) now shows your equipped weapon
- Instructions screen updated to mention weapon drops

## Refinements
- Fixed a bug where earning a new thief title could sit unannounced until you took another action — the announcement now appears on its own after a short pause
- Keen Eyes now reveals one extra tile straight ahead in whichever direction you're moving, on top of its existing view
- Added a blank row of spacing between the bottom of the dungeon and the text in the corner, matching the buffer already at the top of the screen
- General polish to the instructions screen, including a corrected web address

## Balance & Polish
- Weapon drop chance more than doubled (8% → 20% per eligible kill) — you shouldn't have to wait nearly as long for your first one
- Bumping into a wall before you've earned Keen Eyes now says "CRASH! IT'S TOO DARK TO SEE!" instead of "CRASH! YOU BUMPED INTO A WALL"
- Resting now just says "RESTING..." instead of "RESTING FOR 10 TURNS..." — same duration and healing as before, just a shorter message

## Room Names Update
- Certain rooms now display a name in the bottom-left corner, mirroring your title badge in the bottom-right
- The room you start in each level is named "LEVEL X ENTRYWAY"; the room with the stairs down is "STAIRS TO LEVEL X"
- Other rooms are named after what's inside, by priority: a room with treasure is "[MONSTER] TREASURY", a room with only potions and no treasure is "[MONSTER] APOTHECARY", otherwise just "[MONSTER] ROOM"
- Once you defeat that room's monster, its name gains a "(CLEARED)" tag
- Two separate corridors that happen to run right alongside each other are now called out as a "GRAND HALLWAY" while you're standing in one
- The "DESCENDING TO LEVEL X, PLEASE WAIT..." screen is now a clean, blank loading screen matching the style of the death screen, rather than showing stray leftover text

## Performance Improvements
- Fixed a real bug where the game got progressively slower the longer you played in one sitting — a fresh memory cleanup now runs on every level transition instead of letting it build up all session
- The room name, title badge, and turn-summary message line all redraw substantially faster than before
- Movement should feel noticeably snappier — fixed the room name/title corner being recalculated on every single step instead of only when you actually changed rooms
- Fixed a deeper issue causing "press any key" screens (title screen, and general keypress handling) to respond unexpectedly slowly as the game grew larger — this should also make ordinary movement input feel more responsive
- Fixed the same underlying issue for the main gameplay loop itself, which is re-entered after literally every turn — this was the single biggest remaining source of that kind of slowdown
- Fixed a rare bug where certain room names could cause the screen to scroll and throw off the whole layout

## Additional Performance & Bug Fixes
- Fixed a real crash: finding a second weapon while already carrying one could throw a syntax error and stop the game — a variable name happened to collide with a reserved BASIC keyword. If you ever hit an error picking up a weapon, this was it.
- Cleaned up redundant calculations in monster movement and the corridor/hallway-detection check so each value is computed once per use instead of repeatedly
- Several more of the game's most frequently-used internal routines repositioned for faster lookup, extending the same fix used for the message line and HUD in the update above
