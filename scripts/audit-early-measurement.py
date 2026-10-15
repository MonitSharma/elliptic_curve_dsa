"""Bound an exact scheduling route: retire unused quantum wires earlier.

Only unconditional HMR/R is moved, to a condition-depth-zero boundary after
the wire's last previous touch. HMR must use a fresh bit, copied to its original
slot at the original position. This report proposes no score or transformation.
"""
import argparse
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path
import time

spec=importlib.util.spec_from_file_location('wire',Path(__file__).with_name('analyze-wire-lifetimes.py'))
wire=importlib.util.module_from_spec(spec);spec.loader.exec_module(wire)
NO=wire.NO


def peak(intervals):
    live=[]; best=0; first=None
    for start,end,q in sorted(intervals):
        while live and live[0] < start: heapq.heappop(live)
        heapq.heappush(live,end)
        if len(live)>best: best=len(live);first=start
    return best,first


def analyze(path):
    began=time.monotonic()
    abi=set(); width=0
    for _,row in wire.records(path):
        if row[0]==2 and row[4]!=NO: abi.add(row[4])
        width=max([width]+[q+1 for q in row[2:5] if q!=NO])
    depth=0; pending=set(); starts={}; available={}; original=[]; early=[]; moves=[]
    for at,row in wire.records(path):
        k,_,b,a,t,bt,c,_=row
        touches=[q for q in (a,b,t) if q!=NO]
        if k in (11,12) and depth==0 and c==NO and t not in abi:
            start=starts.pop(t,at)
            before=available.get(t,at)
            original.append((2*start,2*at,t))
            early.append((2*start,min(2*at,2*before-1) if start<before else 2*at,t))
            if start<before<at:
                moves.append(dict(operation=at,insert_before=before,target=t,kind=k,bit=bt))
            available.pop(t,None)
            continue
        for q in touches: starts.setdefault(q,at)
        if k==15: depth+=1
        elif k==16:
            depth-=1;assert depth>=0
            if depth==0:
                for q in pending: available[q]=at+1
                pending.clear()
        if depth:
            pending.update(touches)
        else:
            for q in touches: available[q]=at+1
    assert depth==0
    remaining=[(0 if q in abi else 2*s,2*at+2,q) for q,s in starts.items()]
    remaining += [(0,2*at+2,q) for q in abi if q not in starts]
    original.extend(remaining);early.extend(remaining)
    return dict(status='scheduling diagnostic only; not a generated circuit or score',
                stream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),physical_width=width,
                original_peak=peak(original),early_retirement_peak=peak(early),
                moves=moves,operations=at+1,elapsed_seconds=time.monotonic()-began)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stream',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=analyze(a.stream);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:len(v) if k=='moves' else v for k,v in r.items()},indent=2))
