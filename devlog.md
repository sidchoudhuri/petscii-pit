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
