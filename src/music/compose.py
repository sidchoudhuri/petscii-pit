#!/usr/bin/env python3
"""Generates music.asm for PETSCII Pit (original compositions).

Song 0 "Dungeoneering" (A minor, 6 frames/row): intro(4) | A(8) | B(8) | A(8) | loop -> B
Song 1 "Fight" (E phrygian/diminished, 4 frames/row): 4 bars, loops.

Data is pattern based: each voice has an order list of (pattern, transpose)
entries; a pattern is a list of 3-byte events (instrument, note, frames),
note 0 = rest (never transposed). Pattern end = $FF.
Order list end = $FF, <index of the entry to loop to>.
"""
import os

NAMES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
         "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def n(s):
    """'A4' -> note index (C-0 = 0, A4 = 57)."""
    return NAMES[s[:-1]] + int(s[-1]) * 12


# NTSC=1 builds the NTSC version: notes tuned for the NTSC clock, and every
# bar stretched from 96 to 115 frames (Dungeoneering) / 64 to 77 frames
# (Fight) so 60 Hz plays at the PAL tempo.
NTSC = bool(os.environ.get("NTSC"))
CLOCK = 1022727 if NTSC else 985248


# ---------------------------------------------------------------- freq table
def freq_table():
    out = []
    for i in range(96):
        f = 440.0 * 2 ** ((i - 57) / 12)
        out.append(min(0xFFFF, round(f * 16777216 / CLOCK)))
    return out


# ---------------------------------------------------------------- instruments
LEAD, ARP, BASS, KICK, SNARE, HAT, DIM, GRIND = range(8)
NINST = 8
ABS = 0x80

# wave program: list of (waveform byte incl. gate, note) ; last entry loops
# to the index given by 'loop' (relative to the instrument's program start)
PROGRAMS = {
    LEAD:  ([(0x41, 0)], 0),
    ARP:   ([(0x41, 0), (0x41, 12), (0x41, 24)], 0),
    BASS:  ([(0x81, 24), (0x41, 0)], 1),
    KICK:  ([(0x11, ABS | 13), (0x81, ABS | 59), (0x41, ABS | 44),
             (0x41, ABS | 42), (0x40, ABS | 40), (0x80, ABS | 66),
             (0x80, ABS | 51)], 6),
    SNARE: ([(0x81, ABS | 70), (0x41, ABS | 52), (0x41, ABS | 48),
             (0x81, ABS | 64), (0x80, ABS | 62)], 4),
    HAT:   ([(0x81, ABS | 90), (0x80, ABS | 90)], 1),
    # fight: diminished-seventh shimmer (0, 3, 6, 9 semitones, one per frame)
    DIM:   ([(0x41, 0), (0x41, 3), (0x41, 6), (0x41, 9)], 0),
    # fight: sawtooth bass with a noise bite on the attack
    GRIND: ([(0x81, 36), (0x21, 0)], 1),
}

# ad, sr, pw start hi, pw speed (signed), pw min hi, pw max hi,
# vib delay, vib depth, vib speed
INST = {
    LEAD:  (0x08, 0xA9, 0x08, 0x20, 0x04, 0x0E, 12, 0x18, 6),
    ARP:   (0x0A, 0x8A, 0x08, 0x21, 0x02, 0x0E, 0, 0, 2),
    BASS:  (0x00, 0xD9, 0x08, 0x40, 0x06, 0x0E, 0, 0, 2),
    KICK:  (0x00, 0xE8, 0x08, 0x00, 0x08, 0x08, 0, 0, 2),
    SNARE: (0x00, 0xE9, 0x08, 0x00, 0x08, 0x08, 0, 0, 2),
    HAT:   (0x00, 0xA3, 0x08, 0x00, 0x08, 0x08, 0, 0, 2),
    DIM:   (0x00, 0xA8, 0x02, 0x50, 0x02, 0x0D, 8, 0x30, 3),
    GRIND: (0x00, 0xD8, 0x08, 0x00, 0x08, 0x08, 0, 0, 2),
}

# Music level under the game's sound effects: each instrument's sustain level
# is scaled by MUSIC_LEVEL (1.0 = full) and its decay capped at MAX_DECAY so
# notes fall to that quieter level quickly. The SID master volume is shared
# with the effects, so the music is turned down through the envelopes.
MUSIC_LEVEL = 0.1
MAX_DECAY = 0
if os.environ.get("FULL_VOLUME"):     # stand-alone .sid: original envelopes
    MUSIC_LEVEL, MAX_DECAY = 1.0, 15


# In-game mix ("Q"): every note fades in and out a little (attack 1 = 8 ms,
# decay 2 = 48 ms) so nothing clicks, and the pulse instruments use a narrow
# pulse; the lead is a triangle (see PROGRAMS below) and build.py runs the
# music through the low-pass filter. Stand-alone .sid files keep the originals.
INGAME = not os.environ.get("FULL_VOLUME")
SOFT_ATTACK, SOFT_DECAY = 1, 2


def mixed(i):
    ad, sr = INST[i][0], INST[i][1]
    ad = (ad & 0xF0) | min(ad & 0x0F, MAX_DECAY)
    sus = int((sr >> 4) * MUSIC_LEVEL + 0.5)
    sr = (sus << 4) | (sr & 0x0F)
    rest = list(INST[i][2:])
    if INGAME:
        ad = (SOFT_ATTACK << 4) | SOFT_DECAY
        if i in (ARP, BASS, DIM, GRIND):        # narrow pulse, gentle sweep
            rest[0:4] = [1, 0x08, 1, 2]
    return (ad, sr) + tuple(rest)


# ---------------------------------------------------------------- patterns
PATTERNS = []          # list of (name, [(inst, note, frames)])
PIDX = {}


def ntsc_timing(name, events):
    """Re-time a bar-aligned pattern for 60 Hz: row r of a bar starts at
    round(r * barframes / 16), so every bar keeps a whole number of frames."""
    sp = 4 if name.startswith("f_") else (8 if name.startswith("l_") else 6)
    bar = round(16 * sp * 60 / 50)
    pos = lambda r: (r // 16) * bar + round((r % 16) * bar / 16)
    out, row = [], 0
    for ins, note, frames in events:
        assert frames % sp == 0
        rows = frames // sp
        out.append((ins, note, pos(row + rows) - pos(row)))
        row += rows
    assert row % 16 == 0, name
    return out


def pattern(name, events):
    """events: (inst, note, frames); frames > 240 are split."""
    if NTSC:
        events = ntsc_timing(name, events)
    out = []
    for ins, note, frames in events:
        while frames > 0:
            f = min(frames, 240)
            out.append((ins, note, f))
            frames -= f
    PIDX[name] = len(PATTERNS)
    PATTERNS.append((name, out))


# ---- song 0: Dungeoneering (6 frames per row)
SP0 = 6
CH_INTRO = ["A", "F", "C", "G"]
CH_A = ["A", "F", "C", "G", "A", "F", "C", "E"]
CH_B = ["D", "A", "F", "E", "D", "A", "F", "E"]


def bass_root(root):
    r2 = n(root + "2")
    if r2 < n("E2"):          # keep the bass in a comfortable register
        r2 += 12
    return r2


BASS_BASE = bass_root("A")    # pattern written on A, others by transpose
pattern("bass", [(BASS, BASS_BASE + (12 if i % 2 else 0), 2 * SP0)
                 for i in range(8)])


def drums(busy):
    k, s, h = KICK, SNARE, HAT
    pat = [k, h, s, h, k, k if busy else h, s, h]
    return [(i, 1, 2 * SP0) for i in pat]


pattern("drums", drums(False))
pattern("drums_busy", drums(True))

LEAD_A = [
    [("A4", 4), ("C5", 2), ("E5", 2), ("D5", 2), ("C5", 2), ("A4", 4)],
    [("F4", 2), ("A4", 2), ("C5", 4), ("A4", 2), ("C5", 2), ("F5", 4)],
    [("E5", 6), ("D5", 2), ("C5", 4), ("G4", 4)],
    [("B4", 4), ("D5", 4), ("G5", 6), (None, 2)],
    [("A5", 4), ("G5", 2), ("E5", 2), ("C5", 4), ("E5", 4)],
    [("F5", 4), ("E5", 2), ("C5", 2), ("A4", 4), ("C5", 4)],
    [("G5", 4), ("E5", 4), ("C5", 2), ("D5", 2), ("E5", 4)],
    [("D5", 4), ("B4", 4), ("G#4", 8)],
]
ARP_B = [
    ["D5", "F5", "A5", "F5", "D5"],
    ["C5", "E5", "A5", "E5", "C5"],
    ["C5", "F5", "A5", "F5", "C5"],
    ["B4", "E5", "G#5", "E5", "B4"],
    ["D5", "F5", "A5", "F5", "D5"],
    ["C5", "E5", "A5", "E5", "C5"],
    ["C5", "F5", "A5", "C6", "A5"],
    ["G#4", "B4", "E5", "B4", "E5"],
]
ARP_RHYTHM = [4, 4, 2, 2, 4]

pattern("lead_rest", [(LEAD, 0, 16 * 4 * SP0)])
pattern("lead_a", [(LEAD, n(nm) if nm else 0, r * SP0)
                   for bar in LEAD_A for nm, r in bar])
pattern("arp_b", [(ARP, n(nm) - 12, r * SP0)          # arp adds +12/+24
                  for bar in ARP_B for nm, r in zip(bar, ARP_RHYTHM)])


def tr(root):
    return bass_root(root) - BASS_BASE


SONG0 = {
    "drums": [("drums", 0)] * 12 + ["LOOP"] + [("drums_busy", 0)] * 8
             + [("drums", 0)] * 8,
    "bass": [("bass", tr(c)) for c in CH_INTRO + CH_A] + ["LOOP"]
            + [("bass", tr(c)) for c in CH_B + CH_A],
    "lead": [("lead_rest", 0), ("lead_a", 0), "LOOP", ("arp_b", 0), ("lead_a", 0)],
}

# ---- song 1: Fight (4 frames per row, 4 bars, loops)
SP1 = 4
# heartbeat: thump-thump ... with a noise crack at the end of every 2nd bar
pattern("f_beat", [(KICK, 1, 2 * SP1), (KICK, 1, 4 * SP1), (0, 0, 10 * SP1)])
pattern("f_beat_crack", [(KICK, 1, 2 * SP1), (KICK, 1, 4 * SP1), (0, 0, 4 * SP1),
                         (SNARE, 1, 2 * SP1), (SNARE, 1, 2 * SP1),
                         (SNARE, 1, 2 * SP1)])
# grinding bass: E pulsing in 16ths, leaning on F (a semitone up)
E1 = n("E1")
pattern("f_grind", [(GRIND, E1 + d, SP1) for d in
                    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1]])
# diminished shimmer, slowly sinking chromatically
pattern("f_dim", [(DIM, n("E4"), 16 * SP1)])

SONG1 = {
    "drums": [("f_beat", 0), ("f_beat_crack", 0)] * 2,
    "bass": [("f_grind", 0), ("f_grind", 0), ("f_grind", 1), ("f_grind", 0)],
    "lead": [("f_dim", 0), ("f_dim", -1), ("f_dim", 1), ("f_dim", -2)],
}

# ---- song 2: Lamenting (8 frames/row, 4 bars, loops) - a slow, sparse
# echo of Dungeoneering's opening phrase over Am - F - Dm - E
SP2 = 8
pattern("l_beat", [(KICK, 1, 2 * SP2), (0, 0, 14 * SP2)])          # one soft thud a bar
pattern("l_bass", [(BASS, n("A2"), 16 * SP2)])                     # held root, transposed
pattern("l_lead", [(LEAD, n(nm) if nm else 0, r * SP2) for nm, r in [
    ("A4", 4), ("C5", 4), ("E5", 6), ("D5", 2),
    ("C5", 8), ("A4", 8),
    ("F4", 4), ("A4", 4), ("D5", 6), ("C5", 2),
    ("B4", 8), ("G#4", 6), (None, 2)]])

SONG2 = {
    "drums": [("l_beat", 0)] * 4,
    "bass": [("l_bass", 0), ("l_bass", -4), ("l_bass", 5), ("l_bass", -5)],
    "lead": [("l_lead", -12)],
}
SONGS = [SONG0, SONG1, SONG2]
if INGAME:
    PROGRAMS[LEAD] = ([(0x11, 0)], 0)           # triangle lead in the game


# ---------------------------------------------------------------- output
def order_bytes(ol):
    out, loop = [], 0
    for e in ol:
        if e == "LOOP":
            loop = len(out)
            continue
        p, t = e
        out += [PIDX[p], t & 255]
    return out + [0xFF, loop]


def voice_frames(ol):
    tot, loop = 0, 0
    for e in ol:
        if e == "LOOP":
            loop = tot
            continue
        tot += sum(f for _, _, f in PATTERNS[PIDX[e[0]]][1])
    return tot, loop


def main():
    for si, song in enumerate(SONGS):
        lens = {v: voice_frames(song[v]) for v in ("drums", "bass", "lead")}
        assert len(set(lens.values())) == 1, (si, lens)
        tot, loop = next(iter(lens.values()))
        print(f"song {si}: {tot} frames ({tot / 50:.1f}s), loop at frame {loop}")
    for name, ev in PATTERNS:
        for ins, note, f in ev:
            assert 3 <= f <= 240 and ins < NINST, (name, ins, f)

    L = ["; PETSCII Pit music data (Dungeoneering + Fight)",
         "; generated by compose.py - do not edit by hand", ""]
    ft = freq_table()
    L.append("freqlo  !byte " + ",".join(f"${v & 255:02x}" for v in ft))
    L.append("freqhi  !byte " + ",".join(f"${v >> 8:02x}" for v in ft))

    wave, wnote, wnext, start = [], [], [], {}
    for i in range(NINST):
        prog, lp = PROGRAMS[i]
        base = len(wave)
        start[i] = base
        for j, (w, nt) in enumerate(prog):
            wave.append(w)
            wnote.append(nt)
            wnext.append(base + j + 1 if j + 1 < len(prog) else base + lp)
    L.append("wt_wave !byte " + ",".join(f"${v:02x}" for v in wave))
    L.append("wt_note !byte " + ",".join(f"${v:02x}" for v in wnote))
    L.append("wt_next !byte " + ",".join(f"${v:02x}" for v in wnext))
    L.append("i_wt    !byte " + ",".join(f"${start[i]:02x}" for i in range(NINST)))
    cols = ["i_ad", "i_sr", "i_pw", "i_pws", "i_pwmin", "i_pwmax",
            "i_vdel", "i_vdep", "i_vspd"]
    for c, name in enumerate(cols):
        L.append(f"{name:<8}!byte " + ",".join(
            f"${mixed(i)[c] & 255:02x}" for i in range(NINST)))

    # song table: order list address per song and voice
    labels = [f"o{s}_{v}" for s in range(len(SONGS)) for v in ("drums", "bass", "lead")]
    L.append("songlo  !byte " + ",".join(f"<{l}" for l in labels))
    L.append("songhi  !byte " + ",".join(f">{l}" for l in labels))
    for s, song in enumerate(SONGS):
        for v in ("drums", "bass", "lead"):
            L.append(f"o{s}_{v} !byte " + ",".join(str(b) for b in order_bytes(song[v])))

    L.append("patlo   !byte " + ",".join(f"<p_{nm}" for nm, _ in PATTERNS))
    L.append("pathi   !byte " + ",".join(f">p_{nm}" for nm, _ in PATTERNS))
    for nm, ev in PATTERNS:
        L.append(f"p_{nm}")
        for ins, note, f in ev:
            L.append(f"        !byte {ins},{note},{f}")
        L.append("        !byte $ff")

    open("music.asm", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
