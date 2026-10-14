"""Ideal-integer N275 capacity/reciprocal screening, never circuit qualification.

The proposed guard and precision are fixed before the experiment. Inputs are
the preserved ORIGINAL failed packet plus independently seeded field operands.
No nonce, official packet, schedule or candidate source is changed.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import time

P=2**256-2**32-977


def over(w,z,k):
    size=z.bit_length();shift=size-k
    assert shift>=0
    head=(z>>shift)|1
    reciprocal=((1<<(256-shift))-1)//head
    cut=max(0,257-size-26)
    return (w>>cut)>(reciprocal>>cut)


def screen(dx,rows,stats):
    r,t=[P,dx],[0,1]
    while r[-1]:
        q=r[-2]//r[-1];r.append(r[-2]-q*r[-1]);t.append(t[-2]+q*t[-1])
    j,c,ph,dq=1,0,False,False
    events=[]
    def fits(z,x,y,zn):
        v=lambda x:(x&-x).bit_length()-1 if x else 999
        ring=277 if c<len(rows) and rows[c][2] else 278
        need=max(z.bit_length()+v(x),zn.bit_length()+v(y))
        cut=ring-max(x.bit_length(),y.bit_length())
        if v(x)>21 or v(y)>21 or need>cut:
            events.append({'kind':'map_domain','column':c,'need':need,'cut':cut})
    while not(ph and j==len(r)-2):
        if dq:
            fits(t[j],r[j+1],r[j],t[j+1]);j+=1;dq=False;c+=1;continue
        if not ph and r[j].bit_length()<=128 and r[j].bit_length()<=t[j].bit_length():
            fits(t[j-1],r[j],t[j],r[j-1]);ph=True;c+=1;continue
        delayed=not ph and r[j].bit_length()<=128
        mode='HT' if ph else 'delayed_HR' if delayed else 'HR'
        z,y=(t[j],r[j]) if ph else(r[j],t[j]);q=r[j-1]//r[j]
        row=rows[c] if c<len(rows) else None
        pure=(row is not None and c>=2 and row[6]<=255 and row[0] and not any(row[i] for i in [1,2,3])
              and not(len(row)>16 and (row[14] or row[15])) and not rows[c-1][2]
              and row[8]+23<128)
        qb=24 if pure else 22;k=32 if y.bit_length()<=96 else 24
        stats['active_steps']+=1;stats['pure_HR_steps' if pure else 'mixed_steps']+=1
        stats['head32_steps' if k==32 else 'head24_steps']+=1
        if q>=1<<22:
            stats['q22_pure' if pure else 'q22_outside_guard']+=1
            stats['maximum_q22_outside_guard']=max(stats['maximum_q22_outside_guard'],q if not pure else 0)
        if q>=1<<qb:events.append({'kind':'quotient_cap','column':c,'step':j,'q':q,'cap':qb,'pure':bool(pure)})
        if r[j].bit_length()<=128<r[j-1].bit_length():
            yy=t[j] if r[j].bit_length()>t[j].bit_length() else r[j]
            need=max(0,yy.bit_length()+q.bit_length()-129)
            stats['maximum_required_crossing_reserve']=max(stats['maximum_required_crossing_reserve'],need)
            if need>9:events.append({'kind':'parking','column':c,'step':j,'required':need})
        bb=258-z.bit_length()-y.bit_length()
        if not ph:
            w=t[j-1]
            for bit in range(qb-1,-1,-1):
                if bit<bb:
                    trial=w+(y<<bit)
                    if not over(trial,z,k):w=trial
            if w!=t[j+1]:events.append({'kind':'reciprocal_HR','column':c,'step':j,'head':k,'got':hex(w),'expected':hex(t[j+1])})
        else:
            remaining,x=q,r[j-1]
            for bit in range(qb):
                if bit>=bb:continue
                if remaining>>bit&1:x-=y<<bit
                if not over(x+(y<<bit),z,k):remaining^=1<<bit
            if remaining or x!=r[j+1]:events.append({'kind':'reciprocal_HT','column':c,'step':j,'head':k,'remaining':remaining})
        if delayed:
            fits(t[j+1],r[j],t[j],r[j+1]);ph=True;dq=True
        else:
            fits(z,t[j+1] if not ph else r[j+1],y,r[j+1] if not ph else t[j+1]);j+=1
        c+=1
    return events


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('packet',type=Path);a.add_argument('schedule',type=Path);a.add_argument('output',type=Path)
    a.add_argument('--samples',type=int,default=512);a.add_argument('--seed',type=lambda x:int(x,0),default=0xecd5a69220261014)
    args=a.parse_args();began=time.monotonic()
    rows=[list(map(int,l.split()[1:])) for l in args.schedule.read_text().splitlines() if l.startswith('C ')]
    groups={'original_packet':[],'independent_denominators':[]}
    stats={name:collections.Counter() for name in groups}
    counts=collections.Counter()
    for line in args.packet.read_text().splitlines():
        if line.startswith('#') or not line.strip():continue
        w=line.split();shot=int(w[0]);tx,ty,ox,oy,ex,ey=[int(s,16) for s in w[1:7]]
        for division,dx in [(1,(tx-ox)%P),(2,(ex-ox)%P)]:
            events=screen(dx,rows,stats['original_packet']);counts['original_packet']+=1
            if events:groups['original_packet'].append({'shot':shot,'division':division,'input':hex(dx),'events':events})
    rng=random.Random(args.seed)
    for i in range(args.samples):
        dx=rng.randrange(1,P);events=screen(dx,rows,stats['independent_denominators']);counts['independent_denominators']+=1
        if events:groups['independent_denominators'].append({'index':i,'input':hex(dx),'events':events})
    result={'scope':'Ideal recurrence/predicted quotient, parking, reciprocal and map domains only; no emitted gates, phase, allocation proof, source-width or score',
            'proposal':{'N':275,'K_physical':16,'small_SY_max':96,'small_head':32,'large_head':24,'mixed_cap':22,'pure_HR_cap':24,'crossing_reserve':9,'ordinary_map_extra':3},
            'guard':'Pure HR, not mixed/switch/done/delayed, col>=2 excludes wideSZ/tt, previoussw false, envelopeSYupper+23<128',
            'original_packet_sha256':hashlib.sha256(args.packet.read_bytes()).hexdigest(),'schedule_sha256':hashlib.sha256(args.schedule.read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'independent_seed':args.seed,'input_counts':dict(counts),
            'stats':{g:dict(s) for g,s in stats.items()},'flagged':groups,'elapsed_seconds':time.monotonic()-began,
            'limitations':'No check of fresh-input schedule envelopes, carry-tail errors, quantum/measurement phase, physical donor ownership or actual N275 emitted arithmetic. Unchanged full benchmark still required.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['input_counts','stats','elapsed_seconds']},indent=2),flush=True)
    print('FLAGGED_INPUTS',json.dumps({g:len(v) for g,v in groups.items()}),flush=True)


if __name__=='__main__':main()
