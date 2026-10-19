"""PETSCII Pit dungeon strip for the Grand Medley demo.

Builds a few small levels (6 rows x 38 columns, rooms joined by corridors),
then plays them the way the game's thief would: reveal a room on entry,
pick up potions and treasure, bump monsters until they drop, walk the
corridors, take the stairs. Everything is worked out here; the demo only
plays it back.

Shared by gen.py (machine code version: a stream of screen writes) and
gen_basic.py (BASIC version: map strings, room boxes and a move string that
the BASIC replays with the same rules).
"""
import random
from collections import deque

H, W = 6, 38
# tile letters -> demo glyph number (machine code font codes 0-21)
#   0 blank, 1 wall, 2 floor, 3 stairs, 4 potion, 5 treasure,
#   6 player, 7 player bumping, 8+2*m (+1 second frame) monster m
TILE_CODE = {" ": 0, "W": 1, ".": 2, ">": 3, "P": 4, "T": 5}
MONSTERS = "ABCDEFG"          # leech goblin imp serpent guard cultist golem
MON_GLYPHS = [(83, 211), (88, 216), (90, 218), (84, 212), (86, 214), (91, 219), (65, 193)]
MON_COLOURS = [5, 7, 8, 5, 10, 2, 4]   # the game's monster table colours
# game glyph codes for each demo glyph (font data comes from the loader DATA)
GAME_CODES = [None, 102, 159, 190, 158, 132, 128, 144] + [c for pair in MON_GLYPHS for c in pair]
COLOURS = [0, 12, 11, 7, 5, 8, 3, 3] + [c for c in MON_COLOURS for _ in (0, 1)]
NLEVELS = 4
DIRS = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}
BUMP = {"L": "H", "R": "J", "U": "K", "D": "N"}     # bump, monster survives
KILL = {"L": "A", "R": "B", "U": "C", "D": "E"}     # bump, monster drops


def make_level(rng, depth):
    grid = [[" "] * W for _ in range(H)]
    room = [[-1] * W for _ in range(H)]           # -1 void, -2 corridor, k room
    rects = []
    x = 0
    prev_rows = None
    while True:
        left = W - x
        if left < 6:
            break
        rw = rng.randint(6, 11)
        if left - rw < 8:              # last room takes what is left
            rw = left
        top = rng.choice((0, 0, 1))
        bot = rng.choice((5, 5, 4))
        if bot - top < 3:
            bot = top + 3
        if prev_rows:
            # the corridor row must be inside both rooms
            lo, hi = max(prev_rows[0], top + 1), min(prev_rows[1], bot - 1)
            if lo > hi:
                top, bot = 0, 5
                lo, hi = max(prev_rows[0], 1), min(prev_rows[1], 4)
            crow = rng.randint(lo, hi)
            cx0 = rects[-1][3] + 1
            for c in range(cx0, x):
                grid[crow][c] = "."
                room[crow][c] = -2
            grid[crow][cx0 - 1] = "."              # door in the previous room
            grid[crow][x] = "."                    # door in this room
            doorrow = crow
        k = len(rects)
        r0, c0, r1, c1 = top, x, bot, x + rw - 1
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                room[r][c] = k
                edge = r in (r0, r1) or c in (c0, c1)
                if grid[r][c] != ".":
                    grid[r][c] = "W" if edge else "."
        if prev_rows:
            grid[doorrow][c0] = "."
        rects.append((r0, c0, r1, c1))
        prev_rows = (r0 + 1, r1 - 1)
        if x + rw >= W:
            break
        x = x + rw + rng.randint(1, 4)
        if W - x < 6:
            # stretch the last room to the edge instead of a stub
            r0, c0, r1, c1 = rects[-1]
            break
    # contents
    n = len(rects)
    hp = {}
    for k, (r0, c0, r1, c1) in enumerate(rects):
        cells = [(r, c) for r in range(r0 + 1, r1) for c in range(c0 + 2, c1 - 1)
                 if grid[r][c] == "."]
        rng.shuffle(cells)
        things = []
        if k == n - 1:
            things.append(">")
        if rng.random() < 0.6:
            things.append("P")
        if rng.random() < 0.6:
            things.append("T")
        for _ in range(rng.randint(0 if k == 0 else 1, 2)):
            things.append(rng.choice(MONSTERS[:3 + depth]))
        for t in things:
            if not cells:
                break
            r, c = cells.pop()
            grid[r][c] = t
            if t in MONSTERS:
                hp[(r, c)] = rng.randint(1, 3)
    start = (rects[0][0] + 1, rects[0][1] + 1)
    return {"grid": grid, "room": room, "rects": rects, "hp": hp, "start": start}


def passable(t):
    return t in ".PT>"


def bfs(grid, src, goal_ok, blocked_ok=lambda r, c: False):
    prev = {src: None}
    q = deque([src])
    while q:
        cur = q.popleft()
        if goal_ok(*cur) and cur != src:
            path = []
            while cur != src:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dr, dc in DIRS.values():
            r, c = cur[0] + dr, cur[1] + dc
            if 0 <= r < H and 0 <= c < W and (r, c) not in prev:
                if passable(grid[r][c]) or goal_ok(r, c):
                    prev[(r, c)] = cur
                    q.append((r, c))
    return None


def dir_of(a, b):
    for k, (dr, dc) in DIRS.items():
        if (a[0] + dr, a[1] + dc) == b:
            return k
    raise ValueError((a, b))


def play_level(lv):
    """the thief's moves through one level, as a move string"""
    grid = [row[:] for row in lv["grid"]]
    hp = dict(lv["hp"])
    pos = lv["start"]
    moves = []
    rects = lv["rects"]
    for k, (r0, c0, r1, c1) in enumerate(rects):
        inroom = lambda r, c: r0 <= r <= r1 and c0 <= c <= c1
        while True:
            targets = [(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)
                       if grid[r][c] in "PT" or grid[r][c] in MONSTERS]
            if not targets:
                break
            path = bfs(grid, pos, lambda r, c: (r, c) in targets)
            if path is None:
                break
            for cell in path:
                d = dir_of(pos, cell)
                t = grid[cell[0]][cell[1]]
                if t in MONSTERS:
                    while hp[cell] > 1:
                        hp[cell] -= 1
                        moves.append(BUMP[d])
                    moves.append(KILL[d])
                    grid[cell[0]][cell[1]] = "."
                    break
                moves.append(d)
                if t in "PT":
                    grid[cell[0]][cell[1]] = "."
                pos = cell
        if k == len(rects) - 1:
            goal = lambda r, c: grid[r][c] == ">"
        else:
            nr0, nc0, nr1, nc1 = rects[k + 1]
            goal = lambda r, c: c == nc0 and grid[r][c] == "."
        path = bfs(grid, pos, goal)
        for cell in path:
            moves.append(dir_of(pos, cell))
            pos = cell
    moves.append("S")
    return "".join(moves)


def levels(seed=26):
    rng = random.Random(seed)
    out = []
    for depth in range(NLEVELS):
        while True:
            lv = make_level(rng, depth + 1)
            if len(lv["rects"]) >= 3:
                break
        lv["moves"] = play_level(lv)
        out.append(lv)
    return out


class Replay:
    """Plays a level step by step with the demo's drawing rules and reports
    the cells that change (row, col, glyph) for each step. gen_basic's BASIC
    code follows the same rules, so both versions look the same."""

    def __init__(self, lv):
        self.lv = lv
        self.grid = [row[:] for row in lv["grid"]]
        self.seen = [[False] * W for _ in range(H)]
        self.rooms_seen = set()
        self.alive = {(r, c): self.grid[r][c] for r in range(H) for c in range(W)
                      if self.grid[r][c] in MONSTERS}
        self.pos = lv["start"]
        self.frame = 0
        self.bumped = False

    def glyph(self, r, c):
        t = self.grid[r][c]
        if (r, c) == self.pos:
            return 6
        if t in MONSTERS:
            return 8 + 2 * MONSTERS.index(t) + self.frame
        return TILE_CODE[t]

    def reveal_room(self, k, out):
        r0, c0, r1, c1 = self.lv["rects"][k]
        self.rooms_seen.add(k)
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if not self.seen[r][c]:
                    self.seen[r][c] = True
                    out.append((r, c, self.glyph(r, c)))

    def look(self, out):
        r, c = self.pos
        k = self.lv["room"][r][c]
        if k >= 0 and k not in self.rooms_seen:
            self.reveal_room(k, out)
        for dr, dc in [(0, 0)] + list(DIRS.values()):
            rr, cc = r + dr, c + dc
            if 0 <= rr < H and 0 <= cc < W and self.lv["room"][rr][cc] == -2 and not self.seen[rr][cc]:
                self.seen[rr][cc] = True
                out.append((rr, cc, self.glyph(rr, cc)))

    def start(self):
        out = []
        self.look(out)
        out.append((self.pos[0], self.pos[1], 6))
        return out

    def step(self, m):
        out = []
        self.frame ^= 1
        if self.bumped:                               # bump glyph lasts a step
            out.append((self.pos[0], self.pos[1], 6))
            self.bumped = False
        for (r, c), t in self.alive.items():          # monsters dance
            if self.seen[r][c]:
                out.append((r, c, 8 + 2 * MONSTERS.index(t) + self.frame))
        if m == "S":
            return out
        d = next(k for k, v in list(BUMP.items()) + list(KILL.items()) if v == m) \
            if m not in DIRS else m
        dr, dc = DIRS[d]
        r, c = self.pos
        tr, tc = r + dr, c + dc
        if m in DIRS:
            if self.grid[tr][tc] in "PT":
                self.grid[tr][tc] = "."
            self.pos = (tr, tc)
            out.append((r, c, self.glyph(r, c)))
            out.append((tr, tc, 6))
            self.look(out)
        else:
            out.append((r, c, 7))                     # bump
            self.bumped = True
            if m in KILL.values():
                del self.alive[(tr, tc)]
                self.grid[tr][tc] = "."
                out.append((tr, tc, 2))
        return out

def ml_stream(lvls, max_writes=40):
    """machine code version: steps of screen writes for rows 9-14.
    step = count, then count x (offset, glyph); offset = row*40 + col + 1.
    count 255 = back to the start."""
    out = bytearray()

    def emit(writes):
        nonlocal out
        while True:
            chunk, writes = writes[:max_writes], writes[max_writes:]
            out.append(len(chunk))
            for r, c, g in chunk:
                out += bytes([r * 40 + c + 1, g])
            if not writes:
                break

    for lv in lvls:
        for r in range(H):                            # clear a row a step
            emit([(r, c, 0) for c in range(W)])
        rp = Replay(lv)
        emit(rp.start())
        for m in lv["moves"]:
            emit(rp.step(m))
        for _ in range(6):                            # a moment on the stairs
            emit([])
    out.append(255)
    return bytes(out)


if __name__ == "__main__":
    for i, lv in enumerate(levels()):
        print("level", i + 1, "rooms", len(lv["rects"]), "moves", len(lv["moves"]))
        for row in lv["grid"]:
            print("  |" + "".join(row) + "|")
        print("  ", lv["moves"])
    print("ml stream bytes", len(ml_stream(levels())))
