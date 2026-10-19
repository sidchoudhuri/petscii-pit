#!/usr/bin/env python3
"""Runs pitmedleybas.bas on the real C64 BASIC and KERNAL ROMs in py65.

No VIC or SID: the raster counter is faked from the cycle count, LOAD is
answered from the build folder, and TI is ticked by the harness (optionally
fast-forwarded to reach the ending sooner). Stops on any BASIC error and
reports the line. Takes screen snapshots for a contact sheet.
usage: basictest.py PAL|NTSC seconds_of_c64_time [skip_to_ending] [snap_every_s]
"""
import sys, pickle
from py65.devices.mpu6502 import MPU
sys.path.insert(0, "/home/claude/demo")
import build_disk

NTSC = sys.argv[1].upper() == "NTSC"
SECONDS = float(sys.argv[2])
SKIP = len(sys.argv) > 3 and sys.argv[3] == "skip"
SNAP_EVERY = float(sys.argv[4]) if len(sys.argv) > 4 else 0
CLOCK = 1022727 if NTSC else 985248
LINES, CPL = (263, 65) if NTSC else (312, 63)

BASIC = open("src/basic-901226-01.bin", "rb").read()
KERNAL = open("src/kernal-901227-03.bin", "rb").read()
CHARGEN = open("src/chargen.bin", "rb").read()


class Mem:
    def __init__(self, mpu):
        self.ram = bytearray(65536)
        self.io = bytearray(4096)
        self.colour = bytearray(1024)
        self.mpu = mpu
        self.d018 = []

    def port(self):
        return self.ram[1] & 7

    def __getitem__(self, a):
        if a < 0xA000:
            return self.ram[a]
        p = self.port()
        if a < 0xC000:
            return BASIC[a - 0xA000] if (p & 3) == 3 else self.ram[a]
        if a < 0xD000:
            return self.ram[a]
        if a < 0xE000:
            if (p & 3) == 0:
                return self.ram[a]
            if p & 4:
                return self.ioread(a)
            return CHARGEN[a - 0xD000]
        return KERNAL[a - 0xE000] if p & 2 else self.ram[a]

    def ioread(self, a):
        cyc = self.mpu.processorCycles
        line = (cyc // CPL) % LINES
        if a == 0xD012:
            return line & 255
        if a == 0xD011:
            return (self.io[0x011] & 0x7F) | (0x80 if line > 255 else 0)
        if a == 0xD019:
            return 0
        if 0xD800 <= a < 0xDC00:
            return self.colour[a - 0xD800] | 0xF0
        if a == 0xDC01:
            return 0xFF
        if a == 0xDC0D or a == 0xDD0D:
            return 0
        return self.io[a - 0xD000]

    def __setitem__(self, a, v):
        if 0xD000 <= a < 0xE000 and (self.port() & 3) and (self.port() & 4):
            if 0xD800 <= a < 0xDC00:
                self.colour[a - 0xD800] = v & 15
            else:
                self.io[a - 0xD000] = v
                if a == 0xD018:
                    self.d018.append(v)
                    flips.append(self.mpu.processorCycles)
            return
        self.ram[a] = v


flips = []
PROF_START = '--startup' in sys.argv
skipped = False
prof = {}
lastc = 0
m = MPU()
mem = Mem(m)
m.memory = mem
mem.ram[0], mem.ram[1] = 0x2F, 0x37
m.pc = KERNAL[0x1FFC] | KERNAL[0x1FFD] << 8
files = {"MEDLEYPAL": open("build/medleypal.prg", "rb").read(),
         "MEDLEYNTSC": open("build/medleyntsc.prg", "rb").read()}
prg = build_disk.tokenize("pitmedleybas.bas")
JIFFY = CLOCK / 60
started = False
next_jiffy = 0
loads = []
snaps = []
next_snap = SNAP_EVERY * CLOCK if SNAP_EVERY else None
lines_seen = set()
limit = int(SECONDS * CLOCK)
start_cycles = 0
error = None
while m.processorCycles - start_cycles < limit or not started:
    pc = m.pc
    if pc == 0xFFD5:                        # KERNAL LOAD
        n = mem.ram[0xB7]
        a = mem.ram[0xBB] | mem.ram[0xBC] << 8
        name = bytes(mem[a + i] for i in range(n)).decode()
        d = files[name]
        la = d[0] | d[1] << 8 if mem.ram[0xB9] else mem.ram[0x2B] | mem.ram[0x2C] << 8
        mem.ram[la:la + len(d) - 2] = d[2:]
        end = la + len(d) - 2
        mem.ram[0xAE], mem.ram[0xAF] = end & 255, end >> 8
        m.x, m.y = end & 255, end >> 8
        m.p &= ~m.CARRY
        lo = m.stPop()
        hi = m.stPop()
        m.pc = (hi << 8 | lo) + 1
        loads.append(name)
        continue
    if pc == 0xA437:                        # BASIC error
        error = (m.x, mem.ram[0x39] | mem.ram[0x3A] << 8)
        break
    if not started and pc == 0xE5CD:        # waiting for a key at READY.
        mem.ram[0x0801:0x0801 + len(prg) - 2] = prg[2:]
        end = 0x0801 + len(prg) - 2
        for z in (0x2D, 0x2F, 0x31):
            mem.ram[z], mem.ram[z + 1] = end & 255, end >> 8
        mem.ram[0x02A6] = 0 if NTSC else 1
        for i, ch in enumerate(b"RUN\r"):
            mem.ram[0x0277 + i] = ch
        mem.ram[0xC6] = 4
        started = True
        start_cycles = m.processorCycles
        next_jiffy = m.processorCycles + JIFFY
    m.step()
    if started:
        if m.processorCycles >= next_jiffy:     # TI, 60 times a second
            next_jiffy += JIFFY
            ti = mem.ram[0xA0] << 16 | mem.ram[0xA1] << 8 | mem.ram[0xA2]
            ti += 1
            mem.ram[0xA0], mem.ram[0xA1], mem.ram[0xA2] = ti >> 16 & 255, ti >> 8 & 255, ti & 255
        if SKIP and len(mem.d018) > 12 and not skipped:
            skipped = True
            mem.ram[0xA0] = 0x7F                # pretend the song has ended
        line = mem.ram[0x39] | mem.ram[0x3A] << 8
        lines_seen.add(line)
        if len(flips) >= 2 or PROF_START:
            prof[line] = prof.get(line, 0) + m.processorCycles - lastc
        lastc = m.processorCycles
        if next_snap and m.processorCycles - start_cycles >= next_snap:
            next_snap += SNAP_EVERY * CLOCK
            shown = mem.d018[-1] if mem.d018 else 2
            base = 0xC000 + (shown >> 4) * 0x400
            snaps.append((round((m.processorCycles - start_cycles) / CLOCK, 1), line,
                          bytes(mem.ram[base:base + 1000]), bytes(mem.colour[:1000]),
                          bytes(mem.ram[0xC800:0xD000])))

secs = (m.processorCycles - start_cycles) / CLOCK
def basvars():
    out = {}
    a = mem.ram[0x2D] | mem.ram[0x2E] << 8
    end = mem.ram[0x2F] | mem.ram[0x30] << 8
    while a < end:
        n1, n2 = mem.ram[a], mem.ram[a + 1]
        name = chr(n1 & 127) + (chr(n2 & 127) if n2 & 127 else "")
        v = mem.ram[a + 2:a + 7]
        if not (n1 & 128) and not (n2 & 128):          # float
            e = v[0]
            if e == 0:
                val = 0.0
            else:
                mant = ((v[1] | 0x80) << 24 | v[2] << 16 | v[3] << 8 | v[4]) / 2 ** 32
                val = (-1 if v[1] & 0x80 else 1) * mant * 2 ** (e - 128)
            out[name] = val
        a += 7
    return out


if error:
    print(f"BASIC ERROR code {error[0]} in line {error[1]} after {secs:.1f}s")
    print({k: v for k, v in basvars().items()})
else:
    print(f"ran {secs:.1f}s of C64 time without a BASIC error")
print("loads:", loads, " last line:", mem.ram[0x39] | mem.ram[0x3A] << 8)
allnums = [int(l.split()[0]) for l in open("pitmedleybas.bas")]
code_lines = [n for n in allnums if n < 1000]
print("lines never reached (below 1000):", [n for n in code_lines if n not in lines_seen][:40])
import statistics
d = [(b - a) / CLOCK for a, b in zip(flips, flips[1:])]
if d:
    print("seconds per screen flip: first 10", [round(x, 2) for x in d[:10]], "median", round(statistics.median(d), 2))
tot = sum(prof.values())
nf = max(1, len(flips) - 2)
print("ms per flip by line (after the 2nd flip):", [(l, round(c / nf / CLOCK * 1000)) for l, c in sorted(prof.items(), key=lambda x: -x[1])[:14]])
if not error:
    v = basvars()
    pickle.dump({"vars": v, "screens": (bytes(mem.ram[0xC000:0xC3E8]), bytes(mem.ram[0xC400:0xC7E8])),
                 "colour": bytes(mem.colour[:1000])}, open("build/basic-final.pkl", "wb"))
pickle.dump(snaps, open("build/basic-snaps-%s.pkl" % ("ntsc" if NTSC else "pal"), "wb"))
