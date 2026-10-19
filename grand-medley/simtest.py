#!/usr/bin/env python3
"""Rough C64 harness for the demo's machine code in py65.

Emulates just enough of the VIC-II (raster counter, raster IRQ, bad lines)
to run the IRQ chain and the main loop, and checks that every screen write
to the middle rows lands while the beam is not showing that row, and before
the frame that needs it. Also snapshots the screen at chosen frames.
usage: simtest.py PAL|NTSC frames [start_fcnt]
"""
import sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0, "/home/claude/demo")
import gen

NTSC = sys.argv[1].upper() == "NTSC"
FRAMES = int(sys.argv[2])
START_FCNT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
LINES = 263 if NTSC else 312
CPL = 65 if NTSC else 63

m = MPU()
mem = m.memory


def load_prg(path):
    d = open(path, "rb").read()
    a = d[0] | d[1] << 8
    mem[a:a + len(d) - 2] = list(d[2:])


load_prg("build/democode.prg")
hi = open("build/hi.bin", "rb").read()
mem[0xA000:0xA000 + len(hi)] = list(hi)
dng = open("build/dng.bin", "rb").read()
mem[0xE000:0xE000 + len(dng)] = list(dng)
LBL = {l.split()[2][1:]: int(l.split()[1][2:], 16) for l in open("build/medley.lbl") if len(l.split()) == 3}
sid = open("src/petscii-pit-medley-%s.sid" % ("ntsc" if NTSC else "pal"), "rb").read()
mem[0x9300:0x9300 + len(sid) - sid[7] - 2] = list(sid[sid[7] + 2:])
mem[0x02A6] = 0 if NTSC else 1

clock = 0          # VIC cycles since start
irq_line = None
irq_en = False
d016_log = []      # (frame, line, value)
writes = []        # (time, addr)
req_log = []       # (time, req)


def raster():
    return (clock // CPL) % LINES


class IO:
    pass


orig_read = None


# hook memory: py65 memory is a list; wrap with ObservableMemory
from py65.memory import ObservableMemory
om = ObservableMemory(subject=mem)
m.memory = om


def rd_d012(addr):
    return raster() & 255


def rd_d011(addr):
    return (mem[0xD011] & 0x7F) | (0x80 if raster() > 255 else 0)


om.subscribe_to_read([0xD012], rd_d012)
om.subscribe_to_read([0xD011], rd_d011)


def wr(addr, val):
    global irq_line, irq_en
    if addr == 0xD012:
        irq_line = val
    elif addr == 0xD01A:
        irq_en = bool(val & 1)
    elif addr == 0xD018:
        d018_now.append((raster(), val))
    elif addr == 0xD016:
        d016_log.append((clock // (CPL * LINES), raster(), val))
    elif 0x0400 <= addr < 0x07E8:
        writes.append((clock, addr))
    elif addr == 0x16 and val:
        req_log.append((clock, val))


om.subscribe_to_write(list(range(0xD000, 0xD030)) + list(range(0x0400, 0x07E8)) + [0x16], wr)

m.pc = LBL['start']
m.sp = 0xFF
started = False
last_line = -1
irq_pending = False
snap = {}
d018 = {}
d018_now = []
SNAP_AT = {int(x) for x in sys.argv[4].split(",")} if len(sys.argv) > 4 else set()
max_frame = FRAMES
while clock // (CPL * LINES) < max_frame:
    if not started and m.pc == LBL['mainloop']:      # reached main loop
        started = True
        start_clock = clock
        if START_FCNT:
            mem[0x0C] = START_FCNT & 255
            mem[0x0D] = START_FCNT >> 8
    before = m.processorCycles
    m.step()
    clock += m.processorCycles - before
    line = raster()
    if line != last_line:
        # bad line: CPU loses ~40 cycles
        if 0x30 <= line <= 0xF7 and (line & 7) == (mem[0xD011] & 7):
            clock += 40
        if irq_en and line == irq_line:
            irq_pending = True
        frame = clock // (CPL * LINES)
        if line == 0:
            if frame - 1 in SNAP_AT:
                d018[frame - 1] = list(d018_now)
            d018_now.clear()
            if frame in SNAP_AT:
                snap[frame] = (list(mem[0x0400:0x07E8]), list(mem[0xD800:0xDBE8]))
        last_line = line
    if irq_pending and not (m.p & m.INTERRUPT):
        irq_pending = False
        # push PC and P, jump through $FFFE
        m.stPushWord(m.pc)
        m.stPush(m.p & ~m.BREAK | m.UNUSED)
        m.p |= m.INTERRUPT
        m.pc = mem[0xFFFE] | mem[0xFFFF] << 8
        clock += 7

FL = CPL * LINES
# ---- check: writes to middle rows happen after the beam has shown the row
bad = 0
writes = [w for w in writes if w[0] >= start_clock]
for t, addr in writes:
    row = (addr - 0x400) // 40
    if 1 <= row <= 22:
        line = (t // CPL) % LINES
        top, bot = 51 + 8 * row, 58 + 8 * row
        if top <= line <= bot:
            bad += 1
print(f"{'NTSC' if NTSC else 'PAL'}: frames {max_frame}, screen writes {len(writes)}, "
      f"middle-row writes while that row was on screen: {bad}")
# ---- check: each request finished before the next frame showed its rows
late = 0
for i, (t, r) in enumerate(req_log):
    f = t // FL
    nxt = (f + 1) * FL
    span = [w for w in writes if t <= w[0] < (req_log[i + 1][0] if i + 1 < len(req_log) else 1e18)]
    for wt, addr in span:
        row = (addr - 0x400) // 40
        if 1 <= row <= 22 and (r == 1 or (r == 3 and not 9 <= row <= 14)):
            if wt > nxt + (51 + 8 * row) * CPL:
                late += 1
print(f"requests {len(req_log)}, writes landing after the next frame showed the row: {late}")
print("mode", mem[0x11], "tstep", mem[0x15], "fcnt", mem[0x0C] | mem[0x0D] << 8, "pos", mem[0x12])
vals = {}
for f, l, v in d016_log[-30:]:
    vals.setdefault(f, []).append((l, v))
for f in sorted(vals)[-3:]:
    print(" frame", f, "d016 writes (line, value):", vals[f])

import pickle
pickle.dump({f: (snap[f][0], snap[f][1], d018.get(f, [])) for f in snap}, open("build/snaps-%s.pkl" % ("ntsc" if NTSC else "pal"), "wb"))
from collections import Counter
cnt = Counter()
ri = 0
for t, addr in writes:
    row = (addr - 0x400) // 40
    line = (t // CPL) % LINES
    if 1 <= row <= 22 and 51 + 8 * row <= line <= 58 + 8 * row:
        while ri + 1 < len(req_log) and req_log[ri + 1][0] <= t:
            ri += 1
        cnt[(req_log[ri][1] if req_log else 0, row)] += 1
print("bad writes by (request, row):", sorted(cnt.items())[:40])
early = 0
for i, (t, r) in enumerate(req_log):
    if r != 1:
        continue
    f = t // FL
    end = req_log[i + 1][0] if i + 1 < len(req_log) else 1e18
    for wt, addr in writes:
        if t <= wt < end:
            row = (addr - 0x400) // 40
            if 1 <= row <= 22 and wt < f * FL + (59 + 8 * row) * CPL:
                early += 1
print("big-dancer writes that land before the beam has shown the row (would show a frame early):", early)
