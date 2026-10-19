"""render the harness snapshots (build/snaps-*.pkl) to a contact sheet"""
import pickle, sys
from PIL import Image
import gen
which = sys.argv[1] if len(sys.argv) > 1 else "pal"
out = sys.argv[2] if len(sys.argv) > 2 else "build/sim-%s.png" % which
snap = pickle.load(open("build/snaps-%s.pkl" % which, "rb"))
hi = open("build/hi.bin", "rb").read()
cons = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in open("build/consts.asm") if "=" in l}
dfont = int(cons["ADDR_DFONT"][1:], 16) - 0xA000
PAL = dict(gen.PAL)
PAL.update({2: (136, 57, 50), 3: (112, 164, 178), 4: (111, 61, 134), 5: (88, 141, 67),
            7: (184, 199, 111), 8: (111, 79, 37), 10: (184, 105, 98)})


def render(s, c, dd):
    img = Image.new("RGB", (320, 200))
    px = img.load()
    split = any(v == 0x12 for _, v in dd)
    for r in range(25):
        for col in range(40):
            code = s[r * 40 + col]
            if split and 9 <= r <= 14:
                bits = hi[dfont + code * 8:dfont + code * 8 + 8] if code < 22 else bytes([0x55] * 8)
            else:
                bits = gen.ROM[code * 8:code * 8 + 8]
            fg = PAL.get(c[r * 40 + col] & 15, (255, 0, 255))
            for y in range(8):
                for x in range(8):
                    if bits[y] >> (7 - x) & 1:
                        px[col * 8 + x, r * 8 + y] = fg
    return img.resize((640, 400), Image.NEAREST)


fs = sorted(snap)
W, H = 640, 400
sheet = Image.new("RGB", (2 * W + 30, ((len(fs) + 1) // 2) * (H + 10) + 10), (40, 40, 40))
for i, f in enumerate(fs):
    s, c, dd = snap[f]
    sheet.paste(render(s, c, dd), (10 + (i % 2) * (W + 10), 10 + (i // 2) * (H + 10)))
sheet.resize((sheet.width // 2, sheet.height // 2)).save(out)
print(out, fs)
