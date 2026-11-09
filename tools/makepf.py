# PETSCII Pit: build petscii-pit.pf (raw 2048-byte charset, screen-code order, no header)
# exactly as the loader builds it: ROM uppercase/graphics set + glyph DATA (lines 120-230) + solid pi (94).
# usage: makepf.py src/petsciipitloader.bas src/petscii-pit.pf <chargen ROM file>
# (the C64 character ROM is not in the repo; VICE ships it as chargen-901225-01.bin)
import sys
bas=sys.argv[1]; out=sys.argv[2]
rom=bytearray(open(sys.argv[3],'rb').read()[:2048])
L={}
for line in open(bas).read().split('\n'):
    if line.strip(): n,t=line.split(' ',1); L[int(n)]=t
for k in sorted(L):
    if 120<=k<=230 and L[k].startswith('DATA'):
        v=[int(x) for x in L[k][5:].split(':REM')[0].split(',')]
        for i in range(0,len(v),9): rom[v[i]*8:v[i]*8+8]=bytes(v[i+1:i+9])
rom[94*8:94*8+8]=b'\xff'*8
open(out,'wb').write(rom)
