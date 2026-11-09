# PETSCII-Pit & Self-Playing Demo
## [https://m0nde.itch.io/petscii-pit](https://m0nde.itch.io/petscii-pit)
A C64 BASIC roguelike - Version 28

Three ways to play: **STORY** (100 hand-made levels, starting with a tutorial, with notes, runes and an ending), **ENDLESS** (a new random pit every level) and the **ARENA** (fights only, harder and harder monsters). Fights happen on their own battle screen with Hit, Jab, Heavy and Guard. Weapons roll their stats and some are cursed. Every 5th level, Charpentier the mage (CHAR) runs a shop: weapons, shields, draughts, curse lifting. In the arena CHAR opens his shop every 3 fights. Thief titles unlock skills such as Keen Eyes, Deep Sleep (R) and Backtrack (T), and runes save your progress.

## Disk Image
The game must be launched from disk (LOAD"*",8 and RUN) because the games, music and story levels are loaded separately

[PETSCIIPIT.D64](petsciipit.d64) - Game disk image.

&nbsp;&nbsp;&nbsp;|-- [PETSCIIPIT](prg/petsciipitloader.prg) - Loader: title screen, menu, instructions, SID setup, runes

&nbsp;&nbsp;&nbsp;|-- [STORY](prg/petsciipitstory.prg) - The STORY game

&nbsp;&nbsp;&nbsp;|-- [ENDLESS](prg/petsciipitendless.prg) - The ENDLESS game

&nbsp;&nbsp;&nbsp;|-- [ARENA](prg/petsciipitarena.prg) - The Battle Arena: fights only, CHAR's shop every 3 fights

&nbsp;&nbsp;&nbsp;|-- [DEMO](prg/petsciipitdemo.prg) - Self-playing demo

&nbsp;&nbsp;&nbsp;|-- [SHOWCASE](prg/glyphshowcase.prg) - Custom characters showcase

&nbsp;&nbsp;&nbsp;|-- [MUSICPAL](prg/musicpal.prg) - PAL version of game music

&nbsp;&nbsp;&nbsp;|-- [MUSICNTSC](prg/musicntsc.prg) - NTSC version of game music

&nbsp;&nbsp;&nbsp;|-- [LEVELS](prg/levels.prg) - The 100 STORY levels and the ending

&nbsp;&nbsp;&nbsp;|__ [LEVELIDX](prg/levelidx.prg) - Where each STORY level sits on the disk

## Source

[PETSCIIPITLOADER.BAS](src/petsciipitloader.bas) - Loader source code

[PETSCIIPITSTORY.BAS](src/petsciipitstory.bas) - STORY game source code

[PETSCIIPITENDLESS.BAS](src/petsciipitendless.bas) - ENDLESS game source code

[PETSCIIPITARENA.BAS](src/petsciipitarena.bas) - Battle Arena source code

[PETSCIIPITDEMO.BAS](src/petsciipitdemo.bas) - Self-playing demo source code

[GLYPHSHOWCASE.BAS](src/glyphshowcase.bas) - Custom characters showcase source code

[LEVELS.TXT](src/levels.txt) - The STORY levels as text, built by [pitlevels.py](tools/pitlevels.py)

[TEXTS.TXT](src/texts.txt) - The games' fixed text (status messages, character sheet, CHAR's lines), built into the loader by [textbank.py](tools/textbank.py)

[PETSCII-PIT.PF](src/petscii-pit.pf) - The custom character set

[ASM](src/asm) - Machine code the loader installs: [screen wipes](src/asm/wipe.asm), [room reveal and level fill](src/asm/gfx.asm), [STORY level reading](src/asm/story.asm), [SID model check](src/asm/model.asm), [game text printing](src/asm/text.asm)

## Tools

[tools/crunch.py](tools/crunch.py) - Strips spaces and REM text when building the .prg files, and checks nothing changed meaning

[tools/basiccheck.py](tools/basiccheck.py) - Checks the BASIC listings for missing jump targets and variable name clashes

[tools/vicetest.py](tools/vicetest.py) - Scripted test runs of a test copy of the disk in VICE

[tools/buildprgs.sh](tools/buildprgs.sh) - Builds the programs in prg/ from the listings in src/

[tools/build_d64.sh](tools/build_d64.sh) - Builds the disk (with the story levels and the directory art): `tools/build_d64.sh 28`

[tools/levelspage.py](tools/levelspage.py) - Makes the story levels page ([m0n.de/story-levels](https://m0n.de/story-levels))

[tools/makepf.py](tools/makepf.py), [tools/titlestrips.py](tools/titlestrips.py) - Make the character set file and the title-screen strips from the loader's glyph data

## Music

[PETSCII-PIT-PAL.SID](sid/petscii-pit-pal.sid) - PAL version of single .SID file with all three songs

&nbsp;&nbsp;&nbsp;|-- [DUNGEONEERING-PAL.SID](sid/dungeoneering-pal.sid) - PAL version of exploration .SID music

&nbsp;&nbsp;&nbsp;|-- [ASSAILING-PAL.SID](sid/assailing-pal.sid) - PAL version of fighting .SID music

&nbsp;&nbsp;&nbsp;|__ [LAMENTING-PAL.SID](sid/lamenting-pal.sid) - PAL version of gloomy .SID music

[BARTERING-PAL.SID](sid/bartering-pal.sid) - PAL version of CHAR's shop .SID music

[PETSCII-PIT-NTSC.SID](sid/petscii-pit-ntsc.sid) - NTSC version of single .SID file with all three songs

&nbsp;&nbsp;&nbsp;|-- [DUNGEONEERING-NTSC.SID](sid/dungeoneering-ntsc.sid) - NTSC version of exploration .SID music

&nbsp;&nbsp;&nbsp;|-- [ASSAILING-NTSC.SID](sid/assailing-ntsc.sid) - NTSC version of fighting .SID music

&nbsp;&nbsp;&nbsp;|__ [LAMENTING-NTSC.SID](sid/lamenting-ntsc.sid) - NTSC version of gloomy .SID music

[BARTERING-NTSC.SID](sid/bartering-ntsc.sid) - NTSC version of CHAR's shop .SID music

[GRAND-MEDLEY](grand-medley) - The music medley disk ([pitmedley.d64](grand-medley/pitmedley.d64)) and the files that build it

## Screenshots

[ASSETS](assets) - Screenshots: the V28 title and instructions, STORY and ENDLESS, battles and ambushes, skills, weapons, game over, the demo, the [disk directory](assets/18-disk-directory.png), CHAR's shop ([room](assets/19-char-shop-room.png), [screen](assets/20-char-shop.png)) and the [Battle Arena](assets/24-arena-start-shop.png)

## Development Logs

[Game development log](devlog.md)

[Demo development log](docs/devlogdemo.md)

[Testing checklist](docs/TESTING.txt)

## Roadmaps

[Game roadmap](docs/roadmap.md)

[Demo roadmap](docs/roadmapdemo.md)
