# PETSCII Pit: apply the standard directory layout to a freshly built d64.
# usage: python3 dirlayout.py petsciipit.d64
# dirlayout.bin holds the 30-byte entries of the layout in order. Entries whose
# type is PRG with a real name are replaced by the matching file from the new
# disk (block count, track/sector); everything else (DEL art, blank lines) is copied as-is.
import sys,os
img=sys.argv[1]; d=bytearray(open(img,'rb').read())
lay=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),sys.argv[2] if len(sys.argv)>2 else 'dirlayout.bin'),'rb').read()
lay=[lay[i:i+30] for i in range(0,len(lay),30)]
def off(t,s):
    spt=[21]*17+[19]*7+[18]*6+[17]*5
    return (sum(spt[:t-1])+s)*256
cur={};t,s=18,1
while t==18:
    p=off(t,s)
    for i in range(8):
        e=bytes(d[p+i*32+2:p+i*32+32])
        if e[0]: cur[e[3:19]]=e
    t,s=d[p],d[p+1]
new=[]
for e in lay:
    if e[0]==0x82 and e[3]!=0xA0:
        assert e[3:19] in cur, 'missing file '+e[3:19].rstrip(b'\xa0').decode()
        new.append(cur.pop(e[3:19]))
    else: new.append(e)
assert not cur, 'files not in layout: '+str([k.rstrip(b'\xa0') for k in cur])
order=[1,4,7,10,13,16,2,5,8,11,14,17,3,6,9,12,15,18]
need=(len(new)+7)//8; secs=order[:need]
b=off(18,0)+4+17*4
for s in order:            # free all dir sectors, then claim the ones used
    if not d[b+1+s//8]&(1<<(s%8)): d[b+1+s//8]|=1<<(s%8); d[b]+=1
for k,s in enumerate(secs):
    p=off(18,s); d[p:p+256]=bytes(256)
    for i,e in enumerate(new[k*8:k*8+8]): d[p+i*32+2:p+i*32+32]=e
    d[p],d[p+1]=(18,secs[k+1]) if k+1<need else (0,255)
    d[b+1+s//8]&=~(1<<(s%8))&255; d[b]-=1
open(img,'wb').write(d)
