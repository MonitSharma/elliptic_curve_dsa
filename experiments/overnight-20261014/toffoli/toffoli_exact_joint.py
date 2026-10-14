"""Full joint rank closure with exact affine-factor solver fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from toffoli_factor_solver import solve
from toffoli_quadratic_closure import closure,load


def main():
    p=argparse.ArgumentParser()
    p.add_argument("netlist",type=Path);p.add_argument("--seconds",type=int,default=120)
    p.add_argument("--timeout",type=int,default=10);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    net=json.loads(a.netlist.read_text());raw,targets,_=load(net)
    started=time.monotonic();gates=[];steps=[]
    report={"source_lf_sha256":net["source_lf_sha256"],"netlist_sha256":hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            "exact_domain_size":1<<net["input_count"],"old_ANDs":len(net["gates"]),"steps":steps,"status":"running"}
    def save():a.output.write_bytes((json.dumps(report,indent=2)+"\n").encode())
    while time.monotonic()-started<a.seconds:
        current=closure(raw,targets,prefix=gates)
        gates=current["gates"]
        steps.append({"closure":current})
        print(json.dumps({"closure_status":current["status"],"gates":len(gates)}),flush=True)
        save()
        if current["status"]!="nondecomposable_kernel_unresolved":
            report.update(status=current["status"],gates=gates,AND_count=len(gates),seconds=time.monotonic()-started)
            if current["status"]=="value_witness_found":report["outputs"]=current["outputs"]
            save();return
        factor=solve(net,{"gates":gates},len(gates),min(a.timeout,max(1,int(a.seconds-(time.monotonic()-started)))))
        steps[-1]["factor"]=factor
        print(json.dumps({"factor_status":factor["status"],"prefix":len(gates),"seconds":factor["seconds"]}),flush=True)
        if factor["status"]=="sat":
            gates.append([factor["a"],factor["b"]])
            save();continue
        report.update(status="exact_affine_product_obstruction" if factor["status"]=="unsat" else "factor_unknown_unresolved",
                      gates=gates,AND_count=len(gates),seconds=time.monotonic()-started)
        save();return
    report.update(status="time_budget_incomplete",gates=gates,AND_count=len(gates),seconds=time.monotonic()-started)
    save()


if __name__=="__main__":main()
