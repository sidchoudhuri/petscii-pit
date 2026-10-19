import sys
d=open(sys.argv[1],'rb').read()
def off(t,s):
    spt=[21]*17+[19]*7+[18]*6+[17]*5
    return (sum(spt[:t-1])+s)*256
b=off(18,0); print('name',d[b+0x90:b+0xa0], 'id', d[b+0xa2:b+0xa4])
t,s=18,1
while t==18:
    p=off(t,s)
    for i in range(8):
        e=d[p+i*32+2:p+i*32+32]
        if e[0] or any(e): print('%02x'%e[0], e[3:19].hex(), repr(bytes(c if 32<=c<127 else 46 for c in e[3:19]).decode()), e[28]|e[29]<<8)
    t,s=d[p],d[p+1]
