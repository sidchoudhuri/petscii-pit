import sys, hashlib
from py65.devices.mpu6502 import MPU
def run(path):
    d=open(path,'rb').read(); off=d[7]; la=d[8]<<8|d[9]; ia=d[10]<<8|d[11]; pa=d[12]<<8|d[13]
    data=d[off+2:] if la==0 else d[off:]
    if la==0: la=d[off]|d[off+1]<<8
    m=MPU(); mem=m.memory
    for i,b in enumerate(data): mem[la+i]=b
    def call(addr,a=0):
        mem[0xff00]=0x20; mem[0xff01]=addr&255; mem[0xff02]=addr>>8; mem[0xff03]=0x00
        m.pc=0xff00; m.a=a; m.sp=0xfd; n=0
        while m.pc!=0xff03:
            m.step(); n+=1
            assert n<200000
        return m.processorCycles
    call(ia,0)
    seen={}; frames=0; maxcyc=0
    while frames<200000:
        c0=m.processorCycles; call(pa); maxcyc=max(maxcyc,m.processorCycles-c0)
        frames+=1
        h=hashlib.md5(bytes(mem[0:0xd000])+bytes(mem[0xe000:0xff00])).digest()
        if h in seen:
            return seen[h],frames,maxcyc
        seen[h]=frames
for p in sys.argv[1:]:
    j,k,mc=run(p); print(p,'state after frame',k,'= state after frame',j,'-> song length',k-j,'frames; max play cycles',mc)
