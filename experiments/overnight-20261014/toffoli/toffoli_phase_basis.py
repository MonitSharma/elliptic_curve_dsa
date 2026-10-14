"""Test bank-basis loans with complete quadratic measurement-phase repair.

Construction keeps its31ANDs. Rebase the bank so25directions span every value
needed by the consumer and six directions are unused. Early erasure and late
cleanup are allowed only with an exact quadratic phase identity on all16384
source inputs. This is a complete-cost/lifetime lead, not a scored result.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load


def phase_expression(target,available):
    terms=[("one",0,0)]+[("z",i,i) for i in range(1,len(available))]
    values=[available[0]]+available[1:]
    for i,j in itertools.combinations(range(1,len(available)),2):
        terms.append(("cz",i,j));values.append(available[i]&available[j])
    rows={}
    for index,v in enumerate(values):
        mask=1<<index
        while v:
            bit=v.bit_length()-1
            if bit not in rows:rows[bit]=v,mask;break
            x,m=rows[bit];v ^= x;mask ^= m
    answer=0;v=target
    while v:
        bit=v.bit_length()-1
        if bit not in rows:return None
        x,m=rows[bit];v ^= x;answer ^= m
    assert combination(answer,values)==target
    return [terms[i] for i in range(len(terms)) if answer>>i&1]


def erase_order(data,banks,allowed,priority="forward"):
    banks=list(banks);allowed=set(allowed);steps=[]
    while allowed:
        found=None
        indices=list(range(len(banks)))
        if priority=="reverse":indices.reverse()
        elif priority=="source":
            def score(index):
                name=banks[index][0]
                if name.startswith("dead"):return (0,-int(name[4:]))
                number=int(name[4:])
                if number>=7:return (1,-number)
                return (2,[0,5,6,4,3,2,1].index(number))
            indices.sort(key=score)
        for index in indices:
            name,v=banks[index]
            if name not in allowed:continue
            other=[b for j,b in enumerate(banks) if j!=index]
            available=data+[v for name,v in other]
            expression=phase_expression(v,available)
            if expression is not None:
                found=index,other,expression;break
        if found is None:
            return banks,steps,sorted(allowed)
        index,other,expression=found
        name,v=banks[index]
        steps.append({"erase":name,"available_order":[f"data{i}" for i in range(len(data))]+[name for name,v in other],
                      "phase_terms":expression,"tested_truth_rows":1<<14})
        allowed.remove(name);banks=other
    return banks,steps,[]


def main():
    p=argparse.ArgumentParser();p.add_argument("netlist",type=Path);p.add_argument("--output",type=Path,required=True)
    p.add_argument("--early-order",default="reverse");p.add_argument("--late-order",default="source")
    a=p.parse_args();net=json.loads(a.netlist.read_text());raw,targets,original=load(net)
    start=time.monotonic();modraw=Space();rows=[]
    # Carry6 first remains a physical wire; low-write raw matrix stays unchanged.
    order=[27]+list(range(21,27))+list(range(21))
    for index in order:
        mask=net["outputs"][index]>>len(raw)
        if modraw.add(mask):rows.append((f"live{len(rows)}",mask))
    live_count=len(rows)
    assert live_count==25
    for j in range(len(net["gates"])):
        mask=1<<j
        if modraw.add(mask):rows.append((f"dead{len(rows)-live_count}",mask))
    assert len(rows)==31
    banks=[(name,combination(mask,original[len(raw):])) for name,mask in rows]
    initial_banks=list(banks)
    banks,early,early_blocked=erase_order(raw,banks,[name for name,v in banks if name.startswith("dead")],a.early_order)
    late=[];late_blocked=[]
    changed=list(raw)
    changed[1:7]=targets[21:27]
    banks,late,late_blocked=erase_order(changed,banks,[name for name,v in banks],a.late_order)
    status="all_phase_erasures_found" if not early_blocked and not late_blocked else "partial_early_loan_with_full_cleanup" if early and not late_blocked else "phase_erase_obstruction_or_greedy_deadend"
    report={"status":status,
            "source_lf_sha256":net["source_lf_sha256"],"constructor_ANDs":31,"live_bank_for_consumer":25,
            "basis_rows":rows,"early_erasures":early,"early_blocked":early_blocked,
            "late_erasures":late,"late_blocked":late_blocked,
            "remaining_banks":[name for name,v in banks],"seconds":time.monotonic()-start,
            "limits":"No native integration or Toffoli saving measured. Each quadratic phase identity is exhaustive on the full source domain; greedy failure is not impossibility."}
    a.output.write_bytes((json.dumps(report,indent=2)+"\n").encode())
    print(json.dumps({"status":report["status"],"early":len(early),"late":len(late),"early_blocked":early_blocked,"late_blocked":late_blocked,"seconds":report["seconds"]},indent=2))


if __name__=="__main__":main()
