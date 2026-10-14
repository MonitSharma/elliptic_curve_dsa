"""Exact free-quadratic cleanup closure for the consumer's changed c3 loan basis.

Unlike W40, old acc3 is overwritten and y3 is rebased by c3 before c3 leaves.
Only non-lean physical banks are modeled. This is a phase-interface value-span
calculation, not native execution or a complete circuit qualification.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load


def phase_closure(seed,interface,original):
    h=Space(interface);s=Space(seed);o=Space(original)
    assert all(h.express(value) is not None for value in seed)
    initial=[o.express(value) for value in s.values];chain=[];stages=[]
    while True:
        d=len(s.values);pairs=list(itertools.combinations(range(d),2))
        products=[s.values[i]&s.values[j] for i,j in pairs];table={};new=[]
        def project(value):
            for pivot,(row,mask) in sorted(h.rows.items(),reverse=True):
                if value>>pivot&1:value^=row
            return value
        for i,value in enumerate(products):
            residual=project(value);mask=1<<i
            while residual:
                pivot=residual.bit_length()-1
                if pivot not in table:table[pivot]=residual,mask;break
                row,coordinate=table[pivot];residual^=row;mask^=coordinate
            if not residual:
                candidate=combination(mask,products)
                if s.add(candidate):
                    assert h.express(candidate) is not None
                    new.append({'original_affine_mask':o.express(candidate),'quadratic_mask':mask,'pair_basis_rank':d})
        stages.append({'rank_before':d,'rank_after':len(s.values),'quadratic_products':len(pairs),'extensions':len(new)})
        chain.extend(new)
        if not new or len(s.values)==len(h.values):break
    return {'status':'free_quadratic_cleanup_basis_found' if len(s.values)==len(h.values) else 'proper_phase_closed_subspace_obstruction',
            'initial_rank':len(initial),'interface_rank':len(h.values),'closed_rank':len(s.values),
            'initial_original_masks':initial,'chain':chain,'stages':stages,
            'all_interface_coordinates_in_closed_basis':[s.express(value) for value in interface]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_text());raw,targets,original=load(net)
    c1=original[15];c2=original[16]^c1;c3=original[17]^c2
    reports=[];started=time.monotonic()
    for fin in [0,1,2]:
        for tt_erased in [False,True]:
            data=list(raw);data[4]=targets[24]
            removed={2}
            if fin>=1:removed.add(1)
            if fin>=2:removed.add(0)
            if tt_erased:removed.add(4)
            bank=[value^(c3 if j==8 else 0) for j,value in enumerate(original[15:]) if j not in removed]
            # A linear write puts final bits4/5 in data before helper cleanup.
            data[5:7]=targets[25:27]
            interface=data+bank
            final=list(raw);final[4:7]=targets[24:27]
            # In fin>0, c1/c2 must still be rebuilt by the ordinary low tail.
            if fin==0:final[1:4]=targets[21:24]
            result=phase_closure(final,interface,original)
            result.update(fin=fin,tt_erased=tt_erased,removed_original_gate_indices=sorted(removed),
                          physical_scope='non-lean bank; acc3 final and y3+c3 basis; acc4/5 final linear writes; fin>0 low0..2 still original for ordinary low carry rebuild')
            reports.append(result)
    receipt={'status':'changed_consumer_carry_phase_interfaces_computed','source_lf_sha256':net['source_lf_sha256'],
             'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':1<<14,
             'cases':reports,'seconds':time.monotonic()-started,'native_verified':False,
             'limits':'Quadratic phase-span construction on the unrestricted14-input primitive and non-lean bank only. Each constructive basis requires exact physical rebase, every independent measurement coefficient and producer/complete-builder integration. Negative result excludes all-free quadratic erasure within that explicit fixed span, not charged cleanup or all circuit optimizations.'}
    args.output.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps([{key:item[key] for key in ['fin','tt_erased','status','initial_rank','interface_rank','closed_rank']} for item in reports]))


if __name__=='__main__':main()
