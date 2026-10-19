"""contact sheet of basictest.py snapshots"""
import pickle, sys
from PIL import Image
import gen
snaps = pickle.load(open(sys.argv[1], "rb"))
pick = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
PAL = dict(gen.PAL)
PAL.update({2: (136, 57, 50), 3: (112, 164, 178), 4: (111, 61, 134), 5: (88, 141, 67),
            6: (53, 40, 121), 7: (184, 199, 111), 8: (111, 79, 37), 9: (67, 57, 0), 10: (184, 105, 98),
            13: (154, 210, 132), 14: (108, 94, 181)})
chosen = [s for s in snaps if pick is None or s[0] in pick]
print([(s[0], s[1]) for s in snaps])
W, H = 640, 400
sheet = Image.new("RGB", (2 * W + 30, ((len(chosen) + 1) // 2) * (H + 10) + 10), (40, 40, 40))
for i, (t, line, scr, col, font) in enumerate(chosen):
    img = Image.new("RGB", (320, 200))
    px = img.load()
    for r in range(25):
        for c in range(40):
            code = scr[r * 40 + c]
            bits = font[(code & 127) * 8:(code & 127) * 8 + 8]
            inv = code >= 128
            fg = PAL[col[r * 40 + c] & 15]
            for y in range(8):
                for x in range(8):
                    if ((bits[y] >> (7 - x)) & 1) ^ inv:
                        px[c * 8 + x, r * 8 + y] = fg
    sheet.paste(img.resize((W, H), Image.NEAREST), (10 + (i % 2) * (W + 10), 10 + (i // 2) * (H + 10)))
sheet.resize((sheet.width // 2, sheet.height // 2)).save(sys.argv[2])
