#!/usr/bin/env python3
"""PETSCII Pit Grand Medley demo - BASIC version generator.

Writes pitmedleybas.bas: the whole demo in BASIC V2, with everything worked
out here ahead of time and written into the listing as strings and DATA.
Only the music is machine code: the medley's own player, started with
SYS 38662 like the game does.

Same show as the machine code version, at BASIC speed, a character at a time:
dancers with name labels (2.5x, 2 dance frames), the scrollers, the portrait
coming in, the colour wipe, the shrink, the two small dancer bands, the
portrait shrinking away and the dungeon strip.

Memory: BASIC $0801-$92FF, music $9300, screens $C000/$C400 (shown
alternately, like the PETSCII Pit title screen), font $C800 (ROM copy +
block shapes + game glyphs).
"""
import os
import gen
import dungeon as D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build")

# ---------------------------------------------------------------- font
# quarter-block shapes go into printable codes the texts don't use, so the
# dancer and portrait strings are plain characters in the listing
QCODES = [33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 59, 60, 61, 62, 63]
SHAPES = [q for q in sorted(gen.QUAD) if q != (0, 0, 0, 0)]
BQUAD = {(0, 0, 0, 0): 32}
BQUAD.update(dict(zip(SHAPES, QCODES)))
DBASE = 99                       # dungeon glyph g (1-21) -> screen code 99+g


def quad_bits(q):
    tl, tr, bl, br = q
    top = (0xF0 if tl else 0) | (0x0F if tr else 0)
    bot = (0xF0 if bl else 0) | (0x0F if br else 0)
    return [top] * 4 + [bot] * 4


def glyph_data():
    out = []
    for q, code in zip(SHAPES, QCODES):
        out.append([code] + quad_bits(q))
    for g in range(1, 22):
        code = D.GAME_CODES[g]
        if code in gen.GLYPHS:
            bits = [sum(b << (7 - x) for x, b in enumerate(row)) for row in gen.GLYPHS[code]]
        else:
            bits = list(gen.ROM[code * 8:code * 8 + 8])
        out.append([DBASE + g] + bits)
    return out


def lchar(code):
    """screen code -> character in the listing"""
    if 1 <= code <= 26:
        return chr(64 + code)
    if 32 <= code <= 63 and code != 34:
        return chr(code)
    raise ValueError(code)


# ---------------------------------------------------------------- dancers
PH = 2                           # dance frames
BW = gen.BIG_LINE + 40           # 232


def big_cells_b(bits):
    cells = []
    for cy in range(20):
        row = []
        for cx in range(20):
            q = tuple(bits[(cy * 2 + dy) // 5][(cx * 2 + dx) // 5] for dy in (0, 1) for dx in (0, 1))
            row.append(BQUAD[q])
        cells.append(row)
    return cells


def big_strings():
    rows = {}
    for p in range(PH):
        grid = [[32] * BW for _ in range(20)]
        for i, frames in enumerate(gen.LINEUP):
            cells = big_cells_b(gen.GLYPHS[frames[p]])
            for copy in (0, gen.BIG_LINE):
                x0 = copy + i * gen.BIG_SLOT + 2
                for y in range(20):
                    for x in range(20):
                        if x0 + x < BW:
                            grid[y][x0 + x] = cells[y][x]
        for i, name in enumerate(gen.NAMES):
            for copy in (0, gen.BIG_LINE):
                x = copy + i * gen.BIG_SLOT + 2 + (20 - len(name)) // 2
                for j, ch in enumerate(name):
                    if x + j < BW:
                        grid[19][x + j] = gen.screencode(ch)
        for r in range(20):
            rows[(p, r)] = "".join(lchar(c) for c in grid[r])
    labels = [(i * gen.BIG_SLOT + 2 + (20 - len(n)) // 2 + 1, len(n)) for i, n in enumerate(gen.NAMES)]
    return rows, labels


def small_strings():
    rows = {}
    W = 40 + gen.SM_LINE + 40 + 40
    for p in range(PH):
        grid = [[32] * W for _ in range(8)]
        for i, frames in enumerate(gen.LINEUP):
            b = gen.GLYPHS[frames[p]]
            for copy in (40, 40 + gen.SM_LINE):
                x0 = copy + i * gen.SM_SLOT + 1
                for y in range(8):
                    for x in range(8):
                        if b[y][x] and x0 + x < 40 + gen.SM_LINE + 40:
                            grid[y][x0 + x] = BQUAD[(1, 1, 1, 1)]
        for r in range(8):
            rows[(p, r)] = "".join(lchar(c) for c in grid[r])
    return rows


# ---------------------------------------------------------------- portrait
QCAND = [(BQUAD[q], [quad_bits(q)[y] >> (7 - x) & 1 for y in range(8) for x in range(8)])
         for q in gen.QUAD]


def to_quads(img, w, h):
    small = img.resize((8 * w, 8 * h), gen.Image.LANCZOS).load()
    out = []
    for cy in range(h):
        row = []
        for cx in range(w):
            cell = [small[cx * 8 + x, cy * 8 + y] / 255 for y in range(8) for x in range(8)]
            best = min(QCAND, key=lambda cb: sum((a - b) ** 2 for a, b in zip(cell, cb[1])))
            row.append(best[0])
        out.append(row)
    return out


def portrait():
    _, img = gen.read_portrait()
    sizes = list(zip(gen.SHRINK_W, gen.SHRINK_H))            # 20x22 .. 8x8
    frames = [to_quads(img, w, h) for w, h in sizes]
    outro = ["".join(lchar(c) for c in [32] * 10 + frames[0][r] + [32] * 10) for r in range(22)]

    def records(sizes, frames):
        recs = []
        for k in range(1, len(sizes)):
            pw, ph = sizes[k - 1]
            w, h = sizes[k]
            pt, pl = gen.box(pw, ph)
            t, l = gen.box(w, h) if w else (pt, pl)
            rows = []
            for r in range(ph):
                s = ""
                for c in range(pw):
                    y, x = pt + r - t, pl + c - l
                    s += lchar(frames[k][y][x]) if 0 <= y < h and 0 <= x < w else " "
                rows.append(s)
            recs.append((pt, pl, rows))
        return recs

    rec1 = records(sizes, frames)
    s2 = [(8, 8)] + [(n, n) for n in range(6, 0, -1)] + [(0, 0)]
    f2 = [frames[-1]] + [to_quads(img, w, h) for w, h in s2[1:-1]] + [[]]
    rec2 = records(s2, f2)
    return outro, rec1, rec2


# ---------------------------------------------------------------- BASIC text
COLOURS = {1: 5, 15: 155, 12: 152, 11: 151}
STRIDE_BIG = BW + 6              # REM line: link, number, REM token, data, 0
STRIDE_SM = 200 + 6
STRIDE_O = 40 + 6
CSTRIP = 52224                   # $CC00 label colour strip (232 bytes)
CBUF = {11: 52480, 12: 52520, 15: 52560, 1: 52600}   # 40-byte colour rows
SPBUF = 52640                    # 40 spaces


def program(addr=None):
    """addr: addresses of the REM data lines, filled in on the second pass"""
    big, labels = big_strings()
    small = small_strings()
    outro, rec1, rec2 = portrait()
    lv = D.levels()
    glyphs = glyph_data()
    top = gen.TOP_TEXT
    bottom = gen.BOTTOM_TEXT
    assert len(top) == 56 and len(bottom) == 275, (len(top), len(bottom))
    kpal = round(gen.song_frames(os.path.join(gen.SRC, "petscii-pit-medley-pal.sid")) * 60 / (985248 / (312 * 63)))
    kntsc = round(gen.song_frames(os.path.join(gen.SRC, "petscii-pit-medley-ntsc.sid")) * 60 / (1022727 / (263 * 65)))
    a = addr or {}

    L = []

    def add(text, label=None):
        L.append((label, text))

    def cp(src, dst, n):
        """BASIC for the ROM block copy (Eyvind's quick memcopy): n bytes"""
        return (f"S={src}:D={dst}:N={n}:GOSUB ~CP")

    add("REM PETSCII PIT - GRAND MEDLEY - BASIC VERSION BY M0NDE - HTTPS://M0N.DE")
    add("GOTO ~INIT")
    add("REM COPY N BYTES FROM S TO D WITH THE BASIC ROM BLOCK MOVE (EYVIND EBSEN)", "CP")
    add("SH=INT(S*Q8):POKE K2,S-V*SH:POKE K3,SH:DH=INT(D*Q8):POKE K0,D-V*DH:POKE K1,DH:POKE K4,O:POKE K5,N:SYS Y:RETURN")
    # ------------------------------------------------ main show (kept near the top: fast GOTOs)
    add("REM DANCERS WHILE THE MEDLEY PLAYS", "DANCE")
    add("BF=1-BF:DB=49152+1024*BF:GOSUB ~TEXT:POKE K2,P-O:SH=BG(F):D=DB+80:GOSUB ~PTRD")
    add("FOR R=O TO 20:POKE K3,SH:POKE K0,DL:POKE K1,DH:POKE K4,O:POKE K5,Z:SYS Y:SH=SH+O:DL=DL+Z:IF DL>U THEN DL=DL-V:DH=DH+O")
    add("NEXT R")
    add(f"POKE 53272,2+16*BF:{cp('CS+P-1', 56136, 40)}:P=P+2:IF P>192 THEN P=P-192")
    add("F=1-F:IF TI<K THEN ~DANCE")
    add("REM THE PORTRAIT COMES IN")
    add("T=0")
    add("BF=1-BF:DB=49152+1024*BF:GOSUB ~TEXT:T=T+2:LM=40-T:GOSUB ~OROWS", "OUTRO")
    add(f"POKE 53272,2+16*BF:IF LM>0 THEN {cp('CS+P-1', 56136, 'LM')}")
    add(f"{cp(CBUF[11], '56136+LM', 'T')}:P=P+2:IF P>192 THEN P=P-192")
    add("F=1-F:IF T<40 THEN ~OUTRO")
    add("DB=49152+1024*(1-BF):GOSUB ~OROWS")
    add("REM COLOUR WIPE TO WHITE")
    add(f"FOR W=1 TO 22:BF=1-BF:DB=49152+1024*BF:GOSUB ~TEXT:POKE 53272,2+16*BF:{cp(CBUF[1], '55296+40*W', 40)}:NEXT W")
    add("REM SHRINK TO 8X8")
    add(f"FOR W=1 TO {len(rec1)}:GOSUB ~TSTEP:GOSUB ~SHREC:NEXT W:FOR W=1 TO 10:GOSUB ~TSTEP:NEXT W")
    add("REM TWO DANCER BANDS, THE PORTRAIT SHRINKS AWAY, THEN THE DUNGEON")
    add("FOR W=0 TO 7:C=SC(W):S=CB(C):D=55336+40*W:N=40:GOSUB ~CP:D=55896+40*W:GOSUB ~CP:NEXT W")
    add(f"PA=1:PB=121:N2={len(rec2)}:DG=0:B2=1")
    add("BF=1-BF:DB=49152+1024*BF:GOSUB ~TEXT:POKE K2,PA-O:SH=SM(F):D=DB+40:GOSUB ~PTRD", "BANDS")
    add("FOR R=O TO 8:POKE K3,SH:POKE K0,DL:POKE K1,DH:POKE K4,O:POKE K5,Z:SYS Y:SH=SH+O:DL=DL+Z:IF DL>U THEN DL=DL-V:DH=DH+O")
    add("NEXT R:POKE K2,39+PB:SH=SM(F):D=DB+600:GOSUB ~PTRD")
    add("FOR R=O TO 8:POKE K3,SH:POKE K0,DL:POKE K1,DH:POKE K4,O:POKE K5,Z:SYS Y:SH=SH+O:DL=DL+Z:IF DL>U THEN DL=DL-V:DH=DH+O")
    add("NEXT R:POKE 53272,2+16*BF")
    add("PA=PA+2:IF PA>120 THEN PA=PA-80")
    add("PB=PB-2:IF PB<1 THEN PB=PB+80")
    add("F=1-F:IF N2>0 THEN N2=N2-1:GOSUB ~SHREC:IF N2=0 THEN DG=1:L=0:DS=0")
    add("IF DG THEN GOSUB ~DSTEP")
    add("GOTO ~BANDS")
    # ------------------------------------------------ subroutines
    add("REM TOP ROW LEFT TO RIGHT, BOTTOM ROW RIGHT TO LEFT", "TEXT")
    add(f"{cp('TP+TA-1', 'DB', 40)}:TA=TA-1:IF TA<1 THEN TA=56")
    add("S=BA+TB-1:IF TB>160 THEN S=BB+TB-161")
    add("D=DB+960:N=40:GOSUB ~CP:TB=TB+1:IF TB>275 THEN TB=1")
    add("RETURN")
    add("BF=1-BF:DB=49152+1024*BF:GOSUB ~TEXT:POKE 53272,2+16*BF:RETURN", "TSTEP")
    add("DH=INT(D*Q8):DL=D-V*DH:RETURN", "PTRD")
    add("REM DANCERS IN COLUMNS 0 TO LM-1, PORTRAIT FROM LM", "OROWS")
    add("FOR R=0 TO 21:D=DB+40+40*R:IF LM>0 AND R>0 AND R<21 THEN S=(BG(F)+R-1)*V+P-1:N=LM:GOSUB ~CP")
    add(f"S=OA+R*{STRIDE_O}:D=DB+40+40*R+LM:N=T:GOSUB ~CP:NEXT R:RETURN")
    add("REM ONE SHRINK STEP, ON BOTH SCREENS", "SHREC")
    add("READ R0,C0,NR:FOR I=1 TO NR:READ FS$(I):NEXT I:POKE 648,192:GOSUB ~FROWS:POKE 648,196")
    add("FOR I=1 TO NR:POKE 214,R0+I-1:POKE 211,C0:SYS 58732:POKE 646,1:IF B2 AND (R0+I=9 OR R0+I=16) THEN POKE 646,11", "FROWS")
    add("PRINT FS$(I);:NEXT I:RETURN")
    add("REM DUNGEON: CLEAR A ROW A STEP, THEN ONE MOVE A STEP", "DSTEP")
    add("IF DS<6 THEN ~DROW")
    add("IF DS=6 THEN DS=7:MI=1:FR=0:BM=0:PR=ASC(RB$(L))-47:PC=ASC(MID$(RB$(L),2,1))-47:GOSUB ~LOOK:R=PR:C=PC:G=6:GOTO ~DRAW")
    add("IF MI>LEN(MV$(L)) THEN MI=MI+1:IF MI>LEN(MV$(L))+6 THEN L=(L+1) AND 3:DS=0")
    add("IF MI>LEN(MV$(L)) THEN RETURN")
    add("M$=MID$(MV$(L),MI,1):MI=MI+1:FR=1-FR:IF BM THEN BM=0:R=PR:C=PC:G=6:GOSUB ~DRAW")
    add("FOR I=1 TO MN:R=MR%(I):C=MC%(I):IF T%(R,C)>=8 AND V%(R,C) THEN G=T%(R,C)+FR:GOSUB ~DRAW")
    add('NEXT I:IF M$="S" THEN RETURN')
    add("X=ASC(M$):TR=PR+DR%(X):TC=PC+DC%(X):IF MT%(X)=0 THEN ~DMOVE")
    add("R=PR:C=PC:G=7:GOSUB ~DRAW:BM=1:IF MT%(X)=2 THEN T%(TR,TC)=2:R=TR:C=TC:G=2:GOSUB ~DRAW")
    add("RETURN")
    add("IF T%(TR,TC)=4 OR T%(TR,TC)=5 THEN T%(TR,TC)=2", "DMOVE")
    add("R=PR:C=PC:PR=TR:PC=TC:G=T%(R,C):GOSUB ~DRAW:R=PR:C=PC:G=6:GOSUB ~DRAW")
    add("REM REVEAL THE ROOM ON ENTRY AND THE CORRIDOR NEXT TO THE THIEF", "LOOK")
    add('K$=MID$(Z$(L,PR),PC+1,1):IF K$>="0" AND K$<="9" THEN K=VAL(K$):IF RS%(K)=0 THEN GOSUB ~ROOM')
    add("FOR Q=0 TO 4:R=PR+QR%(Q):C=PC+QC%(Q):IF R>=0 AND R<=5 AND C>=0 AND C<=37 THEN IF V%(R,C)=0 THEN GOSUB ~CORR")
    add("NEXT Q:RETURN")
    add('IF MID$(Z$(L,R),C+1,1)="-" THEN V%(R,C)=1:GOTO ~GCELL', "CORR")
    add("RETURN")
    add("RS%(K)=1:R0=ASC(MID$(RB$(L),4*K+1,1))-48:C0=ASC(MID$(RB$(L),4*K+2,1))-48", "ROOM")
    add("R1=ASC(MID$(RB$(L),4*K+3,1))-48:C1=ASC(MID$(RB$(L),4*K+4,1))-48")
    add("FOR R=R0 TO R1:FOR C=C0 TO C1:IF V%(R,C)=0 THEN V%(R,C)=1:GOSUB ~GCELL")
    add("NEXT C,R:RETURN")
    add("G=T%(R,C):IF G>=8 THEN G=G+FR", "GCELL")
    add("IF R=PR AND C=PC THEN G=6")
    add(f"A=49513+R*40+C:GX=G+{DBASE}+{DBASE - 32}*(G=0):POKE A,GX:POKE A+1024,GX:POKE A+6144,CO%(G):RETURN", "DRAW")
    add("REM CLEAR SCREEN ROW 9+DS AND COPY MAP ROW DS", "DROW")
    add("IF DS=0 THEN MN=0:FOR I=0 TO 9:RS%(I)=0:NEXT I")
    add(f"S={SPBUF}:D=49512+40*DS:N=40:GOSUB ~CP:D=D+1024:GOSUB ~CP")
    add("FOR C=0 TO 37:X=TC%(ASC(MID$(M$(L,DS),C+1,1))):T%(DS,C)=X:V%(DS,C)=0:IF X>=8 THEN MN=MN+1:MR%(MN)=DS:MC%(MN)=C")
    add("NEXT C:DS=DS+1:RETURN")
    # ------------------------------------------------ start up
    add("POKE 53280,0:POKE 53281,0:IF PEEK(56)<>147 THEN POKE 55,0:POKE 56,147:CLR", "INIT")
    add("REM BUSIEST VARIABLES FIRST: BASIC FINDS THEM FASTER")
    add(f"R=0:SL=0:SH=0:DL=0:DH=0:K2=90:K3=91:K0=88:K1=89:K4=781:K5=782:O=1:Z=40:Y=41964")
    add(f"E={STRIDE_BIG}:H={STRIDE_SM}:U=255:V=256:Q8=1/256:S=0:D=0:N=0:F=0:P=0:BF=0:DB=0:TA=0:TB=0:CS=0:TP=0:BA=0:BB=0:I=0:J=0:C=0:B=0:X=0:W=0:A=0")
    add("DV=PEEK(186):IF DV<8 THEN DV=8")
    add('IF QM=0 THEN QM=1:F$="MEDLEYPAL":IF PEEK(678)=0 THEN F$="MEDLEYNTSC"')
    add('IF QM=1 THEN QM=2:PRINT CHR$(147);"{WHT}LOADING PETSCII PIT - GRAND MEDLEY ...":LOAD F$,DV,1')
    add('PRINT "{WHT}BUILDING THE FONT ...":POKE 56334,PEEK(56334) AND 254:POKE 1,PEEK(1) AND 251')
    add("REM ROM FONT TO $C800")
    add("POKE 88,0:POKE 89,207:POKE 90,0:POKE 91,215:POKE 781,8:POKE 782,0:SYS 41964")
    add("POKE 1,PEEK(1) OR 4:POKE 56334,PEEK(56334) OR 1")
    add("REM LETTERS ALSO AT 65-90, SO THE REM TEXT CAN BE COPIED STRAIGHT TO THE SCREEN")
    add("S=51208:D=51720:N=208:GOSUB ~CP")
    add("DIM FS$(22),M$(3,5),Z$(3,5),RB$(3),MV$(3),T%(5,37),V%(5,37),RS%(9),MR%(20),MC%(20),CO%(21)")
    add("DIM TC%(90),DR%(90),DC%(90),MT%(90),QR%(4),QC%(4),SC(7),CB(15),BG(1),SM(1)")
    add("READ BG(0),BG(1),SM(0),SM(1),OA,TP,BA,BB:FOR I=0 TO 1:BG(I)=BG(I)/256:SM(I)=SM(I)/256:NEXT I")
    add(f"FOR I=1 TO {len(glyphs)}:READ C:A=51200+8*C:FOR J=A TO A+7:READ B:POKE J,B:NEXT J,I")
    add("FOR I=0 TO 21:READ CO%(I):NEXT I")
    add("FOR I=1 TO 12:READ X,DR%(X),DC%(X),MT%(X):NEXT I:FOR I=0 TO 4:READ QR%(I),QC%(I):NEXT I")
    add("FOR I=1 TO 12:READ X,TC%(X):NEXT I:GOSUB ~LEVELS")
    add("REM COLOUR ROWS, LABEL COLOUR STRIP, SPACES")
    add(f"CB(11)={CBUF[11]}:CB(12)={CBUF[12]}:CB(15)={CBUF[15]}:CB(1)={CBUF[1]}")
    add("FOR C=1 TO 15:IF CB(C) THEN FOR I=CB(C) TO CB(C)+39:POKE I,C:NEXT I")
    add(f"NEXT C:FOR I={SPBUF} TO {SPBUF + 39}:POKE I,32:NEXT I:FOR I={CSTRIP} TO {CSTRIP + 231}:POKE I,11:NEXT I")
    add(f"CS={CSTRIP}:READ NL:FOR J=1 TO NL:READ X,N:FOR I=CS+X TO CS+X+N-1:POKE I,1:NEXT I,J")
    add("FOR I=0 TO 7:READ SC(I):NEXT I")
    add("REM SCREENS $C000/$C400 IN VIC BANK 3, FONT $C800")
    add("POKE 56576,PEEK(56576) AND 252:POKE 648,196:PRINT CHR$(147);:POKE 648,192:PRINT CHR$(147);")
    add(f"FOR W=0 TO 24:READ C:{cp('CB(C)', '55296+40*W', 40)}:NEXT W")
    add(f"POKE 53272,2:BF=0:LM=40:P=1:F=0:TA=56:TB=1:K={kpal}:IF PEEK(678)=0 THEN K={kntsc}")
    add('SYS 38662:TI$="000000":GOTO ~DANCE')
    # ------------------------------------------------ data, in reading order
    def num(v):
        return f"{v:05d}" if addr is None else str(v)

    add("REM WHERE THE REM DATA LINES ARE: BIG DANCERS, SMALL DANCERS, PORTRAIT, TOP TEXT, BOTTOM TEXT")
    add("DATA " + ",".join(f"{a.get(k, 0):05d}" for k in ("big0", "big1", "sm0", "sm1", "outro", "top", "bot1", "bot2")))
    add("REM BLOCK SHAPES (CODES 33-63) AND GAME GLYPHS (CODES 100-120)")
    for g in glyphs:
        add("DATA " + ",".join(map(str, g)))
    add("REM DUNGEON GLYPH COLOURS")
    add("DATA " + ",".join(map(str, D.COLOURS)))
    add("REM MOVES: LETTER, ROW STEP, COLUMN STEP, 0 WALK / 1 BUMP / 2 BUMP AND DROP")
    mv = []
    for typ, table in ((0, {k: k for k in D.DIRS}), (1, D.BUMP), (2, D.KILL)):
        for d, letter in table.items():
            dr, dc = D.DIRS[d]
            mv += [ord(letter), dr, dc, typ]
    add("DATA " + ",".join(map(str, mv)))
    add("DATA 0,0,0,-1,0,1,-1,0,1,0")
    tiles = [("W", 1), (".", 2), (">", 3), ("P", 4), ("T", 5)] + \
        [(m, 8 + 2 * i) for i, m in enumerate(D.MONSTERS)]
    add("DATA " + ",".join(f"{ord(x)},{y}" for x, y in tiles))
    add("REM LABEL COLUMNS AND LENGTHS (BOTH COPIES), SMALL DANCER ROW COLOURS, SCREEN ROW COLOURS")
    lab = []
    for x, n in labels:
        for c in (x - 1, x - 1 + gen.BIG_LINE):
            n2 = min(n, BW - c)
            if n2 >= 1:                  # a FOR loop always runs once
                lab += [c, n2]
    add("DATA " + str(len(lab) // 2) + "," + ",".join(map(str, lab)))
    add("DATA " + ",".join(map(str, gen.SM_COLOURS)))
    add("DATA " + ",".join(map(str, [1] + gen.BIG_COLOURS + [11, 15])))
    add("REM SHRINK STEPS: SCREEN ROW, COLUMN, ROWS, THEN THE ROWS")
    for recs in (rec1, rec2):
        for pt, pl, rows in recs:
            items = [str(pt), str(pl), str(len(rows))] + ['"' + r + '"' for r in rows]
            line = []
            for it in items:
                if sum(len(x) + 1 for x in line) + len(it) > 70:
                    add("DATA " + ",".join(line))
                    line = []
                line.append(it)
            if line:
                add("DATA " + ",".join(line))
    add("REM DUNGEON LEVELS: MAP, ROOM NUMBERS, ROOM BOXES, THE THIEF'S MOVES", "LEVELS")
    for i, lvl in enumerate(lv):
        for r in range(D.H):
            add(f'M$({i},{r})="' + "".join(lvl["grid"][r]) + '"')
        for r in range(D.H):
            z = "".join(str(k) if k >= 0 else ("-" if k == -2 else " ") for k in lvl["room"][r])
            add(f'Z$({i},{r})="' + z + '"')
        rb = "".join(chr(48 + v) for rect in lvl["rects"] for v in rect)
        assert '"' not in rb
        add(f'RB$({i})="' + rb + '"')
        add(f'MV$({i})="' + lvl["moves"] + '"')
    add("RETURN")
    # REM data lines: copied straight to the screen, so nothing else may
    # share their lines; each is the REM token followed by screen codes
    rem_lines = []
    add("REM ---- SCREEN DATA BELOW: BIG DANCERS (2 FRAMES X 20 ROWS)")
    for p in range(PH):
        for r in range(20):
            if r == 0:
                add("REM#PAD#")
            add("REM#PAD#")
            add("REM" + big[(p, r)], ("big%d" % p) if r == 0 else None)
    add("REM ---- SMALL DANCERS (2 FRAMES X 8 ROWS)")
    for p in range(PH):
        for r in range(8):
            if r == 0:
                add("REM#PAD#")
            add("REM#PAD#")
            add("REM" + small[(p, r)], ("sm%d" % p) if r == 0 else None)
    add("REM ---- THE PORTRAIT AS IT COMES IN (22 ROWS)")
    for r in range(22):
        add("REM" + outro[r], "outro" if r == 0 else None)
    add("REM ---- SCROLLER TEXTS")
    add("REM" + top + top[:40], "top")
    add("REM" + bottom[:200], "bot1")
    add("REM" + bottom[160:] + bottom[:40], "bot2")
    # number the lines and resolve labels
    nums, n = {}, 10
    for label, _ in L:
        if label:
            nums[label] = n
        n += 10
    out, n = [], 10
    for label, text in L:
        for name in sorted(nums, key=len, reverse=True):
            text = text.replace("~" + name, str(nums[name]))
        assert "~" not in text, text
        out.append(f"{n} {text}")
        n += 10
    data_lines = {k: nums[k] for k in ("big0", "big1", "sm0", "sm1", "outro", "top", "bot1", "bot2")}
    return out, data_lines


def rem_addresses(lines, data_lines):
    """tokenize and find where each REM data line's first data byte lands"""
    import build_disk
    path = os.path.join(OUT, "tmp.bas")
    open(path, "w").write("\n".join(lines) + "\n")
    prg = build_disk.tokenize(path)
    addr, pos = {}, 0x0801
    want = {v: k for k, v in data_lines.items()}
    i = 2
    while True:
        link = prg[i] | prg[i + 1] << 8
        if link == 0:
            break
        num = prg[i + 2] | prg[i + 3] << 8
        if num in want:
            assert prg[i + 4] == 0x8F            # REM
            addr[want[num]] = pos + 5
        i += link - pos
        pos = link
    return addr


def fix_pads(lines):
    """size the REM#PAD# lines so the following data line starts on a page.
    A run of placeholders shares the padding, so no line gets too long."""
    import build_disk
    out, pos, i = [], 0x0801, 0
    while i < len(lines):
        num, body = lines[i].split(" ", 1)
        if body != "REM#PAD#":
            pos += 4 + len(build_disk.tokenize_line(body)) + 1
            out.append(lines[i])
            i += 1
            continue
        run = []
        while i < len(lines) and lines[i].split(" ", 1)[1] == "REM#PAD#":
            run.append(lines[i].split(" ", 1)[0])
            i += 1
        g = (-(pos + 5)) % 256          # bytes to fill before the data line's header
        while g < 6 * len(run):
            g += 256
        spaces = g - 6 * len(run)
        for k, n in enumerate(run):
            take = spaces // (len(run) - k)
            spaces -= take
            out.append(f"{n} REM" + " " * take)
            pos += 6 + take
    return out


def main():
    lines, data_lines = program()
    lines = fix_pads(lines)
    addr = rem_addresses(lines, data_lines)
    lines2, _ = program(addr)
    lines2 = fix_pads(lines2)
    assert rem_addresses(lines2, data_lines) == addr
    lines = lines2
    path = os.path.join(HERE, "pitmedleybas.bas")
    open(path, "w").write("\n".join(lines) + "\n")
    longest = max(len(l) for l in lines)
    print(f"pitmedleybas.bas: {len(lines)} lines, longest {longest} chars")


if __name__ == "__main__":
    main()
