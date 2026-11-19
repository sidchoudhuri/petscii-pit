#!/usr/bin/env python3
"""PETSCII Pit: move fixed game text out of the BASIC games into a text bank.

The bank lives in the RAM under the BASIC ROM at $B200 (2 KB, to $B9FF).
Its source is src/texts.txt: one message per line, "NNN text", with {CODES}
as in the listings and "^" for RETURN. The build attaches the bank to the end
of the loader program (page aligned, 8 pages); the loader copies it to $B200
at start (line 386). Bartering's patterns (prg/musicshop.bin: a PAL page and
an NTSC page) follow the bank and land at $BA00/$BB00; the attached block is
12 pages, copied 3 x 4. The games reach the bank through src/asm/text.asm:

  PRINT "TEXT"            ->  SYS 1024,N          (message N ends with RETURN)
  PRINT "TEXT";X          ->  SYS 1024,N:PRINT X
  MS$="LONG MESSAGE"+X$   ->  SYS 1027,N:GOSUB 98:MS$=MS$+X$
                              98 MS$=LEFT$(BL$,PEEK(1152)):SYS 1030:RETURN

Messages are shared between the games and keep their numbers when the tool
is run again.

usage: textbank.py convert <texts.txt> <game.bas> [<game.bas> ...]
         rewrites the games in place, adds new messages to texts.txt
       textbank.py attach <texts.txt> <loader.prg> [<musicshop.bin>]
         appends the bank (and Bartering's patterns) to the built loader program
"""
import re, sys

PRINT_MIN = 6      # shortest PRINT text (in bytes) worth moving
MS_MIN = 9         # shortest status message worth moving
PAGES = 8          # bank size in pages ($B200-$B9FF)
BLOCK = 12         # attached pages ($B200-$BDFF); the loader copies 3 x 4 (line 386)
KW = ["PRINT", "GOSUB", "SYS", "THEN", "LEFT$", "MID$", "STR$", "CHR$", "PEEK"]


def nbytes(lit):
    """Bytes a literal takes once tokenized ({CODES} are one byte)."""
    return len(re.sub(r"\{[^}]*\}", "x", lit))


def split_top(s, seps):
    """Split s at seps outside quotes and parentheses; keep the separators."""
    out, cur, q, d = [], "", False, 0
    for ch in s:
        if ch == '"':
            q = not q
        if not q:
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
            elif d == 0 and ch in seps:
                out.append(cur)
                out.append(ch)
                cur = ""
                continue
        cur += ch
    out.append(cur)
    return out


def size(stmt):
    """Rough crunched size of a statement (keywords count one byte)."""
    s = re.sub(r'"[^"]*"', lambda m: '"' + "x" * nbytes(m.group(0)[1:-1]) + '"', stmt)
    s = s.replace(" ", "")
    for k in KW:
        s = s.replace(k, "\x01")
    return len(s)


class Bank:
    def __init__(self, msgs):
        self.msgs = msgs  # list of stored texts (source form, "^" = RETURN)

    def num(self, text):
        if text not in self.msgs:
            self.msgs.append(text)
        return self.msgs.index(text) + 1


def is_lit(p):
    p = p.strip()
    return len(p) >= 2 and p[0] == '"' and p[-1] == '"' and p.count('"') == 2


def print_items(args):
    """PRINT arguments -> flat list of ('L', text) / ('E', expr), or None."""
    parts = split_top(args, ";,")
    if "," in parts:
        return None
    items = []
    for p in parts[::2]:
        if p.strip() == "":
            continue
        sub = split_top(p, "+")[::2]
        if len(sub) > 1 and any(is_lit(x) for x in sub):
            for x in sub:
                items.append(("L", x.strip()[1:-1]) if is_lit(x) else ("E", x.strip()))
        elif is_lit(p):
            items.append(("L", p.strip()[1:-1]))
        else:
            items.append(("E", p.strip()))
    # merge neighbouring literals
    m = []
    for k, t in items:
        if m and k == "L" and m[-1][0] == "L":
            m[-1] = ("L", m[-1][1] + t)
        else:
            m.append((k, t))
    return m


def do_print(stmt, bank):
    m = re.match(r"^(\s*)PRINT(?!#)\s*(.*)$", stmt)
    if not m or '"' not in m.group(2):
        return None
    args = m.group(2).rstrip()
    trail = args.endswith(";")
    if trail:
        args = args[:-1]
    items = print_items(args)
    if items is None or not items:
        return None
    # literal runs worth moving become messages; the rest stays in PRINTs
    chunks = []  # ('M', text) or ('P', [items])
    for k, t in items:
        if k == "L" and nbytes(t) >= PRINT_MIN:
            chunks.append(("M", t))
        else:
            item = '"%s"' % t if k == "L" else t
            if chunks and chunks[-1][0] == "P":
                chunks[-1][1].append(item)
            else:
                chunks.append(("P", [item]))
    if not any(c[0] == "M" for c in chunks):
        return None
    out = []
    for i, (k, v) in enumerate(chunks):
        last = i == len(chunks) - 1
        if k == "M":
            text = v + ("" if (trail or not last) else "^")
            out.append("SYS 1024,%d" % bank.num(text))
        else:
            out.append("PRINT " + ";".join(v) + ("" if (last and not trail) else ";"))
    new = m.group(1) + ":".join(out)
    if size(new) >= size(stmt):
        return None
    return new


def do_ms(stmt, bank):
    m = re.match(r'^(\s*)MS\$="([^"]*)"(.*)$', stmt)
    if not m:
        return None
    lit, rest = m.group(2), m.group(3).strip()
    if nbytes(lit) < MS_MIN or nbytes(lit) > 40 or "{" in lit:
        return None
    if rest and (not rest.startswith("+") or "MS$" in rest):
        return None
    new = m.group(1) + "SYS 1027,%d:GOSUB 98" % bank.num(lit)
    if rest:
        new += ":MS$=MS$" + rest
    return new


def convert_line(body, bank):
    segs = split_top(body, ":")
    out, changed = [], False
    for s in segs[::2]:
        pre, stmt = "", s
        m = re.match(r"^(.*?\bTHEN\s*)(.*)$", s)
        if m and not m.group(1).count('"') % 2:
            pre, stmt = m.group(1), m.group(2)
        if stmt.lstrip().startswith("REM") or s.lstrip().startswith("DATA"):
            out.append(s)
            continue
        new = do_print(stmt, bank) or do_ms(stmt, bank)
        if new:
            changed = True
            out.append(pre + new)
        else:
            out.append(s)
    return ":".join(out), changed


def read_texts(path):
    msgs = []
    try:
        for l in open(path).read().split("\n"):
            if l.strip():
                n, t = l.split(" ", 1) if " " in l else (l, "")
                assert int(n) == len(msgs) + 1, "texts.txt: expected %d, got %s" % (len(msgs) + 1, n)
                msgs.append(t)
    except FileNotFoundError:
        pass
    return msgs


def write_texts(path, msgs):
    open(path, "w").write("".join("%03d %s\n" % (i + 1, t) for i, t in enumerate(msgs)))


def petscii(msgs):
    """Messages -> PETSCII bytes, using petcat for the {CODES}."""
    import subprocess, tempfile, os
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "t.bas")
        out = os.path.join(d, "t.prg")
        text = "".join('%d PRINT"%s"\n' % (i + 1, t.replace('"', "@").replace("^", ""))
                       for i, t in enumerate(msgs))
        # as in crunch.py: petcat wants lower case for the letters and codes
        text = text.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))
        open(src, "w").write(text.replace("{cbm-+}", "{CBM-+}"))
        subprocess.run(["petcat", "-w2", "-o", out, "--", src], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        b = open(out, "rb").read()[2:]
    res, p = [], 0
    for t in msgs:
        end = b.index(0, p + 4)            # each line: link, number, PRINT, "text", 0
        assert b[p + 4] == 0x99 and b[p + 5] == 34 and b[end - 1] == 34
        body = bytes(34 if c == 64 else c for c in b[p + 6:end - 1])
        if t.endswith("^"):
            body += b"\r"
        res.append(body)
        p = end + 1
    return res


def attach(texts, prg, shop=None):
    msgs = read_texts(texts)
    blob = b"".join(bytes([len(m)]) + m for m in petscii(msgs))
    assert len(blob) <= PAGES * 256, "text bank too big: %d bytes" % len(blob)
    blob += bytes(PAGES * 256 - len(blob))
    if shop:
        blob += open(shop, "rb").read()
    assert len(blob) <= BLOCK * 256
    blob += bytes(BLOCK * 256 - len(blob))
    d = bytearray(open(prg, "rb").read())
    load = d[0] | d[1] << 8
    end = load + len(d) - 2
    d += bytes((-end) % 256)
    d += blob
    open(prg, "wb").write(d)
    print("bank: %d messages, %d of %d bytes" % (len(msgs), sum(len(m) + 1 for m in petscii(msgs)), PAGES * 256))


def convert(texts, games):
    bank = Bank(read_texts(texts))
    for g in games:
        lines = open(g).read().split("\n")
        out, n = [], 0
        for l in lines:
            m = re.match(r"(\d+) (.*)$", l)
            # lines below 30 run before the loader check, so they keep their text
            if m and int(m.group(1)) >= 30 and not m.group(2).startswith(("REM", "DATA")):
                body, ch = convert_line(m.group(2), bank)
                if ch:
                    n += 1
                    l = m.group(1) + " " + body
            out.append(l)
        nums = [int(re.match(r"(\d+)", l).group(1)) for l in out if re.match(r"\d+ ", l)]
        if any("GOSUB 98" in l for l in out) and 98 not in nums:
            i = next(k for k, v in enumerate(nums) if v > 98)
            pos = [k for k, l in enumerate(out) if re.match(r"\d+ ", l)][i]
            out.insert(pos, "98 MS$=LEFT$(BL$,PEEK(1152)):SYS 1030:RETURN")
        open(g, "w").write("\n".join(out))
        print("%s: %d lines changed" % (g, n))
    write_texts(texts, bank.msgs)
    print("texts: %d messages" % len(bank.msgs))


if __name__ == "__main__":
    if sys.argv[1] == "convert":
        convert(sys.argv[2], sys.argv[3:])
    else:
        attach(*sys.argv[2:5])
