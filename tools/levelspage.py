#!/usr/bin/env python3
"""Make the story levels preview page from a pitlevels.py build folder.
usage: levelspage.py <build-dir> <artifact.html> <standalone.html>"""
import base64, csv, sys, os
d, art, alone = sys.argv[1:4]
rows = list(csv.DictReader(open(os.path.join(d, 'stats.csv'))))
cards = []
for r in rows:
    lv = int(r['level'])
    b64 = base64.b64encode(open(os.path.join(d, 'level-%03d.png' % lv), 'rb').read()).decode()
    tags = []
    if r['made'] == 'hand-made': tags.append('<span class="tag hand">%s</span>' % ('tutorial' if lv == 0 else 'hand-made'))
    if r['notes'] != '0': tags.append('<span class="tag note">%s note%s</span>' % (r['notes'], 's' * (r['notes'] != '1')))
    if r['hole'] == '1': tags.append('<span class="tag hole">hole</span>')
    if r['rune'] == '1': tags.append('<span class="tag rune">rune</span>')
    if r.get('shop') == '1': tags.append('<span class="tag shop">CHAR&rsquo;s shop</span>')
    blk = '%s block%s' % (r['blocks'], 's' * (r['blocks'] != '1'))
    seed = 'seed %s' % r['seed'] if r['made'] == 'generated' else 'drawn in levels.txt'
    cards.append(f'''<figure class="lvl" id="l{lv}" tabindex="0" aria-label="{'Tutorial' if lv == 0 else 'Level %d' % lv}">
<img src="data:image/png;base64,{b64}" width="320" height="200" alt="Map of {'the tutorial' if lv == 0 else 'level %d' % lv}" loading="lazy">
<figcaption><b>{'TUTORIAL' if lv == 0 else 'LEVEL %d' % lv}</b><span class="meta">{r['rooms']} rooms · {r['bytes']} bytes · {blk} · {seed}</span><span class="tags">{''.join(tags)}</span></figcaption></figure>''')
tot = len(rows)
nb = {}
for r in rows: nb[r['blocks']] = nb.get(r['blocks'], 0) + 1
blocks = sum(int(r['blocks']) for r in rows) + 1
holes = sum(r['hole'] == '1' for r in rows); runes = sum(r['rune'] == '1' for r in rows); shops = sum(r.get('shop') == '1' for r in rows)
notes = sum(int(r['notes']) for r in rows)
bsum = ', '.join('<b>%d</b> in %s block%s' % (nb[k], k, 's' * (k != '1')) for k in sorted(nb))
style = '''
/* Layout: a C64 screen-room; a header strip, then a wrap grid of 100 map tiles at native 320x200 */
:root {
  --bg: #0b0b0e; --panel: #15151b; --line: #2a2a34; --fg: #c9c9d4; --dim: #8a8a99;
  --cyan: #67b6bd; --yellow: #bfce72; --white: #f2f2f2; --green: #94e089;
  --display: "Silkscreen", "Courier New", monospace;
  --body: "IBM Plex Mono", ui-monospace, "Courier New", monospace;
  color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 14px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 48px; }
header { max-width: 1400px; margin: 0 auto 24px; display: grid; gap: 10px; }
h1 { font-family: var(--display); font-weight: 400; font-size: clamp(22px, 4vw, 34px); color: var(--white); margin: 0; letter-spacing: .02em; text-wrap: balance; }
header p { margin: 0; max-width: 70ch; color: var(--dim); line-height: 1.55; }
.facts { display: flex; flex-wrap: wrap; gap: 8px 22px; font-variant-numeric: tabular-nums; }
.facts span b { color: var(--cyan); font-weight: 600; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 16px; color: var(--dim); font-size: 12px; }
.legend i { font-style: normal; color: var(--fg); }
main { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 14px; }
.lvl { margin: 0; background: var(--panel); border: 1px solid var(--line); padding: 8px; display: grid; gap: 8px; cursor: zoom-in; }
.lvl:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.lvl img { width: 100%; height: auto; image-rendering: pixelated; display: block; background: #000; }
.lvl.big { grid-column: 1 / -1; cursor: zoom-out; }
.lvl.big img { max-width: 960px; justify-self: center; }
figcaption { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; font-size: 12px; font-variant-numeric: tabular-nums; }
figcaption b { font-family: var(--display); font-weight: 400; font-size: 14px; color: var(--yellow); letter-spacing: .04em; }
.meta { color: var(--dim); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-left: auto; }
.tag { font-size: 11px; padding: 1px 6px; border: 1px solid var(--line); text-transform: uppercase; letter-spacing: .08em; }
.tag.rune, .tag.note { color: var(--white); }
.tag.hand { color: var(--green); border-color: var(--green); }
.tag.shop { color: #b98cd6; border-color: #b98cd6; }
@media (prefers-reduced-motion: no-preference) { .lvl { transition: border-color .15s; } .lvl:hover { border-color: var(--dim); } }
'''
body = f'''<header>
<h1>PETSCII PIT · STORY LEVELS</h1>
<p>All 100 levels for the STORY game, drawn with the game's own characters in Keen Eyes colors. The player marks the start. Hidden holes are shown as a grey O so they can be reviewed. In game they look like the floor. Monsters are placed at random each time a level loads, except where a level fixes them (the tutorial's goblin). Click a map to enlarge it.</p>
<div class="facts"><span><b>{tot-1}</b> levels and the tutorial</span><span>{bsum}</span><span><b>{blocks}</b> blocks for the levels file</span><span><b>{notes}</b> notes</span><span><b>{holes}</b> with a hole</span><span><b>{runes}</b> with a floor rune</span><span><b>{shops}</b> with CHAR&rsquo;s shop</span></div>
<div class="legend"><span><i>yellow steps</i> stairs</span><span><i>green flask</i> potion</span><span><i>orange chest</i> treasure</span><span><i>light green stone</i> rune</span><span><i>light blue scroll</i> note</span><span><i>grey O</i> hidden hole</span><span><i>purple mage</i> CHAR&rsquo;s shop, levels 5, 10 ... 100 (1-3 draughts in the game)</span><span>change a level with levels.txt: seed, rune off, note, or draw it by hand</span></div>
</header>
<main>
{''.join(cards)}
</main>
<script>
document.querySelectorAll('.lvl').forEach(f => {{
  const t = () => f.classList.toggle('big');
  f.addEventListener('click', t);
  f.addEventListener('keydown', e => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); t(); }} }});
}});
</script>
'''
fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen&family=IBM+Plex+Mono:wght@400;600&display=swap">'
open(art, 'w').write('<title>PETSCII Pit Story Levels</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + fonts + '\n<style>' + style + '</style>\n' + body)
open(alone, 'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>PETSCII Pit Story Levels</title>\n' + fonts + '\n<style>\n* { box-sizing: border-box; }\nbody { margin: 0; }' + style + '</style>\n</head>\n<body>\n' + body + '</body>\n</html>\n')
print('pages written')
