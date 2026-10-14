"""Exact quadratic phase erasure across every late-bank hyperplane.

This tests linear rebasing of the six remaining bank directions after the
recorded greedy cleanup. A failure is an interface obstruction at this state,
not a bound on alternative cleanup orders or higher-degree phase repair.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space, combination
from toffoli_quadratic_closure import load
from toffoli_phase_basis import phase_expression


def main():
    p=argparse.ArgumentParser();p.add_argument("netlist",type=Path);p.add_argument("basis",type=Path)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());basis=json.loads(a.basis.read_text());raw,targets,original=load(net)
    rows=[(name,mask) for name,mask in basis["basis_rows"] if name in basis["remaining_banks"]]
    assert len(rows)==6
    values=[combination(mask,original[len(raw):]) for name,mask in rows]
    data=list(raw);data[1:7]=targets[21:27]
    assert len(Space(data+values).values)==21
    records=[];started=time.monotonic()
    for plane in range(1,64):
        pivot=(plane&-plane).bit_length()-1
        remain=[values[j] ^ (values[pivot] if plane>>j&1 else 0) for j in range(6) if j!=pivot]
        masks=[(1<<j)^((1<<pivot) if plane>>j&1 else 0) for j in range(6) if j!=pivot]
        expression=phase_expression(values[pivot],data+remain)
        records.append({"normal":plane,"pivot":pivot,"bank_basis_masks":masks,
                        "quadratic_phase_terms":expression,"status":"phase_erase_found" if expression is not None else "exact_quadratic_phase_obstruction"})
    count=sum(r["quadratic_phase_terms"] is not None for r in records)
    report={"status":"at_least_one_rebased_erase" if count else "no_quadratic_erase_in_all_63_late_hyperplanes",
            "source_lf_sha256":net["source_lf_sha256"],"netlist_sha256":hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            "basis_receipt_sha256":hashlib.sha256(a.basis.read_bytes()).hexdigest(),
            "remaining_bank_names":[name for name,mask in rows],"normal_count":63,"erasable_planes":count,
            "domain_rows":1<<14,"planes":records,"seconds":time.monotonic()-started,
            "scope":"All XOR bank rebases at this exact 15-data/6-bank cleanup state. Does not exclude other cleanup paths, extra temporary ANDs, higher-degree phase terms or different consumer contracts."}
    a.output.write_bytes((json.dumps(report,indent=2)+"\n").encode());print(json.dumps({k:report[k] for k in ["status","erasable_planes","seconds"]}))


if __name__=="__main__":main()
