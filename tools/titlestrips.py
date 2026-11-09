# PETSCII Pit loader: regenerate the title-screen strips (lines 1400-1710)
# from the glyph DATA (lines 120-230) of petsciipitloader.bas.
# "~" in a string is PETSCII 255 = pi, which the loader redefines as a solid block.
import sys,re
f=sys.argv[1]
L={}
for line in open(f).read().split('\n'):
    if line.strip(): n,t=line.split(' ',1); L[int(n)]=t
glyph={}
for n in sorted(L):
    if 120<=n<=230 and L[n].startswith('DATA'):
        v=[int(x) for x in L[n][5:].split(':REM')[0].split(',')]
        for i in range(0,len(v),9): glyph[v[i]]=v[i+1:i+9]
MON=[0,83,88,90,84,86,91,65]; PLAY=[128,129,130,144]
for n in list(L):
    if 1400<=n<=1710: del L[n]
k=1400
for s in range(4):
    for r in range(8):
        row=''
        for gi,g in enumerate(MON):
            code=PLAY[s] if gi==0 else g+128*(s&1)
            b=glyph[code][r]
            row+=''.join('~' if b&(128>>i) else ' ' for i in range(8))+'  '
        row+=row[:40]
        L[k]='T$(%d,%d)="%s"'%(s,r,row)+(':RETURN' if (s,r)==(3,7) else '')
        k+=10
open(f,'w').write('\n'.join('%d %s'%(n,L[n]) for n in sorted(L))+'\n')
