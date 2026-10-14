"""Exact closure in all 63 source-span hyperplanes for <=30-AND witnesses.

This restricts every new function to the original constructor's full internal
span. A negative result does not exclude circuits with functions outside it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space
from toffoli_quadratic_closure import closure,load
from toffoli_factor_solver import solve


def main():
    p=argparse.ArgumentParser();p.add_argument("netlist",type=Path)
    p.add_argument("--seconds",type=int,default=1800);p.add_argument("--timeout",type=int,default=10)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());raw,targets,original=load(net)
    full=Space(raw+targets);outside=[]
    for i,v in enumerate(original[len(raw):]):
        if full.add(v):outside.append((1<<(len(raw)+i),v))
    assert len(outside)==6
    started=time.monotonic();reports=[]
    result={"status":"running","source_lf_sha256":net["source_lf_sha256"],
            "netlist_sha256":hashlib.sha256(a.netlist.read_bytes()).hexdigest(),"planes":reports,
            "exact_domain_size":1<<net["input_count"],"original_AND_count":31,
            "scope":"Every gate lies in the selected45-dimensional hyperplane of the original46-dimensional internal span. Native cleanup and global optimality are not established."}
    def save():a.output.write_bytes((json.dumps(result,indent=2)+"\n").encode())
    planes=sorted(range(1,64),key=lambda x:(x.bit_count(),x))
    for plane in planes:
        if time.monotonic()-started>=a.seconds:break
        pivot=(plane&-plane).bit_length()-1
        extras=[v ^ (outside[pivot][1] if plane>>j&1 else 0) for j,(mask,v) in enumerate(outside) if j!=pivot]
        extra_masks=[mask ^ (outside[pivot][0] if plane>>j&1 else 0) for j,(mask,v) in enumerate(outside) if j!=pivot]
        augmented=dict(net);augmented["outputs"]=net["outputs"]+extra_masks
        gates=[];steps=[];plane_start=time.monotonic()
        record={"hyperplane":plane,"extra_masks":extra_masks,"steps":steps}
        reports.append(record)
        while time.monotonic()-started<a.seconds:
            current=closure(raw,targets,extras,prefix=gates)
            gates=current["gates"];steps.append({"closure":current})
            save()
            if current["status"]=="value_witness_found":
                assert len(gates)<=30
                result.update(status="value_witness_found",AND_count=len(gates),gates=gates,
                              outputs=current["outputs"],hyperplane=plane,seconds=time.monotonic()-started,
                              complete_native_cleanup_verified=False,submission_ready=False)
                save();print(json.dumps({"status":result["status"],"AND_count":len(gates),"hyperplane":plane}),flush=True);return
            if current["status"]=="exact_quadratic_span_obstruction":
                record["status"]=current["status"];break
            factor=solve(augmented,{"gates":gates},len(gates),min(a.timeout,max(1,int(a.seconds-(time.monotonic()-started)))))
            steps[-1]["factor"]=factor
            if factor["status"]=="sat":gates.append([factor["a"],factor["b"]]);continue
            record["status"]="exact_affine_product_obstruction" if factor["status"]=="unsat" else "factor_unknown_unresolved"
            break
        record.update(final_ANDs=len(gates),seconds=time.monotonic()-plane_start)
        save();print(json.dumps({"hyperplane":plane,"status":record.get("status","incomplete"),"gates":len(gates),"seconds":record["seconds"]}),flush=True)
    result.update(status="no_witness_in_examined_planes",seconds=time.monotonic()-started,
                  all_63_planes_completed=len(reports)==63 and all(v.get("status","").startswith("exact_") for v in reports),
                  limits="Only original-span programs covered. Factor UNSAT receipts are solver results without saved formal proof certificates.")
    save()


if __name__=="__main__":main()
