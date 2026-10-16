"""Experimental truncated-rail and modular-payload predictor for 4b2ec52f.

Not a rejection certificate. The actual circuit also has payload-window value
errors, T0 sign-window shortcuts and rail-source corruption. Only a protected
simulator-confirmed failing batch can be rejected with this predictor.
"""
import csv
import json
from pathlib import Path
import sys
import time
from functools import lru_cache

ROOT=Path(__file__).parent
P=(1<<256)-(1<<32)-977
STEPS=[list(map(int,l.split())) for l in (ROOT/'model-source/steps.txt').read_text().splitlines() if l and not l.startswith('#')]
ANCH=[int(x.strip()) for x in (ROOT/'model-source/anchors.txt').read_text().split(',') if x.strip()]
LATE=[(0,22),(1,13),(6,17),(11,22),(90,19),(100,17),(112,15),(118,13),(124,11)]

def trunc(x,w):
    u=x&((1<<w)-1)
    return u-(1<<w) if u>>(w-1) else u

def half(x):
    return (x+(P if x&1 else 0))>>1

@lru_cache(None)
def inverse_barrel_ops(width,k1,k2):
    reflection=lambda x:[(i,(x-i)%width) for i in range(width) if i<(x-i)%width]
    ops=[('x',k1,0),('x',k2,1),('x',k2,width-1)]
    ops += [('s',i,j) for i,j in reflection(0) if (i,j)!=(1,width-1) and k2]
    ops += [('s',i,j) for i,j in reflection(width-2) if k1^k2]
    ops += [('s',i,j) for i,j in reflection(width-3) if (i,j)!=(width-2,width-1) and k1]
    ops += [('x',k2,width-2),('x',k2,width-1)]
    return tuple(reversed(ops))

def inverse_barrel_literal(value,width,extra):
    word=value&((1<<width)-1);sign=word>>(width-1)
    for kind,a,b in inverse_barrel_ops(width,extra&1,extra>>1):
        if kind=='x':word ^= (sign&a)<<b
        elif ((word>>a)^(word>>b))&1:word ^= (1<<a)|(1<<b)
    return trunc(word,width)

@lru_cache(None)
def compiled_inverse_barrel(width,extra):
    permutation=list(range(width));mask=0
    for kind,a,b in inverse_barrel_ops(width,extra&1,extra>>1):
        if kind=='x':mask^=a<<b
        else:
            permutation[a],permutation[b]=permutation[b],permutation[a]
            if ((mask>>a)^(mask>>b))&1:mask^=(1<<a)|(1<<b)
    exceptions=tuple((i,source,(i-extra)%width) for i,source in enumerate(permutation) if source!=(i-extra)%width)
    return exceptions,mask

def inverse_barrel(value,width,extra):
    word=value&((1<<width)-1)
    result=((word<<extra)|(word>>(width-extra)))&((1<<width)-1)
    exceptions,mask=compiled_inverse_barrel(width,extra)
    for dest,actual,rotated in exceptions:
        result^=(((word>>actual)^(word>>rotated))&1)<<dest
    result^=(word>>(width-1))*mask
    return trunc(result,width)

def reverse_rails(endpoint,tape,leg,trace=None,diagnostics=None):
    # N2 returns its parked sign-copy loan before reverse rail ticks. A bad
    # endpoint's lower held bits are overwritten by fresh copies of its sign.
    r=[-1 if x<0 else 1 for x in endpoint]
    for tick in reversed(range(1,len(STEPS))):
        w,n0,n1,n2,nb=STEPS[tick];wn=STEPS[min(tick+1,len(STEPS)-1)][0]
        target=tick%2;source=1-target
        fused=leg=='multiply' and 76<=tick<131
        bw=lambda n:min(n,w,wn) if fused else n
        if leg=='multiply' and tick==75:
            if diagnostics is not None:diagnostics['FM_loan_clean']=trunc(r[1],STEPS[76][0]-2)==r[1]
            r[1]=trunc(r[1],STEPS[76][0]-2)
        r[target]=trunc(r[target],min(nb,wn) if fused else w)
        r[source]=trunc(r[source],min(w,wn) if fused else w)
        letters,sign,extra=tape[tick]
        r[target]=trunc(r[target],nb);r[source]=trunc(r[source],bw(n2))
        r[target]=inverse_barrel(r[target],nb,extra)
        r[target]=trunc(r[target],n2-1)
        r[target]=trunc(2*r[target]+(r[source] if sign else -r[source]),n2)
        for sign,nk in zip(reversed(letters),[n1,n0][-len(letters):] if letters else []):
            r[target]=trunc(r[target],nk-1);r[source]=trunc(r[source],bw(nk))
            r[target]=trunc(2*r[target]+(r[source] if sign else -r[source]),nk)
        r=[trunc(v,w) for v in r]
        if trace is not None:trace.append(dict(tick=tick,r0=r[0]%P,r1=r[1]%P))
    return r

def window(x,width,tick):
    k=next(l-2 for start,l in reversed(LATE) if tick>=start)
    low=max(ANCH[tick]-k,0)
    # Source w1_window excludes the sign bit and all sign-extension positions.
    mag=(x ^ (-1 if x<0 else 0)) & ((1<<(width-1))-1)
    return (mag>>low)&((1<<(k+2))-1)

def choice(t,b,tw,bw,tick,before_forced=None,forced_sign=0,source_sign_before=None):
    dq=((t^b)>>1)&1
    z=[((t^b)>>i)&1 ^ dq for i in (2,3,4)]
    z2,z3,z4=z
    eq=int((t<0) ^ (b<0) ^ bool(dq))
    a1=(1-z2)&(1-z3)
    a2=a1&(1-z4)
    out=dq^1^a2
    v3=0
    if tick==0:
        out ^= eq & z2
    elif before_forced is not None:
        y=int(window(t,tw,tick)>2*window(b,bw,tick))
        old_source_sign=(b<0) if source_sign_before is None else source_sign_before
        not_flipped=int(not ((before_forced<0)^(t<0)^old_source_sign^(b<0)))
        added=int(not ((before_forced<0) ^ old_source_sign ^ bool(forced_sign)))
        # Source YP8_VETO=1 computes E & (Y ^ S), including overflow cases.
        veto=eq & (y ^ not_flipped)
        out ^= veto & z2
        v3=veto & (1-z2) & z3 & added
        out ^=v3
    else:
        y=int(window(t,tw,tick)>4*window(b,bw,tick))
        out ^= eq & (1-y) & z2
    k2=(1-z2)^a2^v3
    dsel=out^dq
    k1=dsel^(1-z2)^a1^v3
    return out,k1+2*k2

def onefold(a,b,signs,extra,tick,reverse=False):
    mask=(1<<256)-1;f=(1<<32)+977;s=3+extra
    if reverse:
        W=((a<<s)&mask)|(a>>(256-s))
        signs=[1-si for si in signs]
        X=W+sum((b if not si else mask-b)<<i for i,si in enumerate(signs))
        E=X>>256;L=X&mask;Nm=sum(si<<i for i,si in enumerate(signs));m=W&((1<<s)-1)
        C=E+(E-Nm+m)*(f-1);w=56
        return ((L-(L&((1<<w)-1)))+(((L&((1<<w)-1))+C)&((1<<w)-1)))%P
    X=a+sum((b if not si else mask-b)<<i for i,si in enumerate(signs))
    E=X>>256;L=X&mask;Nm=sum(si<<i for i,si in enumerate(signs))
    A=L+E+(E-Nm)*(f-1);m=(A*pow(f,-1,1<<s))&((1<<s)-1)
    C=E+(E-Nm-m)*(f-1);w=57 if tick<=99 else 56
    window=(L-(L&((1<<w)-1)))+(((L&((1<<w)-1))+C)&((1<<w)-1))
    return ((window>>s)+m*(1<<(256-s)))%P

def walk(d,forward_payload=True,leg='divide',trace=None,payload=None,reverse_trace=None,diagnostics=None):
    r0=d if d&1 else d-P
    r=[r0,(r0+(P if r0%4==3 else -P))//2]
    c=[1,half(1)] if payload is None else [payload,half(payload)]
    tape=[]
    first_overflow=None
    for tick,(w,n0,n1,n2,nb) in enumerate(STEPS):
        target=tick%2;source=1-target
        wn=STEPS[min(tick+1,len(STEPS)-1)][0]
        # Divide fuses payload only after42; multiply forward walk is rails-only.
        fused=leg=='divide' and 42<=tick<131
        payload_before=c[:]
        bw=lambda n:min(n,w,wn) if fused else n
        letters=[]
        before=None;lastsign=0;captured_choice=None
        for j,(nk,nnext) in enumerate(((n0,n1),(n1,n2)) if tick+1<len(STEPS) else ()):
            for side,width in ((target,nk),(source,bw(nk))):
                if trunc(r[side],width)!=r[side] and first_overflow is None:first_overflow=tick
                r[side]=trunc(r[side],width)
            old=r[target]
            sign=((r[target]^r[source])>>1)&1
            v=(r[target]+(-r[source] if sign else r[source]))//2
            r[target]=trunc(v,nk-1)
            if r[target]!=v and first_overflow is None:first_overflow=tick
            if forward_payload:c[target]=half((c[target]+(-c[source] if sign else c[source]))%P)
            letters.append(sign)
            if j==1:
                before=old;lastsign=sign
                if tick!=0:
                    tw=nk-1;source_width=min(bw(nk),tw)
                    captured_choice=choice(r[target],trunc(r[source],source_width),max(tw,6),max(source_width,6),tick,old,sign,r[source]<0)
            # Source code defers the second forced step's trim until choice.
            if fused and j==0:
                r[target]=trunc(r[target],min(nk-1,nnext))
                r[source]=trunc(r[source],min(bw(nk),w,wn))
        r[target]=trunc(r[target],n2);r[source]=trunc(r[source],bw(n2))
        sign,extra=captured_choice if captured_choice is not None else choice(r[target],r[source],max(n2,6),max(bw(n2),6),tick,before,lastsign)
        v=(r[target]+(-r[source] if sign else r[source]))//2
        r[target]=trunc(v,n2-1)
        if r[target]!=v and first_overflow is None:first_overflow=tick
        if forward_payload:
            c[target]=half((c[target]+(-c[source] if sign else c[source]))%P)
            for _ in range(extra):c[target]=half(c[target])
            if payload is not None and tick+1<len(STEPS):
                c[target]=onefold(payload_before[target],payload_before[source],letters+[sign],extra,tick)
        # Barrel receives nb physically stored bits before stripping extra zeros.
        v=trunc(r[target],nb)>>extra
        r[target]=trunc(v,nb-extra)
        for side in range(2):
            if trunc(r[side],wn)!=r[side] and first_overflow is None:first_overflow=tick
            r[side]=trunc(r[side],wn)
        if fused and tick<130:
            nextrow=STEPS[tick+1];nextnext=STEPS[min(tick+2,len(STEPS)-1)][0]
            width=min(nextrow[1],nextrow[0],nextnext)
            r[target]=trunc(r[target],width)
        if trace is not None:trace.append(dict(tick=tick,r0=r[0]%P,r1=r[1]%P,tape=letters+[sign,extra&1,extra>>1]))
        tape.append((letters,sign,extra))
    if diagnostics is not None or reverse_trace is not None:
        recovered=reverse_rails(r,tape,leg,reverse_trace,diagnostics)
        if diagnostics is not None:
            diagnostics.update(endpoint_unit=all(abs(v)==1 for v in r),recovered_denominator=2*recovered[1]%P)
    if forward_payload:
        return ((-c[0])%P if r[0]<0 else c[0]),r,first_overflow
    value=1 if payload is None else payload
    c=[(-value)%P if r[0]<0 else value,(-value)%P if r[1]<0 else value]
    for tick in reversed(range(len(STEPS))):
        target=tick%2;source=1-target
        letters,sign,extra=tape[tick]
        payload_before=c[:]
        c[target]=(c[target]*(1<<extra))%P
        for sign in [sign]+list(reversed(letters)):
            c[target]=(2*c[target]+(c[source] if sign else -c[source]))%P
        if payload is not None and 1<=tick<127:
            c[target]=onefold(payload_before[target],payload_before[source],letters+[tape[tick][1]],extra,tick,True)
    return 2*c[1]%P,r,first_overflow

def predict(row,folds=False):
    tx,ty,ox,oy,ex,ey=[int(row[k],16) for k in ('tx','ty','ox','oy','ex','ey')]
    d=(tx-ox)%P;y=(ty-oy)%P
    coefficient,rails1,overflow1=walk(d,leg='divide',payload=y if folds else None)
    slope=coefficient if folds else coefficient*y%P
    after_square=(tx+2*ox-slope*slope)%P
    mul_coefficient,rails2,overflow2=walk(after_square,False,'multiply',payload=slope if folds else None)
    actualx=(ox-after_square)%P
    actualy=(mul_coefficient-oy)%P if folds else (mul_coefficient*slope-oy)%P
    return dict(predicted_wrong_value=(actualx,actualy)!=(ex,ey),
                division_x_wrong=actualx!=ex,divide_rails=rails1,multiply_rails=rails2,
                divide_first_overflow=overflow1,multiply_first_overflow=overflow2,
                coefficient_invariant=coefficient*d%P==1)

def main():
    source,out=sys.argv[1:3]
    limit=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
    folds='--folds' in sys.argv
    counts=dict(shots=0,tp=0,fp=0,tn=0,fn=0,rail_warnings=0,warnings_on_passing_shots=0)
    start=time.perf_counter()
    with open(source) as inp,open(out,'w') as sink:
        for row in csv.DictReader(inp,delimiter='\t'):
            if counts['shots']>=limit:break
            p=predict(row,folds=folds);truth=int(row['value']);prediction=p['predicted_wrong_value']
            counts['shots']+=1
            counts['tp' if truth and prediction else 'fn' if truth else 'fp' if prediction else 'tn']+=1
            warning=p['divide_first_overflow'] is not None or p['multiply_first_overflow'] is not None
            counts['rail_warnings']+=warning;counts['warnings_on_passing_shots']+=warning and not truth
            if truth or prediction or warning:
                sink.write(json.dumps(dict(batch=int(row['batch']),lane=int(row['lane']),value=truth,**p))+'\n')
            if counts['shots']%4096==0:print(json.dumps(dict(counts,seconds=time.perf_counter()-start)),flush=True)
    counts.update(seconds=time.perf_counter()-start,status='DIAGNOSTIC_ONLY_NOT_SAFE_FOR_REJECTION',source='4b2ec52f')
    Path(out+'.summary.json').write_text(json.dumps(counts,indent=2)+'\n');print(json.dumps(counts),flush=True)

if __name__=='__main__':main()
