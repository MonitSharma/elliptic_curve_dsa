"""Search source-guided 30-AND constructor programs on all 16,384 inputs.

The original internal span contains six directions outside the final value
interface. Search the 63 codimension-one subspaces of those six directions.
Every admitted gate stays in the selected subspace; sparse affine products and
original source operands provide new products. Failure is incomplete search,
never an optimality proof. This is value synthesis, not a full-circuit score.
"""
import argparse
import hashlib
import json
import itertools
from pathlib import Path
import random
import time


class Space:
    def __init__(self, values=()):
        self.rows={}
        self.values=[]
        for v in values:
            self.add(v)
    def express(self,v):
        m=0
        while v:
            b=v.bit_length()-1
            if b not in self.rows:
                return None
            x,s=self.rows[b]
            v ^= x; m ^= s
        return m
    def add(self,v):
        m=1<<len(self.values)
        original=v
        while v:
            b=v.bit_length()-1
            if b not in self.rows:
                self.rows[b]=v,m
                self.values.append(original)
                return True
            x,s=self.rows[b]
            v ^= x;m ^= s
        return False


def combination(mask,vals):
    v=0
    while mask:
        low=mask&-mask
        v ^= vals[low.bit_length()-1]
        mask ^= low
    return v


def run(net,seconds,pairs,output,weight):
    n=1<<net["input_count"]
    raw=[(1<<n)-1]+[sum((r>>i&1)<<r for r in range(n)) for i in range(net["input_count"])]
    original=list(raw)
    gate_data=[]
    for g in net["gates"]:
        a,b=combination(g["a"],original),combination(g["b"],original)
        v=a&b
        gate_data.append((g["name"],a,b,v))
        original.append(v)
    targets=[combination(m,original) for m in net["outputs"]]
    w=Space(raw+targets)
    outside=[]
    full=Space(w.values)
    for name,a,b,v in gate_data:
        if full.add(v):
            outside.append(v)
    assert len(outside)==6 and len(full.values)==46 and len(w.values)==40
    started=time.monotonic()
    planes=list(range(1,64))
    # Simple basis-direction removal first, then mixed hyperplanes.
    planes.sort(key=lambda x:(x.bit_count(),x))
    reports=[]
    result={"baseline_revision":net["baseline_revision"],"source_lf_sha256":net["source_lf_sha256"],
            "exact_domain_size":n,"old_AND_count":31,"status":"running", "planes":reports}
    def save():
        output.write_text(json.dumps(result,indent=2)+"\n")
    for plane in planes:
        if time.monotonic()-started >= seconds:
            break
        pivot=(plane&-plane).bit_length()-1
        extras=[v ^ (outside[pivot] if plane>>j&1 else 0) for j,v in enumerate(outside) if j!=pivot]
        admitted=Space(w.values+extras)
        assert len(admitted.values)==45
        current=Space(raw)
        gates=[]
        attempts=0
        stages=[]
        rng=random.Random(0xECD5A00+plane)
        plane_start=time.monotonic()
        while time.monotonic()-started < seconds:
            if all(current.express(v) is not None for v in targets):
                outputs=[current.express(v) for v in targets]
                check=list(raw)
                for a,b in gates:
                    check.append(combination(a,check)&combination(b,check))
                assert [combination(m,check) for m in outputs]==targets
                result.update(status="value_witness_found",AND_count=len(gates),gates=gates,outputs=outputs,
                              hyperplane=plane,seconds=time.monotonic()-started,
                              complete_native_cleanup_verified=False,submission_ready=False)
                save();print(json.dumps(result),flush=True);return
            changed=False
            for name,a,b,v in gate_data:
                if current.express(v) is not None or admitted.express(v) is None:
                    continue
                ma,mb=current.express(a),current.express(b)
                if ma is not None and mb is not None:
                    assert current.add(v)
                    gates.append([ma,mb]);changed=True
            if changed:
                continue
            masks={1<<i for i in range(len(current.values))}
            for size in range(2,weight+1):
                for indices in itertools.combinations(range(len(current.values)),size):
                    masks.add(sum(1<<i for i in indices))
            for name,a,b,v in gate_data:
                for form in (a,b):
                    m=current.express(form)
                    if m is not None and m:
                        masks.add(m)
            forms=[(m,combination(m,current.values)) for m in sorted(masks)]
            rng.shuffle(forms)
            checked=0
            found=None
            for i,(ma,a) in enumerate(forms):
                for mb,b in forms[i+1:]:
                    checked += 1;attempts += 1
                    v=a&b
                    if admitted.express(v) is not None and current.express(v) is None:
                        found=(ma,mb,v);break
                    if checked>=pairs or time.monotonic()-plane_start>max(5,seconds/63):
                        break
                if found or checked>=pairs or time.monotonic()-plane_start>max(5,seconds/63):
                    break
            stages.append({"rank":len(current.values),"sparse_forms":len(forms),"pairs_checked":checked,"new_product":found is not None})
            if not found:
                break
            ma,mb,v=found
            assert current.add(v)
            gates.append([ma,mb])
        report={"hyperplane":plane,"computed_ANDs":len(gates),"span_rank":len(current.values),
                "pairs_checked":attempts,"stages":stages,"seconds":time.monotonic()-plane_start}
        reports.append(report)
        save()
        print(json.dumps(report),flush=True)
    result.update(status="no_witness_in_incomplete_search",seconds=time.monotonic()-started,
                  limits="Sparse, time-limited search; no lower-bound or scored-result claim.")
    save()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("netlist",type=Path)
    p.add_argument("--seconds",type=int,default=1800)
    p.add_argument("--pairs",type=int,default=150000)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--weight",type=int,default=3)
    a=p.parse_args()
    run(json.loads(a.netlist.read_text()),a.seconds,a.pairs,a.output,a.weight)


if __name__=="__main__":
    main()
