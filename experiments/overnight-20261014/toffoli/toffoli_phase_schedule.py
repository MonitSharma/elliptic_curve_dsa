"""Search interleaved low-result writes and exact quadratic phase erasures."""
import argparse
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_phase_basis import erase_order,phase_expression


def main():
    p=argparse.ArgumentParser();p.add_argument("netlist",type=Path);p.add_argument("basis",type=Path)
    p.add_argument("--states",type=int,default=3000);p.add_argument("--seconds",type=int,default=60)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());basis=json.loads(a.basis.read_text());raw,targets,original=load(net)
    rows=basis["basis_rows"]
    banks=[(name,combination(mask,original[len(raw):])) for name,mask in rows]
    banks,early,blocked=erase_order(raw,banks,[name for name,v in banks if name.startswith("dead")],"reverse")
    assert not blocked
    n=len(banks);seen=set();start=time.monotonic();best=[]
    def current_data(written):
        data=list(raw)
        for i in range(6):
            if written>>i&1:data[i+1]=targets[21+i]
        return data
    def dfs(written,alive,path):
        nonlocal best
        key=written,alive
        if key in seen:return None
        seen.add(key)
        if len(path)>len(best):best=path
        if len(seen)>a.states or time.monotonic()-start>a.seconds:return None
        if written==63 and not alive:return path
        data=current_data(written)
        indices=[i for i in range(n) if alive>>i&1]
        names=[banks[i][0] for i in indices]
        vals=data+[banks[i][1] for i in indices]
        pending=[targets[21+i] for i in range(6) if not written>>i&1]
        def priority(i):
            number=int(banks[i][0][4:])
            if number>=7:return 0,-number
            return 1,[0,5,6,4,3,2,1].index(number)
        for i in sorted(indices,key=priority):
            remain=[j for j in indices if j!=i]
            available=data+[banks[j][1] for j in remain]
            space=Space(available)
            if any(space.express(v) is None for v in pending):continue
            expression=phase_expression(banks[i][1],available)
            if expression is None:continue
            step={"kind":"erase","wire":banks[i][0],"available_order":[f"data{k}" for k in range(len(data))]+[banks[j][0] for j in remain],"phase_terms":expression}
            result=dfs(written,alive^(1<<i),path+[step])
            if result is not None:return result
        space=Space(vals)
        assert len(space.values)==len(vals)
        for bit in [5,4,3,2,1,0]:
            if written>>bit&1:continue
            mask=space.express(targets[21+bit])
            if mask is None or not mask>>(bit+1)&1:continue
            step={"kind":"write","bit":bit,"available_order":[f"data{k}" for k in range(len(data))]+names,
                  "xor_mask":mask^(1<<(bit+1))}
            result=dfs(written|(1<<bit),alive,path+[step])
            if result is not None:return result
        return None
    schedule=dfs(0,(1<<n)-1,[])
    report={"status":"full_free_phase_schedule_found" if schedule is not None else "bounded_search_no_schedule",
            "source_lf_sha256":net["source_lf_sha256"],"states":len(seen),"seconds":time.monotonic()-start,
            "basis_rows":rows,"early_erasures":early,"schedule":schedule,"longest_partial_schedule":best,
            "limits":"Every generated phase identity is exhaustive on16384inputs. No native circuit, count or benchmark result yet; bounded failure is not impossibility."}
    a.output.write_bytes((json.dumps(report,indent=2)+"\n").encode())
    print(json.dumps({"status":report["status"],"states":len(seen),"seconds":report["seconds"],"schedule_length":None if schedule is None else len(schedule),"longest_partial":len(best)},indent=2))


if __name__=="__main__":main()
