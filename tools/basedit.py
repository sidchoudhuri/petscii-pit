# tiny line-number editor for .bas listings
import re,sys
def load(p):
    d={}
    for l in open(p).read().splitlines():
        if l.strip()=="" : continue
        n=int(l.split(' ',1)[0]); d[n]=l
    return d
def save(p,d):
    open(p,'w').write("\n".join(d[k] for k in sorted(d))+"\n")
def sub(d,n,old,new):
    assert old in d[n], (n,old)
    d[n]=d[n].replace(old,new,1)
