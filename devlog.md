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
- Fixed the same kind of slowdown for the "press a key" waiting routine, which is used constantly across stairs, the quit prompt, and weapon pickups — should feel noticeably snappier at those points now

## New Feature: Softer Death at Level 5+
- Dying at dungeon level 5 or deeper, after having reached at least the Alley Rat title, now offers a new option on the death screen: press S to resume one level below where you died, keeping your current XP and weapon
- This option always shows on the death screen, every time you die — it's only greyed out and unselectable until you've met both requirements at once (reached level 5, and reached Alley Rat), so you always know it's there and what it takes to unlock it, no matter how far along you are

## Healing & Ambush Rebalance
- Found and fixed a real balance problem: your max HP grows without any limit as you earn XP, and healing between levels used to scale directly off that ever-growing number — the two together meant the game was quietly getting *safer* the longer you played, not more dangerous, regardless of how deep you went
- Healing when you descend to a new level is now a flat 10% of your max HP instead of a random 33-50% chunk of it
- Resting and drinking potions now heal a small flat 3-5 HP while your max HP is still low (under 30), then shift to a random 10-20% of your max HP once it grows past that
- Resting more than 3 times on the same level now warns you it's risky and asks you to confirm before you can keep going, and the chance of getting ambushed while resting climbs steeply each time past that point
- Reaching Shadow Hand no longer makes you fully immune to ambushes while resting — it now gives you a small 3-5% chance instead, so it's still much safer than earlier titles but no longer risk-free

## Keen Eyes Split Into Two Tiers
- Keen Eyes is no longer a single skill you get all at once — it's now two named tiers, matching the two titles you already earn along the way: Keen Eyes (1) at Alley Rat gives you the usual awareness of the 6 squares around you, and Keen Eyes (2) at Basic Burglar adds seeing 2 tiles ahead in the direction you're walking, instead of the 1 it used to give
- The character screen now lists both as their own separate skills

## Corridors Now Have Walls
- Corridors used to be a bare path through empty black space with nothing marking their edges — they now have real walls on either side, including properly closed corners at bends
- Fixed a real bug found while building this: the walls were being placed correctly, but the game's own reveal logic never actually showed them to you — only the exact tile you were standing on ever got revealed, so the walls next to you stayed invisible even though they existed. Fixed so walls now reveal properly as you walk, including through Keen Eyes' wider vision
- Room walls and corridor walls now look different once you've earned it: before reaching Alley Rat, both are dark grey and you can't tell them apart; after Alley Rat, room walls turn light grey while corridor walls stay dark. The moment you reach Alley Rat, every wall you've already seen updates immediately, not just new ones you find afterward

## New Feature: The Dungeon Starts Dark
- Before reaching Alley Rat, the whole dungeon is now genuinely hard to see: floor, walls, monsters, potions, treasure, stairs, and weapons on the ground all render in a single dark grey instead of their normal colors, since your character hasn't yet learned to make out detail down there
- A random ambient message, "IT'S SO DARK!", now has a small chance (1 in 10) of showing up on an otherwise quiet turn where nothing else happened, as a reminder of why everything looks the way it does
- Fighting a monster while still in the dark has a good chance (1 in 2) of showing "I COULD HARDLY SEE THAT THING!" instead of the normal kill/hit message that turn
- Added a line to the instructions screen explaining this up front, so it reads as an intentional mechanic rather than a bug: "DUNGEON IS DARK UNTIL KEEN EYES AT 50XP"
- The first time you actually reach Alley Rat (Keen Eyes 1), the game now says "MY EYES HAVE ADJUSTED!", pauses for a second, and then all the room walls light up to their proper color
- Reaching Basic Burglar (Keen Eyes 2) now says "I CAN PICK OUT MORE DETAILS!" with the same second-long pause, ahead of a future perk planned for that tier
- Found and fixed a real oversight along the way: weapons sitting on the dungeon floor were still showing their normal color the whole time, regardless of how dark everything else was — these are now dark grey too until Alley Rat, matching everything else

## Color Correction: Three Shades of Grey, Not Two
- Realized partway through that the C64 actually has three distinct grey shades (light, medium, and dark), not two, and the earlier work had been treating "light grey" and "medium grey" as the same color
- Your character is now cyan once you reach Alley Rat, instead of reusing the same light grey that was already being used elsewhere
- Room walls now turn medium grey after Alley Rat rather than light grey, so they read as visually distinct from other light-grey elements like the HUD text
- Confirmed the dungeon floor was already correctly dark grey both before and after Alley Rat, with no change needed there

## Performance & Memory Update
- With the help of Eyvind Ebsen, the font used for all on-screen characters now loads with a single fast block-copy instruction instead of copying it one character at a time — the game starts up noticeably quicker
- The three big dungeon-tracking arrays switched to a more memory-efficient number type, freeing up space for future features
- Replaced a risky trick used to quickly clear those arrays between levels (one that could break certain ways of packaging the game) with a safer approach that works everywhere

## Bug Fix: Monsters Invisible in the Dark
- Fixed a real bug where monsters (and in some cases the stairs) could fail to actually appear on screen while you were still exploring in the dark, before reaching Alley Rat — fog-of-war and the "it's dark" mechanic itself were both working as intended; the monster just never got drawn
- This did not affect the normal full-vision view after Alley Rat, which was already working correctly

## Custom Monster & Dungeon Art
- With the help of Ricky Derocher, learned to create custom character sets.
- Hand-drawn custom glyphs in place of the stock character shapes for: potions, treasure/coins, the Golem, the Leech, the Goblin, the Guard, the Imp, the Cultist, and the stairs down
- The Golem now uses a dedicated character slot instead of sharing one with a generic solid block, so it has its own distinct look

## Music: "Dungeoneering"
- PETSCII Pit now has background music: "Dungeoneering", an original 3-voice SID tune written for the game, with drums, a bouncing octave bass, and a lead melody that switches to a shimmering arpeggio in its middle section
- The music loads from disk automatically when the game starts, so launching is still just LOAD"PETSCIIPIT",8 and RUN
- It starts once the first level has been built and plays on its own raster interrupt, so it keeps a steady tempo no matter what the game is doing, without changing the game's own timing
- Mixed quietly underneath the game so sound effects stay easy to hear
- Sound effects and music share the SID's first voice: the music steps aside while an effect plays and picks that voice back up on its next note
- New keys: M now toggles the music, and E toggles sound effects (M used to be the sound mute). The instructions screen lists both
- The music is stopped cleanly when you quit back to BASIC

## Faster Level Generation
- Clearing the dungeon between levels is now handled by a tiny machine-code helper bundled with the music, instead of a BASIC loop over thousands of cells, so it's practically instant
- Corridor walls are now placed while the corridors are being dug, instead of in a separate full-screen scan afterwards
- Treasure rooms and apothecaries are now recorded as their contents are placed, instead of rescanning every room tile by tile afterwards
- The dungeons themselves are unchanged, just built faster: checked against 5,000 sample dungeons, and every one came out identical to the old generator

## Fight Music: "Assailing"
- The music data was reorganized into short reusable patterns, so two songs now fit in less memory than the single song used to take (2K instead of nearly 3K), giving 1K back to the game
- New: a short, scary fight theme called "Assailing", with a heartbeat kick drum, a grinding bass, and an eerie sinking chord
- It plays whenever a living monster is in the room with you, or while you're fighting one, even from a corridor or doorway
- When that monster dies or you leave the room, "Dungeoneering" comes back exactly where it left off instead of starting over
- The fight music kicks in as you step into the room or swing at a monster, before the monster gets to act
- Descending to a new level always brings back the dungeon music
- With the music off (M), switching songs happens silently; turning the music back on mid-fight starts the fight theme straight away

## Bug Fixes
- Hammering keys during a fight no longer sends you running off once the monster dies: the keyboard buffer is now cleared the moment a kill is finished, the same way it is when you bump into a wall
- Fixed your character vanishing while fighting from a doorway: attacking into a room you hadn't seen yet redrew the whole room, including the doorway you were standing in, and you stayed invisible until you moved again
- When your eyes adjust at Alley Rat, everything you've already seen now lights up to its proper color (potions, treasure, stairs, weapons on the floor, monsters, and your own character), not just the walls

## Redrawn Characters: Chest, Golem, Goblin, Imp
- New hand-drawn designs for four characters:
  - **Treasure chest**: a fuller chest with a lid and a lock
  - **Golem**: bulkier, with raised fists, and now facing left
  - **Goblin**: now facing the other way, with a new arm pose
  - **Imp**: horns up top and arms spread wide

## PAL and NTSC, Quieter Moments, and a Loading Animation
- The game now detects whether it's running on a PAL or NTSC machine and
  loads the matching music. On NTSC, both songs used to play too fast;
  the NTSC version is retuned and re-timed so they sound the same as on PAL.
- The instructions screen shows which machine type was detected, e.g.
  "PAL - PRESS ANY KEY TO CONTINUE".
- HP on the HUD now shows current and max health, e.g. HP:15/30.
- Music now starts while the first level is being built, and plays on
  every "PLEASE WAIT ..." screen.
- Once a level is ready, the music waits silently until you take your
  first step, then picks up where it left off.
- Resting goes quiet too, and the music returns when you start moving.
- When a fight ends, the fight music stops right away (even before
  "MY EYES HAVE ADJUSTED!"), and the dungeon music comes back on your
  next step.
- The "PLEASE WAIT ..." dots now animate, cycling from white through the
  greys, left to right, while each level is built.
- The startup message "BUILDING THE DUNGEON, PLEASE WAIT ..." now appears
  straight away, while the music is still loading from disk.
- The glyph showcase on the disk now plays both songs: SPACE switches
  tracks, Q quits, and it shows what's playing.

## Third Song: "Lamenting"
- New: "Lamenting", a slow, sad, sparse echo of Dungeoneering's opening
  melody over long bass notes, with a single soft thud each bar.
- The dungeon music now has a mood: Lamenting plays while the dungeon is
  still dark (before Alley Rat) and whenever you're near death (HP below
  a quarter of your max); Dungeoneering plays the rest of the time.
- Each one remembers where it was, so switching moods picks the other
  song back up where it left off. Fights still switch to "Assailing" and
  return to whichever mood fits afterwards.
- The glyph showcase now cycles through all three songs with SPACE.

## Optimization: Glyph Setup as DATA
- The 11 custom glyphs (player, floor, potion, chest, stairs and the six
  monsters) are now stored as one DATA line each — screen code followed
  by the 8 bitmap bytes, with the glyph's name in a REM — and written into
  the font by a short READ loop, replacing 88 individual POKEs.
- Same glyphs, byte for byte; the program is about 530 bytes smaller.
- The glyph showcase uses the same table, placed ahead of its own grid
  layout DATA so both read in order.

## Optimization: Integer Arrays
- The room and monster tables (room position/size/type/revealed, monster
  position/health/attack/type/alive) are now integer arrays, taking 2
  bytes per entry instead of 5. About 200 bytes more free memory once the
  game is running; no change to how anything plays.

## Optimization: Fewer IFs
- Drawing a revealed square is much quicker: the game reads the square
  once and jumps straight to the right drawing line instead of checking
  up to 12 possibilities one by one.
- Monster and weapon stats and thief titles come from small tables loaded
  once at startup instead of chains of IFs.
- Keen Eyes works out which squares to reveal in a few lines instead of
  about 40, every step.
- Program about 1.5KB smaller. Everything looks and plays the same.

## Optimization: Instant HUD
- The HUD at the top is now printed in one go instead of being written
  one character at a time, and only when HP, XP, level or coins actually
  change — most turns it costs almost nothing.
- The message lines under it are printed the same way, and only when the
  message changes.

## Optimization: Hot Routines First
- The routines the game uses most (drawing squares, revealing rooms and
  walls, the HUD and messages, monster movement, sound effects, music
  checks) now sit at the top of the program, where BASIC finds them
  fastest. A plain move does less than half the line-searching it used
  to, and room reveals and monster turns are much quicker.
- The program is renumbered in steps of 10; it plays exactly the same.

## Wording
- The ambush message now reads "A MONSTER AMBUSHED YOU!"

## Second SID Support
- If your C64 has a second SID chip at $D420 (Ultimate 64 / C64 Ultimate,
  or VICE with an extra SID set to $D420), the game now finds it at
  startup and plays the music on it, while the sound effects keep the
  first chip to themselves.
- The music is now always the full, original version, the same as the
  .sid files, instead of the turned-down mix that clicked on every note.
- With only one SID, the music and sound effects share the chip at the
  same volume, and the sound effects still borrow one music voice while
  they play.
- The music now starts on the first instructions screen, which shows
  "PAL 2SID" or "NTSC 2SID" at the bottom when a second SID is found.
- Volume steps 0, 3, 6, 9, 12, 15 and wraps back to 0 (0 = mute), shown
  under the HUD as a slider of solid and checkered blocks.
- One SID: M and E still mute music or sound effects on their own, and
  the new V key sets the volume for both together. Starts at 9.
- Two SIDs: separate volumes. M steps the music (starts at 3), E steps
  the sound effects (starts at 15).
- Glyph showcase: new V key steps the music volume 0, 3, 6, 9, 12, 15
  and back to 0, shown as the same slider on the bottom row. Music
  starts at 15. Key line now reads "SPACE - NEXT TRACK V - VOLUME  Q -
  QUIT".
- Demo only: the self-playing AI now reads the level layout and finds
  doors and corridors (see devlogdemo.md). No change to the game.
- Faster "MY EYES HAVE ADJUSTED!": the recolor only checks the rows you've
  explored instead of the whole screen.

## Harder Monsters, Groups, Levels, Weapons and Pits
- Monsters get much tougher as you go deeper, and hit back according to
  how strong they are. Worked out with a 30-level simulation so the game
  keeps getting harder instead of easier.
- From level 3 a monster can be a group: kill one and "ANOTHER GOBLIN!"
  steps up, up to 5 deep. Coins for every one; XP full, then half, then
  a quarter.
- Character levels now get further apart (50, 150, 300, 500, 750 XP...),
  and each level up raises max HP more than the last. The character
  sheet shows the XP needed for the next level. Shadow Hand is now at
  750 XP.
- Dropped weapons roll a random attack bonus that grows with depth.
- Pits: from level 5 a level may hide a hole in the floor. With Keen
  Eyes you might spot it; otherwise "AAAAH! YOU FELL INTO A PIT!" and
  you drop to the next level, hurt, with Lamenting playing until you
  move.

## Version Numbers and Two-SID Key Line
- Builds now have version numbers, starting at 12. The version is the
  disk ID of the .d64 (titled PETSCII PIT) and shows on the top line of
  the instructions screen, e.g. "PETSCII PIT V12".
- With two SIDs the instructions key line reads
  "VOLUME  M - MUSIC  E - SOUND EFFECTS".

## Version 13: Animated Characters
- The player and every monster now animate with Sid's new frames:
  monsters flip between two poses when they move or fight, the player
  takes walking steps, swings when attacking, and settles back to
  standing a moment after you stop.
- The glyph showcase animates them too.

## Version 14
- Demo speed-up (see devlogdemo.md). The game itself only changes its
  version number.

## Version 15: Loader and Title Screen
- New loader, first on the disk: LOAD"*",8 and RUN. It loads the music,
  the font and the glyphs once, then shows a title screen with the player
  and monsters blown up big, dancing and scrolling, and a menu: play,
  demo, glyph showcase, instructions and credits.
- The game and demo start straight at "DESCENDING TO LEVEL 1" with the
  music already playing; quitting returns to the title menu.
- The instructions screen is stored once by the loader and pops up
  instantly with I, in the menu and in the game.
- About 2.5 KB of BASIC memory freed in the game for future features.

## Version 16: Credits
- Credits screen text: design, code and graphics by m0nde; music
  (PETSCII Pit - Dungeoneering, Assailing, Lamenting) by m0nde; thanks to
  Ricky Derocher, Eyvind Ebsen and Bobby Brightling; the itch.io page;
  (C)2026 m0nde - CC BY 4.0.

## Version 17: Music Hand-off
- The loader stops the music before it loads the game, demo or showcase;
  each program starts it again itself (the game and demo on the way down
  to level 1, the showcase on its screen).

## Version 18: Fix Returning From the Glyph Showcase
- Quitting the glyph showcase loaded the loader but stopped with
  ?UNDEF'D STATEMENT ERROR IN 500. The showcase is shorter than the
  loader, and BASIC keeps the old end-of-program pointer when one program
  loads another, so the loader's variables were written over its own
  code. The loader now resets that pointer when it is loaded from another
  program (line 30), the same way the game, demo and showcase do.
- Title screen: the big player now cycles through all four of his frames
  (stand, walk, walk, fight) while the monsters keep alternating their
  two, and the scroll moves two columns per step for about twice the
  speed (still all BASIC PRINTs, colour codes now inside the PRINT).
- Quitting the game, demo or glyph showcase now stops the music before
  loading the loader, so it no longer glitches during the disk load.
- Loading from the title menu now looks seamless: for the game and demo
  the loader shows the same "DESCENDING TO LEVEL 1, PLEASE WAIT ..." the
  game shows, with the three dots in the cycling colours (standing still
  while the disk loads); the game then takes over the same screen, starts
  the dot cycling and the music. The glyph showcase gets "LOADING GLYPH
  SHOWCASE ..." the same way.
- The game and demo keep the loader's screen up while they start, instead
  of clearing it, so the hand-off to "DESCENDING TO LEVEL 1" is seamless.
- The title animation is now double-buffered: each step is printed on a
  hidden second screen and then shown all at once, so the big glyphs no
  longer redraw visibly from top to bottom. Still all BASIC.
- Instructions screen recoloured in the credits' style: keys and actions
  in white, a dark grey dash, descriptions in light grey; the tips are
  all light grey with a blank line separating them from the controls.
- Each instruction tip now has its key word in white (STAIRS, MONSTERS,
  TREASURE, HEALTH, POTIONS, LEVEL UPS, XP, WEAPONS, EQUIP).

## Version 19: Battle Screen
- Every fight now happens on its own battle screen: you and the monster
  drawn big, side by side, with the HUD on top, names and HP bars under
  you both, and "2 MORE GOBLINS" when there's a group behind it.
- Sides follow the map: if you're above the monster or to its right,
  you're on the right; otherwise you're on the left.
- Each hit is a lunge toward the other fighter, with the damage shown
  above whoever took it ("MISS" if nothing got through).
- New: F - FLEE. A coin flip (better odds with Shadowstep). Get away and
  the monster and its group are gone, but you drop 10% of your coins
  (none with Shadowstep). Fail and you lose your turn while it hits you.
- Beat the last monster and you're back on the map.
- Switching screens is instant: the battle screen is kept in spare memory
  and a small machine code helper (installed by the loader) saves and
  restores the map's colours and draws the big glyphs.
- New file names on the disk: the loader is PETSCIIPIT, the game GAME,
  the demo DEMO and the glyph showcase SHOWCASE (music files unchanged).
  Start with LOAD"PETSCIIPIT",8 (or LOAD"*",8 - it is still first).

## Version 19: Runes, Glyph Lore and a New Title
- New title at 300 XP: DELVER OF THE DEPTHS. Skilled Skeeve moves to
  500 XP (with Sneak Attack). The ladder is now Alley Rat (50), Basic
  Burglar (150), Delver of the Depths (300), Skilled Skeeve (500) and
  Shadow Hand (750). Every title now comes with a character level.
- Delver of the Depths brings two skills:
  - GLYPH LORE - READ THE RUNES OF THE PIT
  - KEEN EYES (3) - SENSE WHAT ROOMS HOLD: room walls take on the colour
    of what's inside. Treasuries glow orange like treasure, apothecaries
    green like potions, and a room whose pit you've spotted goes dark grey.
- Skilled Skeeve adds KEEN EYES (4) - SEE FURTHER DOWN HALLS: one more
  square straight ahead, plus the squares either side two ahead.
- Rune stones: from level 3 down, every level has one, glowing white once
  your eyes adjust. Until you have Glyph Lore it's "A STRANGE RUNE... I
  CAN'T MAKE IT OUT." With Glyph Lore you read it and get a DESCENT RUNE,
  a 12-character code that remembers your level, XP, HP, coins and
  weapon. The character sheet keeps your LAST RUNE.
- New on the title menu: R - RESUME THE DESCENT. Speak (type) your rune
  and you go straight back down to that level with those stats. A wrong
  rune gets "THE PIT DOES NOT KNOW THAT RUNE."
- The long title message is shortened to fit: "NOW A DELVER OF THE
  DEPTHS! PRESS C".
- Freed about 2.5 KB of memory in the game (and about 0.4 KB in the demo)
  so there's room for what's next; the game should also pause less often
  to tidy up its memory.

## Version 20: Battle Wipes and SID Setup
- Fights open with a quick wipe instead of a hard cut: the border flashes
  red, the map is swept away in the direction of the blow (the way you or
  the monster moved), and the battle screen sweeps in the same way.
  Leaving a fight, the battle screen closes like a pair of eyelids and the
  map opens up from the middle. Each wipe takes about a tenth of a second.
- New SID setup screen (S on the title menu, which shows how many SIDs
  were found):
  - shows how many SIDs were found and which model (6581 or 8580) is at
    each address
  - choose auto, one SID, or two SIDs with the music on either chip; it
    says exactly where the music and the sound effects play
  - volume bars like the game's; C/V turn the music down/up, D/F the
    sound effects
  - M plays the next song; E plays a sound effect, R repeats it until a
    key is pressed, T picks the next one
  - the volumes you set carry into the game and demo
- With two SIDs, the music and the sound effects each get their own chip
  (music on $D400 by default, so SID-reactive lights like the Ultimate's
  follow the music).
- The game and demo start their music straight on Lamenting.
- The title screen appears right away, with the music, and the big
  characters dance from the first moment (they are now ready-made in the
  loader). The loader goes straight to a black screen on start-up, with no
  flash of blue or garbage.
- The instructions screen is prepared out of sight the first time you
  start the game, demo or showcase (or press I), only once.
- New on the title menu: Q - QUIT. It asks "QUIT PETSCII PIT? Y/N" and
  resets the C64.
- A wrong descent rune shows "THE PIT DOES NOT KNOW THAT RUNE." long
  enough to read.
- The game's glyphs moved off the ordinary text characters, so $ and >
  and the other symbols print normally.
- Fixed: after a reset, starting the disk again could keep the previous
  music player in memory. The loader now always sets itself up from
  scratch unless it's coming back from the game, demo or showcase.

## Version 21: Ready to Publish
- License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-
  ShareAlike 4.0 International). Share and adapt with credit, under the
  same license; no commercial use without permission from m0nde. Shown on
  the credits screen.
- The instructions screen now explains fleeing (F in a fight) and saving
  with runes (read a rune, then R on the title to resume). Two pairs of
  tips were merged to make room.

## Version 22: Faster Rooms and Menus
- Rooms appear at once when you walk in, instead of filling in. The whole
  level is now drawn in black while it's being built, so walking into a
  room only has to light it up.
- I (instructions) and C (character sheet) now open on a separate screen,
  so coming back to the map is instant instead of redrawing everything.
- Fights: keys you pressed before or during a fight no longer pile up.
  Each round only takes one key, so mashing doesn't turn into extra
  attacks. Walking still remembers keys you type ahead.
- Fights now wipe in red: the map sweeps to red from the side you came
  from, then the battle sweeps in over it. Leaving a fight starts on a red
  screen that opens from the middle out to the map.

## Version 23: Battle Moves
- Every fight key is now its own move: D (or SPACE) hits as before, A is a
  quick jab that always lands for half damage, W is a heavy blow that
  hits 60% of the time for double damage, and S guards, halving the
  damage you take with a chance to strike back.
- Monsters sometimes give away their next move: a monster that WINDS UP
  is about to hit twice as hard (guard!), one DARTING AROUND is hard to
  land a heavy blow on (jab!), and one OFF BALANCE is wide open (go
  heavy!).
- The instructions screen lists the fight keys.
- Fight wipes again: the battle screen now sweeps straight over the map
  from the side you came from, and leaving a fight opens the map from the
  middle out over the battle. No more red. The sweep always goes from you
  toward the monster, even when it attacks first.

## Version 24: The Story Begins
- Two games now: PLAY THE STORY (P) and PLAY THE ENDLESS PIT (E).
- The story has 100 levels that are the same every time, read from the
  disk. Monsters still turn up in different places.
- The story starts with a tutorial (shown as TUTORIAL instead of a level
  number): seven rooms that walk you through moving, potions, treasure,
  resting, fighting, and the I and C screens. If you die later you go
  back to level 1, not the tutorial.
- Walking onto a note or the stairs stops any keys you typed ahead, so
  you don't walk past a note or answer the stairs question by accident.
- Notes: scrolls on the floor. Walk over one to read it.
- Runes from the story take you back into the story, runes from the
  endless pit back into the endless pit.
- Reach the bottom of level 100 and the story ends.
- The endless pit is the game as it was.
- P and E now ask HAVE YE A RUNE? first, so you can go straight to the
  rune screen.
- The tutorial has a GLYPH LORE CHAMBER with a rune anyone can read: it
  gives the code for level 1, so next time you can skip the tutorial.
  There may also be a secret way out...
- Falling into a hidden hole now shows the hole as you fall.
- The endless pit has no runes on the floor any more. Instead, when you
  die you get a descent rune for that run, if you have Glyph Lore to
  read it; without it the rune is just question marks.
- Runes on the floor of the story are light green once your eyes adjust.
- The music starts at your chosen volume instead of starting loud and
  then dropping.

## Version 25: The Serpent
- A new monster slithers in from level 5: the SERPENT. It dances on the
  title screen and shows in the glyph showcase, along with the rune and
  the note.
- The game files are about 2 KB smaller: the programs on the disk are
  "crunched" (no spaces or comments), which leaves more memory free while
  you play.
- The story has an ending now (for the moment) after level 100.

## Version 26: Stop and Read
- Runes, notes and the stairs now stop you even if you hold a key down,
  so you can't walk past them without seeing them.
- Questions (Y/N), the I and C screens and game over no longer get
  answered by keys you pressed earlier, and each new level starts fresh.
- Reading a rune shows it in light green with a reminder: WRITE IT DOWN!
  PRESS C TO SEE IT AGAIN.
- Notes and their text are light blue once your eyes adjust.
- Fixed: entering a story rune on the title could give ?FILE NOT FOUND.
