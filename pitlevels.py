#!/usr/bin/env python3
"""PETSCII Pit story levels: make, pack and preview the STORY game's levels.

Generated levels follow the game's own rules (petsciipit.bas 4460-5230,
hole 5850-5880, rune 6300-6330), with whole-level retries instead of the
game's give-up-after-2000-tries overlap, and every level is checked so it can
be completed (start room centre -> stairs). A level can instead be drawn by
hand in levels.txt (level 1, the tutorial, is).

Packed level record (padded to whole 254-byte blocks):
  0      NR (rooms, 5-7 when generated)
  1..    NR x 4 bytes: x, y, width, height (room 1 = start, last = stairs)
  ..     NR bytes: room type RT% (1 entry, 2 stairs, 3 treasury, 4 room,
         5 apothecary)
  ..     2 bytes: hidden hole cell (lo, hi), $FFFF = none
  ..     notes: count, then per note: cell lo, cell hi, length 1, line 1,
         length 2, line 2 (screen codes, up to 39 characters a line)
  ..     fixed monsters: count, then per monster: cell lo, cell hi, type
         (1 leech 2 goblin 3 imp 4 serpent 5 guard 6 cultist 7 golem), group size.
         0 = monsters are placed at random by the game.
  ..     room names: per room a length and the text (screen codes);
         length 0 = the game names the room itself
  ..     map, rows 3-24 (880 cells) as runs: one byte = type*16 + (run-1)
Map cell types: 0 blank, 1 floor, 2 room wall, 5 potion, 6 chest, 7 rune,
8 note (scroll, screen code 167), 9 stairs, 10 corridor wall.

Files:
  levels.prg    block 0 = "PIT LEVELS" header, then each level padded to
                whole 254-byte blocks (level 0 = the tutorial, then levels
                1-100), then the ending (line count, then per line a length
                and the text)
  levelidx.prg  load address $9200: per record (102) track, sector, block
                count (made by reading the finished d64 back)

levels.txt (next to the tool), one change per line, # = comment:
  12 seed 5123                     regenerate level 12 from another seed
  30 rune off                      no floor rune on level 30
  45 note LINE ONE | LINE TWO      a note, placed in a random room
  1 room 2 4 7 5                   hand-made level: rooms in order (x y w h)
  1 name 4 DORMITORY               a room's name (any level)
  ending THE TEXT OF ONE LINE      the ending, up to 10 lines of 39
  1 map                            hand-made level: the next 22 lines are
                                   rows 3-24, 40 characters each, then "end"
     map characters: space blank, . floor, # room wall, + corridor wall,
     P potion, C chest, S stairs, R rune, N note, O hidden hole,
     L G I E U T M monster (leech goblin imp serpent guard cultist golem)
     on floor.
     Notes on a hand-made map take the "note" lines in reading order.

usage: pitlevels.py sample <out-dir> [levels...]   preview PNGs + sizes
       pitlevels.py build <out-dir>                all 100: levels.prg,
                                                   previews, stats
       pitlevels.py index <d64>                    read levels back from the
                                                   d64, write levelidx.prg
"""
import random, sys, os

W, ROW0, ROW1 = 40, 3, 24
BLANK, FLOOR, WALL, POTION, CHEST, RUNE, NOTE, STAIRS, CWALL = 0, 1, 2, 5, 6, 7, 8, 9, 10
MONSTERS = "LGIEUTM"


def gen_level(lv, rng, rune=True, notes=()):
    """One level with the game's rules. Returns a dict, or None to retry."""
    ma = [0] * 1000
    rm = [0] * 1000
    nr = 5 + int(rng.random() * 3)
    rooms = []
    for i in range(nr):
        for tr in range(2000):
            w1 = 4 + int(rng.random() * 4)
            h1 = 3 + int(rng.random() * 3)
            x1 = 1 + int(rng.random() * (39 - w1))
            y1 = 3 + int(rng.random() * (21 - h1))
            ok = all(x1 + w1 + 1 < rx or rx + rw + 1 < x1 or
                     y1 + h1 + 1 < ry or ry + rh + 1 < y1
                     for rx, ry, rw, rh in rooms)
            if ok:
                break
        else:
            return None          # the game would accept an overlap here
        rooms.append((x1, y1, w1, h1))
    for i, (rx, ry, rw, rh) in enumerate(rooms, 1):
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                ix = y * W + x
                if x in (rx, rx + rw - 1) or y in (ry, ry + rh - 1):
                    ma[ix] = WALL
                else:
                    ma[ix] = FLOOR
                    rm[ix] = i

    def cwalls(ux, uy):
        uz = uy * W + ux
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            if (dy < 0 and uy <= 3) or (dy > 0 and uy >= 24) or (dx < 0 and ux <= 0) or (dx > 0 and ux >= 39):
                continue
            if ma[uz + dy * W + dx] == BLANK:
                ma[uz + dy * W + dx] = CWALL

    def centre(r):
        rx, ry, rw, rh = r
        return rx + rw // 2, ry + rh // 2

    for i in range(nr - 1):
        cx, cy = centre(rooms[i])
        ex, ey = centre(rooms[i + 1])
        x = cx
        while x != ex:
            ix = cy * W + x
            ma[ix] = FLOOR
            if rm[ix] == 0:
                cwalls(x, cy)
            x += (ex > cx) - (ex < cx)
        y = cy
        while y != ey:
            ix = y * W + ex
            ma[ix] = FLOOR
            if rm[ix] == 0:
                cwalls(ex, y)
            y += (ey > cy) - (ey < cy)
    sx, sy = centre(rooms[-1])
    ma[sy * W + sx] = STAIRS
    rt = [0] * (nr + 1)

    def interior(pr):
        rx, ry, rw, rh = rooms[pr - 1]
        qx = rx + 1 + int(rng.random() * (rw - 2))
        qy = ry + 1 + int(rng.random() * (rh - 2))
        return qx, qy

    for _ in range(nr // 3 + 1):                       # potions
        pr = 2 + int(rng.random() * (nr - 2))
        qx, qy = interior(pr)
        ma[qy * W + qx] = POTION
        if rt[pr] == 0:
            rt[pr] = 5
    for _ in range(min(lv // 3 + 1, 5)):               # chests
        pr = 2 + int(rng.random() * (nr - 2))
        qx, qy = interior(pr)
        ma[qy * W + qx] = CHEST
        rt[pr] = 3
    rt[1] = 1
    rt[nr] = 2
    for i in range(2, nr):
        if rt[i] not in (3, 5):
            rt[i] = 4
    hz = -1                                            # hidden hole
    if not (lv < 5 or rng.random() * 5 >= lv - 4):
        while True:
            pr = 2 + int(rng.random() * (nr - 2))
            qx, qy = interior(pr)
            if ma[qy * W + qx] == FLOOR and (qx, qy) != centre(rooms[pr - 1]):
                hz = qy * W + qx
                break
    nlist = []
    for note in notes:                                 # story notes
        while True:
            pr = 2 + int(rng.random() * (nr - 2))
            qx, qy = interior(pr)
            ix = qy * W + qx
            if ma[ix] == FLOOR and ix != hz and (qx, qy) != centre(rooms[pr - 1]):
                ma[ix] = NOTE
                nlist.append((ix, note))
                break
    if lv >= 3 and rune:                               # floor rune
        while True:
            pr = 2 + int(rng.random() * (nr - 2))
            qx, qy = interior(pr)
            ix = qy * W + qx
            if ma[ix] == FLOOR and ix != hz and (qx, qy) != centre(rooms[pr - 1]):
                ma[ix] = RUNE
                break
    lvl = dict(lv=lv, nr=nr, rooms=rooms, rt=rt[1:], hole=hz, notes=nlist, monsters=[], names={}, ma=ma, made="generated")
    return lvl if reachable(lvl) else None



def reachable(lvl):
    ma = lvl["ma"]
    rx, ry, rw, rh = lvl["rooms"][0]
    start = (ry + rh // 2) * W + rx + rw // 2
    seen, todo = {start}, [start]
    while todo:
        c = todo.pop()
        if ma[c] == STAIRS:
            return True
        y, x = divmod(c, W)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and ROW0 <= ny <= ROW1:
                n = ny * W + nx
                if n not in seen and ma[n] not in (BLANK, WALL, CWALL):
                    seen.add(n)
                    todo.append(n)
    return False


def make_level(lv, seed, rune=True, notes=()):
    rng = random.Random(seed)
    while True:
        l = gen_level(lv, rng, rune, notes)
        if l:
            l["seed"] = seed
            return l


def hand_level(lv, o):
    """A level drawn in levels.txt."""
    rows, rooms = o["map"], o.get("rooms", [])
    if len(rows) != 22:
        raise SystemExit("level %d map: %d rows, need 22 (rows 3-24)" % (lv, len(rows)))
    if len(rooms) < 2:
        raise SystemExit("level %d map: give at least 2 rooms (start and stairs)" % lv)
    ma, hole, mons, notepos = [0] * 1000, -1, [], []
    code = {" ": BLANK, ".": FLOOR, "#": WALL, "+": CWALL, "P": POTION, "C": CHEST,
            "S": STAIRS, "R": RUNE, "N": NOTE, "O": FLOOR}
    for y, row in enumerate(rows, ROW0):
        row = row.ljust(40)[:40]
        for x, ch in enumerate(row):
            ix = y * W + x
            if ch in MONSTERS:
                ma[ix] = FLOOR
                mons.append((ix, MONSTERS.index(ch) + 1, 1))
            elif ch in code:
                ma[ix] = code[ch]
                if ch == "O":
                    hole = ix
                if ch == "N":
                    notepos.append(ix)
            else:
                raise SystemExit("level %d map: unknown character %r at row %d" % (lv, ch, y))
    texts = o.get("notes", [])
    if len(texts) != len(notepos):
        raise SystemExit("level %d map: %d N cells but %d note lines" % (lv, len(notepos), len(texts)))
    rt = [4] * len(rooms)
    for i, (rx, ry, rw, rh) in enumerate(rooms):
        cells = [ma[y * W + x] for y in range(ry + 1, ry + rh - 1) for x in range(rx + 1, rx + rw - 1)]
        if POTION in cells:
            rt[i] = 5
        if CHEST in cells:
            rt[i] = 3
    rt[0], rt[-1] = 1, 2
    l = dict(lv=lv, nr=len(rooms), rooms=rooms, rt=rt, hole=hole, notes=list(zip(notepos, texts)),
             monsters=mons, names={}, ma=ma, seed=0, made="hand-made")
    if not reachable(l):
        raise SystemExit("level %d map: the stairs can't be reached from room 1's centre" % lv)
    return l


def screen_codes(text):
    out = bytearray()
    for ch in text.upper():
        c = ord(ch)
        if 64 <= c <= 95:
            c -= 64
        elif not 32 <= c <= 63:
            raise SystemExit("note: can't use %r" % ch)
        out.append(c)
    return bytes(out)


def read_options(path):
    opts = {}
    if not os.path.exists(path):
        return opts
    lines = open(path).read().split("\n")
    i = 0
    while i < len(lines):
        n, line = i + 1, lines[i].rstrip()
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(None, 2)
        if parts[0].lower() == "ending":
            t = line.split(None, 1)[1].strip() if len(parts) > 1 else ""
            if len(t) > 39:
                raise SystemExit("levels.txt line %d: an ending line is up to 39 characters" % n)
            opts.setdefault("ending", []).append(screen_codes(t))
            continue
        lv, cmd = int(parts[0]), parts[1].lower()
        o = opts.setdefault(lv, {})
        if cmd == "seed":
            o["seed"] = int(parts[2])
        elif cmd == "rune":
            o["rune"] = parts[2].strip().lower() != "off"
        elif cmd == "note":
            two = [t.strip() for t in parts[2].split("|")] + [""]
            if len(two) > 3 or max(len(two[0]), len(two[1])) > 39:
                raise SystemExit("levels.txt line %d: a note is up to 2 lines of 39 characters" % n)
            o.setdefault("notes", []).append((screen_codes(two[0]), screen_codes(two[1])))
        elif cmd == "name":
            k, t = parts[2].split(None, 1)
            if len(t.strip()) > 30:
                raise SystemExit("levels.txt line %d: a room name is up to 30 characters" % n)
            o.setdefault("names", {})[int(k)] = screen_codes(t.strip())
        elif cmd == "room":
            o.setdefault("rooms", []).append(tuple(int(v) for v in parts[2].split()))
        elif cmd == "map":
            rows = []
            while lines[i].strip() != "end":
                rows.append(lines[i])
                i += 1
            i += 1
            o["map"] = rows
        else:
            raise SystemExit("levels.txt line %d: unknown command %s" % (n, cmd))
    return opts


def all_levels(opts):
    out = []
    for lv in range(0, 101):
        o = opts.get(lv, {})
        if "map" in o:
            l = hand_level(lv, o)
        else:
            l = make_level(lv, o.get("seed", 1000 + lv), o.get("rune", True), o.get("notes", ()))
        for k in o.get("names", {}):
            if not 1 <= k <= l["nr"]:
                raise SystemExit("level %d: no room %d to name" % (lv, k))
        l["names"] = o.get("names", {})
        out.append(l)
    return out


def pack(l):
    out = bytearray([l["nr"]])
    for r in l["rooms"]:
        out += bytes(r)
    out += bytes(l["rt"])
    h = l["hole"] if l["hole"] >= 0 else 0xFFFF
    out += bytes([h & 255, h >> 8])
    out.append(len(l["notes"]))
    for ix, (a, b) in l["notes"]:
        out += bytes([ix & 255, ix >> 8, len(a)]) + a + bytes([len(b)]) + b
    out.append(len(l["monsters"]))
    for ix, t, g in l["monsters"]:
        out += bytes([ix & 255, ix >> 8, t, g])
    for k in range(1, l["nr"] + 1):
        nm = l["names"].get(k, b"")
        out += bytes([len(nm)]) + nm
    cells = l["ma"][ROW0 * W:(ROW1 + 1) * W]
    i = 0
    while i < len(cells):
        t, n = cells[i], 1
        while i + n < len(cells) and cells[i + n] == t and n < 16:
            n += 1
        out.append(t * 16 + n - 1)
        i += n
    return bytes(out)


def unpack(b):
    """Inverse of pack (used to check the format)."""
    nr = b[0]
    p = 1
    rooms = [tuple(b[p + 4 * i:p + 4 * i + 4]) for i in range(nr)]
    p += 4 * nr
    rt = list(b[p:p + nr]); p += nr
    h = b[p] | b[p + 1] << 8; p += 2
    notes = []
    k = b[p]; p += 1
    for _ in range(k):
        ix = b[p] | b[p + 1] << 8; p += 2
        a = b[p + 1:p + 1 + b[p]]; p += 1 + b[p]
        c = b[p + 1:p + 1 + b[p]]; p += 1 + b[p]
        notes.append((ix, (bytes(a), bytes(c))))
    m = b[p]; p += 1
    mons = [(b[p + 4 * j] | b[p + 4 * j + 1] << 8, b[p + 4 * j + 2], b[p + 4 * j + 3]) for j in range(m)]
    p += 4 * m
    names = {}
    for k in range(1, nr + 1):
        if b[p]:
            names[k] = bytes(b[p + 1:p + 1 + b[p]])
        p += 1 + b[p]
    cells = []
    while len(cells) < 880:
        cells += [b[p] >> 4] * ((b[p] & 15) + 1)
        p += 1
    return dict(nr=nr, rooms=rooms, rt=rt, hole=-1 if h == 0xFFFF else h,
                notes=notes, monsters=mons, names=names, ma=[0] * 120 + cells)


DEFAULT_ENDING = ["YOU HAVE REACHED THE BOTTOM", "OF THE PIT.", "", "(THE ENDING TEXT GOES HERE.)"]


def ending_record(opts):
    lines = opts.get("ending") or [screen_codes(t) for t in DEFAULT_ENDING]
    if len(lines) > 10:
        raise SystemExit("levels.txt: the ending is up to 10 lines")
    out = bytearray([len(lines)])
    for t in lines:
        out += bytes([len(t)]) + t
    return bytes(out)


def levels_prg(levels, opts):
    """levels.prg bytes and each record's first block number and block count
    (100 levels, then the ending as record 101)."""
    data = bytearray(b"PIT LEVELS") + bytes([len(levels)])
    data += bytes(252 - len(data))          # block 0: load address + 252 bytes
    where = []
    for b in [pack(l) for l in levels] + [ending_record(opts)]:
        n = -(-len(b) // 254)
        if n > 3:
            raise SystemExit("a level packs to %d bytes; the game reads up to 3 blocks (762)" % len(b))
        where.append(((len(data) + 2) // 254, n))
        data += b + bytes(n * 254 - len(b))
    return bytes([0x00, 0xB0]) + bytes(data), where


SPT = [21] * 17 + [19] * 7 + [18] * 6 + [17] * 5


def d64_chain(d, name):
    """Track/sector list of a file on a d64."""
    off = lambda t, s: (sum(SPT[:t - 1]) + s) * 256
    t, s = 18, 1
    want = name.upper().encode().ljust(16, b"\xa0")
    while t:
        p = off(t, s)
        for i in range(8):
            e = d[p + i * 32 + 2:p + i * 32 + 32]
            if e[0] & 7 == 2 and bytes(e[3:19]).upper() == want:
                ft, fs, chain = e[1], e[2], []
                while ft:
                    chain.append((ft, fs))
                    q = off(ft, fs)
                    ft, fs = d[q], d[q + 1]
                return chain
        t, s = d[p], d[p + 1]
    raise SystemExit("no file %s on the disk" % name)


# ---- preview ----
PAL = [(0, 0, 0), (255, 255, 255), (136, 57, 50), (103, 182, 189), (139, 63, 150),
       (85, 160, 73), (64, 49, 141), (191, 206, 114), (139, 84, 41), (87, 66, 0),
       (184, 105, 98), (80, 80, 80), (120, 120, 120), (148, 224, 137), (120, 105, 196),
       (159, 159, 159)]
# after Keen Eyes (50 XP): screen code and colour for each cell type
LOOK = {BLANK: (32, 0), FLOOR: (159, 11), WALL: (102, 12), POTION: (158, 5), CHEST: (132, 8),
        RUNE: (166, 13), NOTE: (167, 14), STAIRS: (190, 7), CWALL: (102, 11)}
MLOOK = {1: (83, 5), 2: (88, 7), 3: (90, 8), 4: (84, 5), 5: (86, 10), 6: (91, 2), 7: (65, 4)}


def render(l, charset, scale=2):
    from PIL import Image
    img = Image.new("RGB", (320, 200))
    px = img.load()

    def put(ix, code, col):
        y0, x0 = divmod(ix, W)
        for r in range(8):
            bits = charset[code * 8 + r]
            for c in range(8):
                if bits & (128 >> c):
                    px[x0 * 8 + c, y0 * 8 + r] = PAL[col]

    for ix in range(120, 1000):
        code, col = LOOK[l["ma"][ix]]
        if code != 32:
            put(ix, code, col)
    if l["hole"] >= 0:
        put(l["hole"], 87, 15)                 # shown here so it can be reviewed
    for ix, t, g in l["monsters"]:
        put(ix, *MLOOK[t])
    rx, ry, rw, rh = l["rooms"][0]
    put((ry + rh // 2) * W + rx + rw // 2, 128, 3)
    return img.resize((320 * scale, 200 * scale), Image.NEAREST)


def charset(here):
    return open(os.path.join(here, "petscii-pit-note.pf"), "rb").read()


def check(l):
    u = unpack(pack(l))
    assert u["ma"][120:] == l["ma"][120:] and u["hole"] == l["hole"]
    assert u["notes"] == [(ix, (bytes(a), bytes(b))) for ix, (a, b) in l["notes"]]
    assert u["monsters"] == l["monsters"]
    assert u["names"] == l["names"]


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("sample", "build", "index"):
        print(__doc__)
        return
    here = os.path.dirname(os.path.abspath(__file__))
    opts = read_options(os.path.join(here, "levels.txt"))
    if sys.argv[1] == "index":
        d = open(sys.argv[2], "rb").read()
        chain = d64_chain(d, "levels")
        _, where = levels_prg(all_levels(opts), opts)
        idx = bytearray([0x00, 0x92])
        for first, n in where:
            t, s_ = chain[first]
            idx += bytes([t, s_, n])
        open("levelidx.prg", "wb").write(idx)
        print("levelidx.prg: %d levels, levels file is %d blocks" % (len(where), len(chain)))
        return
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    cs = charset(here)
    if sys.argv[1] == "sample":
        lvs = [int(a) for a in sys.argv[3:]] or [0, 1, 10, 25, 50, 100]
        levels = all_levels(opts)
        for lv in lvs:
            l = levels[lv]
            check(l)
            render(l, cs).save(os.path.join(out, "level-%03d.png" % lv))
            print("level %3d: %d rooms, %s, packed %d bytes" % (lv, l["nr"], l["made"], len(pack(l))))
        return
    levels = all_levels(opts)
    prg, where = levels_prg(levels, opts)
    open(os.path.join(out, "levels.prg"), "wb").write(prg)
    with open(os.path.join(out, "stats.csv"), "w") as f:
        f.write("level,rooms,hole,rune,notes,bytes,blocks,seed,made\n")
        for l, (first, n) in zip(levels, where):
            check(l)
            render(l, cs, 1).save(os.path.join(out, "level-%03d.png" % l["lv"]))
            f.write("%d,%d,%d,%d,%d,%d,%d,%d,%s\n" % (l["lv"], l["nr"], l["hole"] >= 0, RUNE in l["ma"],
                                                    len(l["notes"]), len(pack(l)), n, l["seed"], l["made"]))
    print("levels.prg: %d bytes, %d blocks; levels of 1 block: %d, 2 blocks: %d" % (
        len(prg), -(-(len(prg) - 2) // 254), sum(1 for _, n in where[:101] if n == 1),
        sum(1 for _, n in where[:101] if n == 2)))


if __name__ == "__main__":
    main()
