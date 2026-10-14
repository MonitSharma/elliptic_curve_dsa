"""Decide attainment of an AND rank bound by exhaustive restricted closure.

When m new independent functions are necessary and exactly m ANDs are allowed,
every AND truth function must lie in the final affine+output span W. Close the
current span under every product of two current affine forms that stays in W.
If closure stalls below W, no m-AND program over this exact interface exists.
This does not bound larger programs that temporarily leave W.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time


def pivots(values):
    result = {}
    for value in values:
        v = value
        while v and (b := v.bit_length()-1) in result:
            v ^= result[b]
        if v:
            result[v.bit_length()-1] = v
    return result


def residual(v, table):
    while v and (b := v.bit_length()-1) in table:
        v ^= table[b]
    return v


def solve(bundle, max_span=16):
    inputs = [int(v,16) for v in bundle["input_columns_hex"]]
    outputs = [int(v,16) for v in bundle["target_columns_hex"]]
    rows = {}
    for r in range(1<<14):
        x = tuple(v>>r&1 for v in inputs)
        y = tuple(v>>r&1 for v in outputs)
        assert x not in rows or rows[x] == y
        rows[x] = y
    items = list(rows.items())
    source = [sum(x[i]<<r for r,(x,y) in enumerate(items)) for i in range(len(inputs))]
    target = [sum(y[i]<<r for r,(x,y) in enumerate(items)) for i in range(len(outputs))]
    vals = []
    input_indices = []
    for i,v in enumerate(source):
        if residual(v,pivots(vals)):
            vals.append(v)
            input_indices.append(i)
    w = pivots(source+target)
    stages = []
    gates = []
    started = time.monotonic()
    incomplete = False
    while len(pivots(vals)) < len(w):
        current = pivots(vals)
        if len(current) > max_span:
            incomplete = True
            break
        forms = [0]
        for v in vals:
            forms += [x^v for x in forms]
        checked = 0
        found = None
        for i, a in enumerate(forms):
            for j in range(i+1,len(forms)):
                checked += 1
                v = a & forms[j]
                if residual(v,w) == 0 and residual(v,current) != 0:
                    found = (i,j,v)
                    break
            if found:
                break
        stages.append({"current_span_rank":len(current), "affine_forms":len(forms),
                       "pairs_examined":checked,"extension_found":found is not None})
        if not found:
            break
        i,j,v = found
        gates.append([i,j])
        vals.append(v)
    return {"cut":bundle["cut"], "compressed_exact_rows":len(items), "source_rows":1<<14,
            "input_span_rank":len(pivots(source)), "required_final_span_rank":len(w),
            "closure_span_rank":len(pivots(vals)), "rank_bound_attainable":None if incomplete else len(pivots(vals))==len(w),
            "complete":not incomplete,"maximum_enumerated_span":max_span,"independent_input_indices":input_indices,
            "witness_gates":gates,"stages":stages,"seconds":time.monotonic()-started,
            "limits":"All affine products exhaustively checked only if closure stalls. This decides rank-bound attainability, not larger circuit optimum or phase cost."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("targets",type=Path)
    p.add_argument("--index",type=int,default=0)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--max-span",type=int,default=16)
    args = p.parse_args()
    raw=args.targets.read_bytes()
    report=solve(json.loads(raw)[args.index],args.max_span)
    report["targets_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
