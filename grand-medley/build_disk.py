#!/usr/bin/env python3
"""Tokenizes pitmedley.bas and builds pitmedley.d64 with the directory art.

Disk order: PITMEDLEY (BASIC shell, first so LOAD"*",8 finds it), blank line,
player glyph, blank line, the data files, then C64.M0N.DE, the chest glyph
and M0NDE.ITCH.IO. Art lines are 0-block DEL entries, two CBM-+ checkerboard
characters per pixel, shifted one column left. Don't VALIDATE this disk:
that removes the art lines.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")

KEYWORDS = ["END", "FOR", "NEXT", "DATA", "INPUT#", "INPUT", "DIM", "READ", "LET",
            "GOTO", "RUN", "IF", "RESTORE", "GOSUB", "RETURN", "REM", "STOP", "ON",
            "WAIT", "LOAD", "SAVE", "VERIFY", "DEF", "POKE", "PRINT#", "PRINT", "CONT",
            "LIST", "CLR", "CMD", "SYS", "OPEN", "CLOSE", "GET", "NEW", "TAB(", "TO",
            "FN", "SPC(", "THEN", "NOT", "STEP", "+", "-", "*", "/", "^", "AND", "OR",
            ">", "=", "<", "SGN", "INT", "ABS", "USR", "FRE", "POS", "SQR", "RND", "LOG",
            "EXP", "COS", "SIN", "TAN", "ATN", "PEEK", "LEN", "STR$", "VAL", "ASC",
            "CHR$", "LEFT$", "RIGHT$", "MID$", "GO"]
TOKENS = {k: 0x80 + i for i, k in enumerate(KEYWORDS)}
# longest first so INPUT# beats INPUT, PRINT# beats PRINT
ORDER = sorted(KEYWORDS, key=len, reverse=True)
CODES = {"WHT": 5, "CLR": 147, "GRY3": 155}


def tokenize_line(text):
    out = bytearray()
    i, quote, rem, data = 0, False, False, False
    while i < len(text):
        ch = text[i]
        if ch == "{":
            j = text.index("}", i)
            out.append(CODES[text[i + 1:j]])
            i = j + 1
            continue
        if ch == '"':
            quote = not quote
            out.append(34)
            i += 1
            continue
        if quote or rem:
            out.append(ord(ch))
            i += 1
            continue
        if data:
            if ch == ":":
                data = False
            out.append(ord(ch))
            i += 1
            continue
        if ch == " ":
            i += 1          # spaces outside quotes are dropped
            continue
        for kw in ORDER:
            if text.startswith(kw, i):
                out.append(TOKENS[kw])
                i += len(kw)
                rem = kw == "REM"
                data = kw == "DATA"
                break
        else:
            out.append(ord(ch))
            i += 1
    return bytes(out)


def tokenize(path, base=0x0801):
    out = bytearray([base & 255, base >> 8])
    addr = base
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        m = re.match(r"(\d+)\s(.*)", line)
        num, body = int(m.group(1)), tokenize_line(m.group(2))
        nxt = addr + 4 + len(body) + 1
        out += bytes([nxt & 255, nxt >> 8, num & 255, num >> 8]) + body + b"\0"
        addr = nxt
    out += b"\0\0"
    return bytes(out)


# ---------------------------------------------------------------- d64
SPT = [21] * 17 + [19] * 7 + [18] * 6 + [17] * 5


def off(t, s):
    return (sum(SPT[:t - 1]) + s) * 256


def pet(s, n=16, pad=0xA0):
    b = bytes(ord(c) for c in s.upper())
    return (b + bytes([pad] * n))[:n]


class Disk:
    def __init__(self, name, did):
        self.d = bytearray(174848)
        self.free = {t: set(range(SPT[t - 1])) for t in range(1, 36)}
        self.free[18] -= {0, 1}
        self.entries = []
        self.name, self.did = name, did

    def alloc_track_order(self):
        for t in list(range(17, 0, -1)) + list(range(19, 36)):
            yield t

    def add_file(self, name, data):
        chunks = [data[i:i + 254] for i in range(0, len(data), 254)] or [b""]
        secs = []
        tracks = self.alloc_track_order()
        t = next(tracks)
        s = 0
        for _ in chunks:
            while not self.free[t]:
                t = next(tracks)
                s = 0
            cand = sorted(self.free[t], key=lambda x: ((x - s) % SPT[t - 1]))
            s = cand[0]
            self.free[t].discard(s)
            secs.append((t, s))
            s = (s + 10) % SPT[t - 1]
        for k, (chunk, (t, s)) in enumerate(zip(chunks, secs)):
            p = off(t, s)
            if k + 1 < len(secs):
                self.d[p:p + 2] = bytes(secs[k + 1])
            else:
                self.d[p:p + 2] = bytes([0, len(chunk) + 1])
            self.d[p + 2:p + 2 + len(chunk)] = chunk
        e = bytearray(30)
        e[0] = 0x82
        e[1], e[2] = secs[0]
        e[3:19] = pet(name)
        e[28], e[29] = len(secs) & 255, len(secs) >> 8
        self.entries.append(bytes(e))

    def add_art(self, name16):
        e = bytearray(30)
        e[0] = 0x80          # DEL, 0 blocks
        e[1], e[2] = 18, 0
        e[3:19] = name16
        self.entries.append(bytes(e))

    def finish(self):
        dirsecs = [1, 4, 7, 10, 13, 16, 2, 5, 8, 11, 14, 17, 3, 6, 9, 12, 15, 18]
        need = (len(self.entries) + 7) // 8
        used = dirsecs[:need]
        self.free[18] -= set(used)
        for k, s in enumerate(used):
            p = off(18, s)
            if k + 1 < need:
                self.d[p:p + 2] = bytes([18, used[k + 1]])
            else:
                self.d[p:p + 2] = bytes([0, 255])
            for i, e in enumerate(self.entries[k * 8:k * 8 + 8]):
                self.d[p + i * 32 + 2:p + i * 32 + 32] = e
        b = off(18, 0)
        self.d[b:b + 4] = bytes([18, 1, 0x41, 0])
        for t in range(1, 36):
            fr = self.free[t]
            bits = 0
            for s in fr:
                bits |= 1 << s
            self.d[b + 4 * t:b + 4 * t + 4] = bytes([len(fr), bits & 255, bits >> 8 & 255, bits >> 16 & 255])
        self.d[b + 0x90:b + 0xA0] = pet(self.name)
        self.d[b + 0xA0:b + 0xA2] = b"\xa0\xa0"
        self.d[b + 0xA2:b + 0xA4] = pet(self.did, 2)
        self.d[b + 0xA4] = 0xA0
        self.d[b + 0xA5:b + 0xA7] = b"2A"
        self.d[b + 0xA7:b + 0xAB] = b"\xa0" * 4
        return bytes(self.d)


PIX = 0xA6                      # CBM-+ checkerboard
PLAYER = [28, 20, 46, 58, 50, 28, 20, 54]
CHEST = [0, 62, 75, 127, 69, 69, 127, 0]
BLANK = bytes([0x20] * 16)


def glyph_lines(g):
    lines = []
    for b in g:
        row = [PIX if b & (128 >> (i // 2)) else 0x20 for i in range(16)]
        lines.append(bytes(row[1:] + [0x20]))      # one column left
    return lines


def main():
    # machine code version: the loader from loader.asm is the first file
    prg = open(os.path.join(B, "pitmedley.prg"), "rb").read()
    with_basic = "--basic" in sys.argv

    def sidprg(path):
        d = open(path, "rb").read()
        return d[d[7]:]          # embedded load address $9300 + data

    files = [
        ("PITMEDLEY", prg),
        ("MEDLEYPAL", sidprg(os.path.join(HERE, "src", "petscii-pit-medley-pal.sid"))),
        ("MEDLEYNTSC", sidprg(os.path.join(HERE, "src", "petscii-pit-medley-ntsc.sid"))),
        ("DEMOCODE", open(os.path.join(B, "democode.prg"), "rb").read()),
        ("DEMOHI", bytes([0x00, 0xA0]) + open(os.path.join(B, "hi.bin"), "rb").read()),
        ("DEMODNG", bytes([0x00, 0xE0]) + open(os.path.join(B, "dng.bin"), "rb").read()),
    ]
    if with_basic:
        files.append(("PITMEDLEYBAS", tokenize(os.path.join(HERE, "pitmedleybas.bas"))))
    disk = Disk("PIT MEDLEY", "01")
    disk.add_file(*files[0])
    disk.add_art(BLANK)
    for line in glyph_lines(PLAYER):
        disk.add_art(line)
    disk.add_art(BLANK)
    for f in files[1:]:
        disk.add_file(*f)
    disk.add_art(BLANK)
    disk.add_art(pet("C64.M0N.DE", 16, 0x20))
    for line in glyph_lines(CHEST):
        disk.add_art(line)
    disk.add_art(pet("M0NDE.ITCH.IO", 16, 0x20))
    open(os.path.join(B, "pitmedley.d64"), "wb").write(disk.finish())
    for name, data in files:
        open(os.path.join(B, name.lower() + ".prg"), "wb").write(data)
    print("files:", ", ".join(f"{n} {(len(d) + 253) // 254} blocks" for n, d in files))


if __name__ == "__main__":
    main()
