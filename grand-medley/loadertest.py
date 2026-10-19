"""run the machine code loader on the real KERNAL in py65: boots, RUNs
PITMEDLEY, answers the LOADs from build/, checks it jumps to the demo"""
import sys
sys.argv = ["x", sys.argv[1] if len(sys.argv) > 1 else "PAL", "1"]
src = open("basictest.py").read().split("m = MPU()")[0]
exec(src)
m = MPU(); mem = Mem(m); m.memory = mem
mem.ram[0], mem.ram[1] = 0x2F, 0x37
m.pc = KERNAL[0x1FFC] | KERNAL[0x1FFD] << 8
files = {n: open("build/%s.prg" % n.lower(), "rb").read() for n in
         ("MEDLEYPAL", "MEDLEYNTSC", "DEMOCODE", "DEMOHI", "DEMODNG")}
prg = open("build/pitmedley.prg", "rb").read()
loads, started = [], False
for _ in range(20_000_000):
    pc = m.pc
    if pc == 0xFFD5:
        n = mem.ram[0xB7]; a = mem.ram[0xBB] | mem.ram[0xBC] << 8
        name = bytes(mem[a + i] for i in range(n)).decode()
        d = files[name]; la = d[0] | d[1] << 8
        for i, b in enumerate(d[2:]):
            mem[la + i] = b
        m.p &= ~m.CARRY
        lo = m.stPop(); hi = m.stPop(); m.pc = (hi << 8 | lo) + 1
        loads.append((name, hex(la), mem.ram[0xBA], mem.ram[0xB9]))
        continue
    if pc == 0x0900:
        print("reached the demo at $0900 after loading", loads)
        ok = all(mem.ram[0x0900 + i] == files["DEMOCODE"][2 + i] for i in range(100))
        ok &= all(mem.ram[0xE000 + i] == files["DEMODNG"][2 + i] for i in range(100))
        print("memory matches the files:", ok)
        break
    if not started and pc == 0xE5CD:
        mem.ram[0x0801:0x0801 + len(prg) - 2] = prg[2:]
        end = 0x0801 + len(prg) - 2
        for z in (0x2D, 0x2F, 0x31):
            mem.ram[z], mem.ram[z + 1] = end & 255, end >> 8
        mem.ram[0x02A6] = 0 if NTSC else 1
        mem.ram[0xBA] = 9                   # pretend it was loaded from drive 9
        for i, ch in enumerate(b"RUN\r"):
            mem.ram[0x0277 + i] = ch
        mem.ram[0xC6] = 4
        started = True
    m.step()
else:
    print("never reached $0900", loads)
