#!/usr/bin/env python3
"""PETSCII Pit: static checks for a C64 BASIC V2 listing (.bas).

Tokenizes each line the way the C64 does (keywords are matched anywhere
outside quotes, in ROM table order, so a variable like FORM really is
FOR + M), then checks:
  - line numbers are unique and ascending
  - every GOTO / GOSUB / THEN / ON ... GOTO|GOSUB target exists
  - variable names whose first two letters collide (BASIC only keeps two:
    RESULT and RE are the same variable)
  - variables that are read but never set anywhere (likely typos)
  - variables set but never read (dead code or typos), as information

usage: basiccheck.py file.bas [file.bas ...]
"""
import re, sys

KW = ["END", "FOR", "NEXT", "DATA", "INPUT#", "INPUT", "DIM", "READ", "LET",
      "GOTO", "RUN", "IF", "RESTORE", "GOSUB", "RETURN", "REM", "STOP", "ON",
      "WAIT", "LOAD", "SAVE", "VERIFY", "DEF", "POKE", "PRINT#", "PRINT",
      "CONT", "LIST", "CLR", "CMD", "SYS", "OPEN", "CLOSE", "GET", "NEW",
      "TAB(", "TO", "FN", "SPC(", "THEN", "NOT", "STEP", "+", "-", "*", "/",
      "^", "AND", "OR", ">", "=", "<", "SGN", "INT", "ABS", "USR", "FRE",
      "POS", "SQR", "RND", "LOG", "EXP", "COS", "SIN", "TAN", "ATN", "PEEK",
      "LEN", "STR$", "VAL", "ASC", "CHR$", "LEFT$", "RIGHT$", "MID$", "GO"]
WORDS = [k for k in KW if k[0].isalpha()]
RESERVED = {"TI", "TI$", "ST"}


def tokens(text):
    """Yield (kind, value): kw, var, num, str, sym. Spaces are dropped."""
    i = 0
    while i < len(text):
        c = text[i]
        if c == " ":
            i += 1
            continue
        if c == '"':
            j = text.find('"', i + 1)
            j = len(text) if j < 0 else j + 1
            yield ("str", text[i:j])
            i = j
            continue
        if c == "{":                       # petcat control code outside quotes
            j = text.find("}", i)
            yield ("sym", text[i:j + 1])
            i = j + 1
            continue
        kw = next((k for k in WORDS if text.startswith(k, i)), None)
        if kw:
            yield ("kw", kw)
            i += len(kw)
            if kw == "REM":
                return
            if kw == "DATA":               # rest of the statement is data
                j = i
                q = False
                while j < len(text) and (q or text[j] != ":"):
                    q ^= text[j] == '"'
                    j += 1
                i = j
            continue
        if c.isalpha():
            j = i + 1
            # a name runs on through letters/digits, but a keyword inside it
            # ends it (BASIC would tokenize that keyword)
            while j < len(text) and (text[j].isalnum()) and \
                    not any(text.startswith(k, j) for k in WORDS):
                j += 1
            if j < len(text) and text[j] in "$%":
                j += 1
            name = text[i:j]
            arr = j < len(text) and text[j] == "("
            yield ("var", name + ("(" if arr else ""))
            i = j
            continue
        if c.isdigit() or c == ".":
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] in ".E"):
                j += 1
            yield ("num", text[i:j])
            i = j
            continue
        yield ("sym", c)
        i += 1


def sig(name):
    arr = name.endswith("(")
    n = name.rstrip("(")
    suf = n[-1] if n[-1] in "$%" else ""
    core = n.rstrip("$%")
    return core[:2] + suf + ("(" if arr else "")


def check(path):
    lines = {}
    order = []
    problems, info = [], []
    for raw in open(path).read().splitlines():
        if not raw.strip():
            continue
        n, t = raw.split(" ", 1)
        n = int(n)
        if order and n <= order[-1]:
            problems.append("line %d is not after line %d" % (n, order[-1]))
        order.append(n)
        lines[n] = list(tokens(t))
    known = set(lines)
    full = {}            # significant name -> set of spellings
    setv, usev = {}, {}
    for n, tk in lines.items():
        # jump targets
        for k, (kind, val) in enumerate(tk):
            if kind == "kw" and val in ("GOTO", "GOSUB", "THEN", "RUN"):
                if val == "GO":
                    continue
                m = k + 1
                while m < len(tk) and tk[m][0] == "num":
                    tgt = int(float(tk[m][1]))
                    if tgt not in known:
                        problems.append("line %d: %s %d - no such line" % (n, val, tgt))
                    if val in ("THEN", "RUN"):
                        break
                    if m + 1 < len(tk) and tk[m + 1] == ("sym", ","):
                        m += 2
                    else:
                        break
        # variables: set if followed by '=' at a statement start, after FOR,
        # or listed after READ / GET / INPUT / DIM
        stmt_start = True
        listmode = None
        for k, (kind, val) in enumerate(tk):
            if kind == "sym" and val == ":":
                stmt_start, listmode = True, None
                continue
            if kind == "kw" and val in ("THEN", "ELSE"):
                stmt_start, listmode = True, None
                continue
            if kind == "kw" and val in ("READ", "GET", "INPUT", "INPUT#", "DIM"):
                listmode = val
                stmt_start = False
                continue
            if kind == "kw" and val == "FOR":
                stmt_start = True
                continue
            if kind == "var":
                if val.rstrip("(").rstrip("$%") in RESERVED or val in RESERVED:
                    stmt_start = False
                    continue
                s = sig(val)
                full.setdefault(s, set()).add(val)
                nxt = tk[k + 1] if k + 1 < len(tk) else None
                is_set = (stmt_start and (nxt == ("sym", "=") or val.endswith("("))) or \
                    (listmode is not None)
                if val.endswith("(") and stmt_start:
                    # array element assignment: find '=' after the matching ')'
                    depth, m = 0, k + 1
                    while m < len(tk):
                        if tk[m] == ("sym", "("):
                            depth += 1
                        elif tk[m] == ("sym", ")"):
                            depth -= 1
                            if depth == 0:
                                break
                        m += 1
                    is_set = m + 1 < len(tk) and tk[m + 1] == ("sym", "=")
                    if not is_set:
                        usev.setdefault(s, []).append(n)
                if is_set:
                    setv.setdefault(s, []).append(n)
                else:
                    usev.setdefault(s, []).append(n)
            if kind == "kw" and val == "NEXT":
                listmode = "NEXT"          # NEXT I is neither set nor read
            stmt_start = False
    for s, names in sorted(full.items()):
        plain = {x for x in names}
        if len(plain) > 1:
            problems.append("names share their first two letters: %s" % ", ".join(sorted(plain)))
    for s in sorted(usev):
        if s not in setv:
            problems.append("%s is read (lines %s) but never set" %
                            (s, ",".join(map(str, sorted(set(usev[s]))[:6]))))
    for s in sorted(setv):
        if s not in usev:
            info.append("%s is set but never read (line %s)" % (s, sorted(set(setv[s]))[0]))
    return problems, info


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        pr, inf = check(p)
        print("== %s: %d problem(s)" % (p, len(pr)))
        for x in pr:
            print("  PROBLEM", x)
        for x in inf:
            print("  info   ", x)
        bad += len(pr)
    sys.exit(1 if bad else 0)
