#!/usr/bin/env python3
"""PETSCII Pit Grand Medley demo - data generator.

Works everything out ahead of time and writes the data the 6502 code
plays back:
  big dancer strips   (2.5 x 2.5 quarter-block dancers, 4 dance phases)
  small dancer strips (1 x 1 dancers for the ending bands)
  outro strip         (the portrait, scrolled in after the song ends)
  shrink frames       (the portrait, 22 rows tall down to 8 x 8)
  scroller texts      (top: title/author/date, bottom: greetings)
  consts.asm          (addresses and song lengths for the assembler)
  preview.png         (what the screens will look like)

Inputs (src/): petsciipitloader.bas (glyph DATA, lines 120-230),
me-petscii.prg (portrait), chargen.bin (C64 character ROM),
petscii-pit-medley-pal.sid / -ntsc.sid.
"""
import os, re, sys
from PIL import Image
import dungeon

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
os.makedirs(OUT, exist_ok=True)

ROM = open(os.path.join(SRC, "chargen.bin"), "rb").read()[:2048]  # upper/graphics set


def charbits(code):
    return [[(ROM[code * 8 + y] >> (7 - x)) & 1 for x in range(8)] for y in range(8)]


# ---------------------------------------------------------------- glyphs
def read_glyphs():
    g = {}
    for line in open(os.path.join(SRC, "petsciipitloader.bas")):
        m = re.match(r"\s*(\d+)\s+DATA\s*(.*)", line)
        if m and 120 <= int(m.group(1)) <= 230:
            v = [int(x) for x in m.group(2).split(":")[0].split(",")]
            for i in range(0, len(v), 9):
                g[v[i]] = [[(b >> (7 - x)) & 1 for x in range(8)] for b in v[i + 1:i + 9]]
    return g


GLYPHS = read_glyphs()
# Same lineup and dance frames as the title screen strips (phase 0-3)
LINEUP = [
    [128, 129, 130, 144],  # player
    [83, 211, 83, 211],    # leech
    [88, 216, 88, 216],    # goblin
    [90, 218, 90, 218],    # imp
    [84, 212, 84, 212],    # serpent
    [86, 214, 86, 214],    # guard
    [91, 219, 91, 219],    # cultist
    [65, 193, 65, 193],    # golem
]
PHASES = 4

# ---------------------------------------------------------------- quarter blocks
QUAD = {}  # (tl,tr,bl,br) -> screen code
for code in range(256):
    b = charbits(code)
    q = []
    ok = True
    for (y0, x0) in ((0, 0), (0, 4), (4, 0), (4, 4)):
        s = sum(b[y][x] for y in range(y0, y0 + 4) for x in range(x0, x0 + 4))
        if s not in (0, 16):
            ok = False
        q.append(1 if s == 16 else 0)
    if ok and tuple(q) not in QUAD:
        QUAD[tuple(q)] = code
assert len(QUAD) == 16, QUAD
SPACE, SOLID = QUAD[(0, 0, 0, 0)], QUAD[(1, 1, 1, 1)]


def big_cells(bits):
    """8x8 glyph -> 20x20 cells, each glyph pixel 5x5 quarter blocks."""
    cells = []
    for cy in range(20):
        row = []
        for cx in range(20):
            q = tuple(bits[(cy * 2 + dy) // 5][(cx * 2 + dx) // 5]
                      for dy in (0, 1) for dx in (0, 1))
            row.append(QUAD[q])
        cells.append(row)
    return cells


# ---------------------------------------------------------------- layout
BIG_ROWS = 22            # screen rows 1-22
BIG_SLOT = 24            # 20 wide dancer + 2 blank each side
BIG_TOP = 1              # dancer occupies strip rows 1-20 (screen rows 2-21)
BIG_LINE = len(LINEUP) * BIG_SLOT          # 192
BIG_W = 40 + BIG_LINE + 40                 # blank intro + lineup + wrap copy
SM_ROWS = 8
SM_SLOT = 10
SM_LINE = len(LINEUP) * SM_SLOT            # 80
SM_W = 40 + SM_LINE + 40 + 40              # blank | lineup | wrap copy | blank

ADDR_CODE = 0x0900
ADDR_BIG = 0x2C00
ADDR_TEXT = 0x9100
ADDR_SMALL = 0xA000
ADDR_OUTRO = ADDR_SMALL + PHASES * SM_ROWS * SM_W
ADDR_FRAMES = ADDR_OUTRO + BIG_ROWS * 40
ADDR_DNG = 0xE000


NAMES = ["YOU", "LEECH", "GOBLIN", "IMP", "SERPENT", "GUARD", "CULTIST", "GOLEM"]
LABEL_ROW = BIG_TOP + 19        # strip row 20 = screen row 21, the dancers' bottom row
LABEL_COLOUR, FEET_COLOUR = 1, 11


def label_cols():
    """(strip column, name) for every label, both copies"""
    out = []
    for i, name in enumerate(NAMES):
        for copy in (40, 40 + BIG_LINE):
            x = copy + i * BIG_SLOT + 2 + (20 - len(name)) // 2
            out.append((x, name))
    return out


def build_big():
    out = bytearray()
    for p in range(PHASES):
        grid = [[SPACE] * BIG_W for _ in range(BIG_ROWS)]
        for i, frames in enumerate(LINEUP):
            cells = big_cells(GLYPHS[frames[p]])
            for copy in (40, 40 + BIG_LINE):
                x0 = copy + i * BIG_SLOT + 2
                for y in range(20):
                    for x in range(20):
                        if x0 + x < BIG_W:
                            grid[BIG_TOP + y][x0 + x] = cells[y][x]
        for x, name in label_cols():
            for j, ch in enumerate(name):
                if x + j < BIG_W:
                    grid[LABEL_ROW][x + j] = screencode(ch)
        for r in grid:
            out += bytes(r)
    return out


def build_label_colours():
    """colour strip for screen row 21: white under the labels, dark grey elsewhere"""
    col = [FEET_COLOUR] * BIG_W
    for x, name in label_cols():
        for j in range(len(name)):
            if x + j < BIG_W:
                col[x + j] = LABEL_COLOUR
    return bytes(col)


def build_small():
    out = bytearray()
    for p in range(PHASES):
        grid = [[SPACE] * SM_W for _ in range(SM_ROWS)]
        for i, frames in enumerate(LINEUP):
            b = GLYPHS[frames[p]]
            for copy in (40, 40 + SM_LINE):
                x0 = copy + i * SM_SLOT + 1
                for y in range(8):
                    for x in range(8):
                        if b[y][x] and x0 + x < 40 + SM_LINE + 40:
                            grid[y][x0 + x] = SOLID
        for r in grid:
            out += bytes(r)
    return out


# ---------------------------------------------------------------- portrait
def read_portrait():
    d = open(os.path.join(SRC, "me-petscii.prg"), "rb").read()
    base = d[0] | d[1] << 8
    scr = d[0x861 - base + 2:0x861 - base + 2 + 1000]
    cols = [c for c in range(40) if any(scr[r * 40 + c] != 32 for r in range(25))]
    c0, c1 = cols[0], cols[-1]
    codes = [[scr[r * 40 + c] for c in range(c0, c1 + 1)] for r in range(25)]
    img = Image.new("L", (8 * len(codes[0]), 200))
    px = img.load()
    for r, row in enumerate(codes):
        for c, code in enumerate(row):
            b = charbits(code)
            for y in range(8):
                for x in range(8):
                    px[c * 8 + x, r * 8 + y] = 255 * b[y][x]
    return codes, img


def blocky(code):
    """quarter blocks, plus bars/edges whose rows (or columns) are all the same"""
    b = charbits(code)
    if code in QUAD.values():
        return True
    rows_same = all(r == b[0] for r in b)
    cols_same = all(len(set(r)) == 1 for r in b)
    return rows_same or cols_same


GRAPHIC = [c for c in [32, 160] + list(range(64, 128)) + list(range(192, 256)) if blocky(c)]
CAND = [(c, [v for row in charbits(c) for v in row]) for c in GRAPHIC]


def to_petscii(img, w, h):
    small = img.resize((8 * w, 8 * h), Image.LANCZOS).load()
    out = []
    for cy in range(h):
        row = []
        for cx in range(w):
            cell = [min(1.0, max(0.0, small[cx * 8 + x, cy * 8 + y] / 255))
                    for y in range(8) for x in range(8)]
            best = min(CAND, key=lambda cb: sum((a - b) ** 2 for a, b in zip(cell, cb[1])))
            row.append(best[0])
        out.append(row)
    return out


def box(w, h):
    """screen top-left for a w x h portrait centred on rows 1-22, cols 0-39"""
    return 12 - (h + 1) // 2, 20 - (w + 1) // 2


SHRINK_H = list(range(22, 7, -1))                              # 22 .. 8
SHRINK_W = [round(8 + (h - 8) * 12 / 14) for h in SHRINK_H]    # 20 .. 8


def build_portrait(img):
    frames = [to_petscii(img, w, h) for w, h in zip(SHRINK_W, SHRINK_H)]
    # outro strip: 10 blank | portrait frame 0 (20 x 22) | 10 blank
    outro = bytearray()
    for r in range(BIG_ROWS):
        outro += bytes([SPACE] * 10 + frames[0][r] + [SPACE] * 10)
    # shrink frames 1..n: each covers the previous frame's box (clears it)
    blob = bytearray()
    for k in range(1, len(frames)):
        pt, pl = box(SHRINK_W[k - 1], SHRINK_H[k - 1])
        ph, pw = SHRINK_H[k - 1], SHRINK_W[k - 1]
        t, l = box(SHRINK_W[k], SHRINK_H[k])
        blob += bytes([pt, pl, ph, pw])   # screen row, col, rows, cols
        for r in range(ph):
            for c in range(pw):
                y, x = pt + r - t, pl + c - l
                inside = 0 <= y < SHRINK_H[k] and 0 <= x < SHRINK_W[k]
                blob.append(frames[k][y][x] if inside else SPACE)
    blob.append(0)  # end marker
    # second shrink, once the dancer bands start: 8x8 -> 6x6 ... 1x1 -> gone
    sizes = [(8, 8)] + [(n, n) for n in range(6, 0, -1)] + [(0, 0)]
    imgs = [frames[-1]] + [to_petscii(img, w, h) for w, h in sizes[1:-1]] + [[]]
    blob2 = bytearray()
    for k in range(1, len(sizes)):
        pw, ph = sizes[k - 1]
        w, h = sizes[k]
        pt, pl = box(pw, ph)
        t, l = box(w, h) if w else (pt, pl)
        blob2 += bytes([pt, pl, ph, pw])
        for r in range(ph):
            for c in range(pw):
                y, x = pt + r - t, pl + c - l
                inside = 0 <= y < h and 0 <= x < w
                blob2.append(imgs[k][y][x] if inside else SPACE)
    blob2.append(0)
    return frames, outro, blob, blob2


# ---------------------------------------------------------------- texts
def screencode(ch):
    o = ord(ch)
    if 64 <= o <= 95:
        return o - 64
    if 32 <= o <= 63:
        return o
    raise ValueError(ch)


def sid_header(path):
    d = open(path, "rb").read()
    f = lambda a: d[a:a + 32].split(b"\0")[0].decode("latin-1")
    return f(0x16), f(0x36), f(0x56)


TITLE, AUTHOR, DATE = sid_header(os.path.join(SRC, "petscii-pit-medley-pal.sid"))
TOP_TEXT = f"{TITLE} - {AUTHOR} - {DATE} - ".upper()
BOTTOM_TEXT = ("PETSCII Pit  - a game by m0nde - thanks to - arturo dente - "
               "eyvind ebsen - ricky derocher - bobby brightling - coding and "
               "optimization help along the way - nordischsound - dj space - for "
               "music inspiration - all the open source tools used and their "
               "authors - https://m0n.de - ").upper()


def build_texts():
    # the top row moves left to right, so it is fed last letter first
    top = bytes(screencode(c) for c in reversed(TOP_TEXT)) + b"\xff"
    bot = bytes(screencode(c) for c in BOTTOM_TEXT) + b"\xff"
    return top, bot


# ---------------------------------------------------------------- song length
def song_frames(path):
    sys.path.insert(0, HERE)
    from songlen import run
    j, k, _ = run(path)
    return k


# ---------------------------------------------------------------- preview
PAL = {0: (0, 0, 0), 1: (255, 255, 255), 11: (51, 51, 51), 12: (119, 119, 119), 15: (187, 187, 187)}
BIG_COLOURS = [1] * 6 + [15] * 5 + [12] * 5 + [11] * 6     # rows 1-22
SM_COLOURS = [1, 1, 15, 15, 12, 12, 11, 11]


def render(screen, colour, scale=2):
    img = Image.new("RGB", (320, 200))
    px = img.load()
    for r in range(25):
        for c in range(40):
            b = charbits(screen[r][c])
            fg = PAL[colour[r][c]]
            for y in range(8):
                for x in range(8):
                    if b[y][x]:
                        px[c * 8 + x, r * 8 + y] = fg
    return img.resize((320 * scale, 200 * scale), Image.NEAREST)


def text_row(text, start):
    return [screencode(text[(start + i) % len(text)]) for i in range(40)]


def blank():
    return [[SPACE] * 40 for _ in range(25)], [[1] * 40 for _ in range(25)]


def preview(big, small, frames):
    shots = []
    # 1: big dancers mid-song
    s, col = blank()
    pos, p = 40 + 12, 0
    for r in range(BIG_ROWS):
        base = p * BIG_ROWS * BIG_W + r * BIG_W + pos
        s[1 + r] = list(big[base:base + 40])
        col[1 + r] = [BIG_COLOURS[r]] * 40
    s[0] = text_row(TOP_TEXT, 0)
    s[24] = text_row(BOTTOM_TEXT, 0)
    col[24] = [15] * 40
    shots.append(("Dancers", render(s, col)))
    # 2..: portrait shrink steps
    for k in (0, 4, 8, 14):
        s2 = [row[:] for row in s]
        for r in range(1, 23):
            s2[r] = [SPACE] * 40
        t, l = box(SHRINK_W[k], SHRINK_H[k])
        for y in range(SHRINK_H[k]):
            for x in range(SHRINK_W[k]):
                s2[t + y][l + x] = frames[k][y][x]
        c2 = [[1] * 40 for _ in range(25)]
        c2[24] = [15] * 40
        shots.append((f"Portrait {SHRINK_W[k]}x{SHRINK_H[k]}", render(s2, c2)))
    # last: small bands with the portrait
    s3 = [row[:] for row in shots and s]
    c3 = [[1] * 40 for _ in range(25)]
    c3[24] = [15] * 40
    for r in range(1, 23):
        s3[r] = [SPACE] * 40
    pa, pb = 40 + 5, 40 + 33
    for r in range(SM_ROWS):
        ra = 0 * SM_ROWS * SM_W + r * SM_W
        s3[1 + r] = list(small[ra + pa:ra + pa + 40])
        s3[15 + r] = list(small[ra + 40 + pb:ra + 40 + pb + 40])
        c3[1 + r] = [SM_COLOURS[r]] * 40
        c3[15 + r] = [SM_COLOURS[r]] * 40
    t, l = box(8, 8)
    for y in range(8):
        for x in range(8):
            s3[t + y][l + x] = frames[-1][y][x]
            c3[t + y][l + x] = 1
    shots.append(("Ending", render(s3, c3)))
    # sheet
    W, H = 640, 400
    sheet = Image.new("RGB", (W * 2 + 30, (H + 30) * 3 + 10), (40, 40, 40))
    for i, (_, im) in enumerate(shots):
        sheet.paste(im, (10 + (i % 2) * (W + 10), 10 + (i // 2) * (H + 30)))
    sheet.save(os.path.join(OUT, "preview.png"))
    # portrait steps strip, all 15 sizes
    strip = Image.new("RGB", (sum(8 * w + 8 for w in SHRINK_W) + 8, 200 + 16), (40, 40, 40))
    x = 8
    for k, f in enumerate(frames):
        s4 = [[SPACE] * 40 for _ in range(25)]
        for y in range(SHRINK_H[k]):
            for xx in range(SHRINK_W[k]):
                s4[y][xx] = f[y][xx]
        im = render(s4, [[1] * 40] * 25, 1).crop((0, 0, 8 * SHRINK_W[k], 8 * SHRINK_H[k]))
        strip.paste(im, (x, 8))
        x += 8 * SHRINK_W[k] + 8
    strip = strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST)
    strip.save(os.path.join(OUT, "portrait-steps.png"))


def main():
    big = build_big()
    small = build_small()
    codes, img = read_portrait()
    frames, outro, blob, blob2 = build_portrait(img)
    top, bot = build_texts()
    kpal = song_frames(os.path.join(SRC, "petscii-pit-medley-pal.sid"))
    kntsc = song_frames(os.path.join(SRC, "petscii-pit-medley-ntsc.sid"))

    assert ADDR_BIG + len(big) <= ADDR_TEXT, hex(ADDR_BIG + len(big))
    assert ADDR_TEXT + len(top) + len(bot) <= 0x9300
    colstrip = build_label_colours()
    outrocol = bytes([FEET_COLOUR] * 40)
    lv = dungeon.levels()
    dng = dungeon.ml_stream(lv)
    font = bytearray()
    for code in dungeon.GAME_CODES:
        if code is None:
            font += bytes(8)
        elif code in GLYPHS:
            font += bytes(sum(b << (7 - x) for x, b in enumerate(row)) for row in GLYPHS[code])
        else:
            font += ROM[code * 8:code * 8 + 8]
    dcol = bytes(dungeon.COLOURS)
    hi = small + outro + blob + blob2 + colstrip + outrocol + font + dcol
    a_frames2 = ADDR_FRAMES + len(blob)
    a_colstrip = a_frames2 + len(blob2)
    a_outrocol = a_colstrip + len(colstrip)
    a_dfont = a_outrocol + 40
    a_dcol = a_dfont + len(font)
    assert ADDR_SMALL + len(hi) <= 0xD000, hex(ADDR_SMALL + len(hi))
    assert ADDR_DNG + len(dng) <= 0xFFF0, hex(ADDR_DNG + len(dng))
    open(os.path.join(OUT, "dng.bin"), "wb").write(dng)

    open(os.path.join(OUT, "big.bin"), "wb").write(big)
    open(os.path.join(OUT, "texts.bin"), "wb").write(top + bot)
    open(os.path.join(OUT, "hi.bin"), "wb").write(hi)
    with open(os.path.join(OUT, "consts.asm"), "w") as f:
        f.write(f"""; generated by gen.py - do not edit
ADDR_CODE   = ${ADDR_CODE:04X}
ADDR_BIG    = ${ADDR_BIG:04X}
ADDR_TEXT   = ${ADDR_TEXT:04X}
ADDR_TOP    = ${ADDR_TEXT:04X}
ADDR_BOT    = ${ADDR_TEXT + len(top):04X}
ADDR_SMALL  = ${ADDR_SMALL:04X}
ADDR_OUTRO  = ${ADDR_OUTRO:04X}
ADDR_FRAMES = ${ADDR_FRAMES:04X}
HI_END      = ${ADDR_SMALL + len(hi):04X}
BIG_ROWS    = {BIG_ROWS}
BIG_W       = {BIG_W}
BIG_LINE    = {BIG_LINE}
BIG_PHASE   = {BIG_ROWS * BIG_W}
SM_ROWS     = {SM_ROWS}
SM_W        = {SM_W}
SM_LINE     = {SM_LINE}
SM_PHASE    = {SM_ROWS * SM_W}
SONG_PAL    = {kpal}
SONG_NTSC   = {kntsc}
SPACE       = {SPACE}
""")
        f.write(f"""ADDR_FRAMES2 = ${a_frames2:04X}
ADDR_COLSTRIP = ${a_colstrip:04X}
ADDR_OUTROCOL = ${a_outrocol:04X}
ADDR_DFONT  = ${a_dfont:04X}
DFONT_LEN   = {len(font)}
ADDR_DCOL   = ${a_dcol:04X}
ADDR_DNG    = ${ADDR_DNG:04X}
DNG_END     = ${ADDR_DNG + len(dng):04X}
""")
    preview(big, small, frames)
    print(f"big {len(big)} bytes ${ADDR_BIG:04X}-${ADDR_BIG + len(big) - 1:04X}")
    print(f"texts {len(top) + len(bot)} bytes  top {len(top) - 1} chars, bottom {len(bot) - 1} chars")
    print(f"hi {len(hi)} bytes ${ADDR_SMALL:04X}-${ADDR_SMALL + len(hi) - 1:04X} "
          f"(small {len(small)}, outro {len(outro)}, frames {len(blob)})")
    print(f"dungeon stream {len(dng)} bytes ${ADDR_DNG:04X}-${ADDR_DNG + len(dng) - 1:04X}")
    print(f"song end: PAL frame {kpal} ({kpal / 50:.1f}s), NTSC frame {kntsc} ({kntsc / 60:.1f}s)")


if __name__ == "__main__":
    main()
