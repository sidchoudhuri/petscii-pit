# PETSCII-Pit & Self-Playing Demo
## [https://m0nde.itch.io/petscii-pit](https://m0nde.itch.io/petscii-pit)
A C64 BASIC roguelike - Version 27

Two ways to play: **STORY** (100 hand-made levels, starting with a tutorial, with notes, runes and an ending) and **ENDLESS** (a new random pit every level). Fights happen on their own battle screen with Hit, Jab, Heavy and Guard. Weapons roll their stats and some are cursed. Thief titles unlock skills such as Keen Eyes, Deep Sleep (R) and Backtrack (T), and runes save your progress.

## Disk Image
The game must be launched from disk (LOAD"*",8 and RUN) because the games, music and story levels are loaded separately

[PETSCIIPIT.D64](petsciipit.d64) - Game disk image.

&nbsp;&nbsp;&nbsp;|-- [PETSCIIPIT](petsciipitloader.prg) - Loader: title screen, menu, instructions, SID setup, runes

&nbsp;&nbsp;&nbsp;|-- [STORY](petsciipitstory.prg) - The STORY game

&nbsp;&nbsp;&nbsp;|-- [ENDLESS](petsciipitendless.prg) - The ENDLESS game

&nbsp;&nbsp;&nbsp;|-- [DEMO](petsciipitdemo.prg) - Self-playing demo

&nbsp;&nbsp;&nbsp;|-- [SHOWCASE](glyphshowcase.prg) - Custom characters showcase

&nbsp;&nbsp;&nbsp;|-- [MUSICPAL](musicpal.prg) - PAL version of game music

&nbsp;&nbsp;&nbsp;|-- [MUSICNTSC](musicntsc.prg) - NTSC version of game music

&nbsp;&nbsp;&nbsp;|-- [LEVELS](levels.prg) - The 100 STORY levels and the ending

&nbsp;&nbsp;&nbsp;|__ [LEVELIDX](levelidx.prg) - Where each STORY level sits on the disk

## Source

[PETSCIIPITLOADER.BAS](petsciipitloader.bas) - Loader source code

[PETSCIIPITSTORY.BAS](petsciipitstory.bas) - STORY game source code

[PETSCIIPITENDLESS.BAS](petsciipitendless.bas) - ENDLESS game source code

[PETSCIIPITDEMO.BAS](petsciipitdemo.bas) - Self-playing demo source code

[GLYPHSHOWCASE.BAS](glyphshowcase.bas) - Custom characters showcase source code

[LEVELS.TXT](levels.txt) - The STORY levels as text, built by [pitlevels.py](pitlevels.py)

[PETSCII-PIT.PF](petscii-pit.pf) - The custom character set

## Tools

[crunch.py](crunch.py) - Strips spaces and REM text when building the .prg files, and checks nothing changed meaning

[tools/basiccheck.py](tools/basiccheck.py) - Checks the BASIC listings for missing jump targets and variable name clashes

[tools/vicetest.py](tools/vicetest.py) - Scripted test runs of a test copy of the disk in VICE

## Music

[PETSCII-PIT-PAL.SID](petscii-pit-pal.sid) - PAL version of single .SID file with all three songs

&nbsp;&nbsp;&nbsp;|-- [DUNGEONEERING-PAL.SID](dungeoneering-pal.sid) - PAL version of exploration .SID music

&nbsp;&nbsp;&nbsp;|-- [ASSAILING-PAL.SID](assailing-pal.sid) - PAL version of fighting .SID music

&nbsp;&nbsp;&nbsp;|__ [LAMENTING-PAL.SID](lamenting-pal.sid) - PAL version of gloomy .SID music

[PETSCII-PIT-NTSC.SID](petscii-pit-ntsc.sid) - NTSC version of single .SID file with all three songs

&nbsp;&nbsp;&nbsp;|-- [DUNGEONEERING-NTSC.SID](dungeoneering-ntsc.sid) - NTSC version of exploration .SID music

&nbsp;&nbsp;&nbsp;|-- [ASSAILING-NTSC.SID](assailing-ntsc.sid) - NTSC version of fighting .SID music

&nbsp;&nbsp;&nbsp;|__ [LAMENTING-NTSC.SID](lamenting-ntsc.sid) - NTSC version of gloomy .SID music

[GRAND-MEDLEY](grand-medley) - The music medley disk ([pitmedley.d64](grand-medley/pitmedley.d64)) and the files that build it

## Development Logs

[Game development log](devlog.md)

[Demo development log](devlogdemo.md)

[Testing checklist](TESTING.txt)

## Roadmaps

[Game roadmap](roadmap.md)

[Demo roadmap](roadmapdemo.md)
