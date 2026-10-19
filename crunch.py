#!/usr/bin/env python3
"""PETSCII Pit: crunch a .bas listing for the .prg build.

Removes every space outside quotes and the text of REMs (a REM-only line keeps
its line number and a bare REM, so jumps to it still work; a ":REM ..." tail
is dropped). The readable .bas stays the source; only the .prg is crunched.

Safety check: the original and the crunched listing are both tokenized with
petcat, and every line must give the same bytes once the original's spaces
(outside quotes) and REM texts are taken out. If a removed space would have
joined a variable name and a keyword into a different token, the build stops.

usage: crunch.py <in.bas> <out.prg>
"""
import subprocess, sys, tempfile, os


def crunch_line(text):
    out, inq, i = [], False, 0
    while i < len(text):
        ch = text[i]
        if ch == '"':
            inq = not inq
        if not inq:
            if text[i:i + 3] == "REM":
                head = "".join(out).rstrip(":")
                return head if head else "REM"
            if text[i:i + 4] == "DATA":
                # DATA items: keep them as written, but drop spaces outside quotes
                pass
            if ch == " ":
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def crunch(src):
    lines = []
    for l in src.splitlines():
        if not l.strip():
            continue
        n, t = l.split(" ", 1)
        c = crunch_line(t)
        if c == "":
            c = "REM"
        lines.append(n + " " + c)
    return "\n".join(lines) + "\n"


def tokenize(text):
    lower = text.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))
    lower = lower.replace("{cbm-+}", "{CBM-+}")
    with tempfile.NamedTemporaryFile("w", suffix=".bas", delete=False) as f:
        f.write(lower)
        name = f.name
    out = name + ".prg"
    subprocess.run(["petcat", "-w2", "-o", out, "--", name], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    b = open(out, "rb").read()
    os.unlink(name)
    os.unlink(out)
    return b


def lines_of(prg):
    a, i, res = 0x801, 2, {}
    while True:
        n = prg[i] | prg[i + 1] << 8
        if n == 0:
            return res
        ln = prg[i + 2] | prg[i + 3] << 8
        res[ln] = prg[i + 4:i + (n - a) - 1]
        i += n - a
        a = n


def stripped(body):
    out, inq = bytearray(), False
    for x in body:
        if x == 0x22:
            inq = not inq
        if not inq and x == 0x8F:          # REM: keep the token, drop its text
            while out and out[-1] in (0x20, 0x3A):
                out.pop()
            if not out:
                out.append(0x8F)
            return bytes(out)
        if not inq and x == 0x20:
            continue
        out.append(x)
    return bytes(out)


def main():
    src = open(sys.argv[1]).read()
    cr = crunch(src)
    a = lines_of(tokenize(src))
    b_prg = tokenize(cr)
    b = lines_of(b_prg)
    assert a.keys() == b.keys(), "line numbers differ"
    bad = [n for n in a if stripped(a[n]) != b[n]]
    if bad:
        raise SystemExit("crunch changed the meaning of lines: %s" % bad[:10])
    longest = max(len(v) for v in b.values()) + 5
    open(sys.argv[2], "wb").write(b_prg)
    print("%s: %d -> %d bytes (longest line %d)" % (os.path.basename(sys.argv[2]),
          len(tokenize(src)), len(b_prg), longest))


if __name__ == "__main__":
    main()
