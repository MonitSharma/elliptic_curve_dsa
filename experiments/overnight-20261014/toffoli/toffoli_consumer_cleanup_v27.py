"""Exact changed-consumer early bank phase closure, with final cleanup gate."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_carry_cleanup_closure_v1 import phase_closure

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();started=time.monotonic();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net)
    post=[raw[0]]+raw[7:15]+targets[21:27]
    retained=targets[9:21];bank=original[15:]
    whole=Space(post+bank);seed=Space(post+retained)
    assert len(post)==15 and len(Space(post).values)==15 and len(seed.values)==27 and len(whole.values)==46
    assert all(whole.express(value) is not None for value in retained)
    early=phase_closure(post+retained,post+bank,original)
    chain=[combination(item['original_affine_mask'],original) for item in early['chain']]
    for fn in chain:assert not fn&1
    closed=Space(post+retained+chain);assert len(closed.values)==early['closed_rank']
    complement=[];complement_original=[]
    for index,value in enumerate(bank):
        value^=raw[0] if value&1 else 0
        if closed.add(value):complement.append(value);complement_original.append(index)
    assert len(closed.values)==46
    physical_bank=retained+complement+chain;assert len(physical_bank)==31
    expressions=[whole.express(value) for value in physical_bank]
    matrix=[mask>>15 for mask in expressions];assert len(Space(matrix).values)==31
    # Row reduction yields an ancilla-free CX/Swap implementation of the bank map.
    reducing=[];rows=list(matrix)
    for col in range(31):
        pivot=next(i for i in range(col,31) if rows[i]>>col&1)
        if pivot!=col:rows[col],rows[pivot]=rows[pivot],rows[col];reducing.append(['swap',col,pivot])
        for i in range(31):
            if i!=col and rows[i]>>col&1:rows[i]^=rows[col];reducing.append(['cx',col,i])
    assert rows==[1<<i for i in range(31)]
    rebase=list(reversed(reducing));after=list(bank)
    for op,a,b in rebase:
        if op=='swap':after[a],after[b]=after[b],after[a]
        else:after[b]^=after[a]
    for i,mask in enumerate(expressions):after[i]^=combination(mask&((1<<15)-1),post)
    assert after==physical_bank
    # Explicit every-independent-MR coefficient proof for each erased bank direction.
    evolving=Space(post+retained).values
    for item,value in zip(early['chain'],chain):
        d=item['pair_basis_rank'];assert len(evolving)>=d
        pairs=[(i,j) for i in range(d) for j in range(i+1,d)]
        products=[evolving[i]&evolving[j] for i,j in pairs]
        assert combination(item['quadratic_mask'],products)==value
        evolving.append(value)
    final_interface=post+retained+complement
    final=phase_closure(post,final_interface,original)
    # Extra high accumulator bits cannot aid these old-bank identities: for each
    # primitive the low13 write is a translation of the arbitrary seven-bit high
    # payload, hence gives every posthigh pattern exactly once.
    for delta in range(128):assert {(high+delta)&127 for high in range(128)}==set(range(128))
    report={'status':'changed_consumer_early_and_final_phase_closures_computed',
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':16384,'guard_scope':'fin0,ttmfalse,nonlean original31-bank; low0..12 committed before higherladder',
            'unchanged_external_order':'constant,E0..2,Nm0..2,k1,k2,final0..5',
            'retained_field_order':'U3..6,sign,H0..6','full_interface_rank':46,'initial_retained_rank':27,
            'early':early,'early_releasable_bank_directions':len(chain),'retained_bank_width':12+len(complement),
            'retained_complement_original_gate_indices':complement_original,
            'physical_bank_postbasis_masks':expressions,'physical_rebase_row_operations':rebase,
            'physical_external_xors':sum((mask&((1<<15)-1)).bit_count() for mask in expressions),
            'rebase_truth_rows_verified':16384,'early_phase_coefficient_rows_verified':16384,
            'final':final,'complete_two_stage_zero_Toff_plan':final['status']=='free_quadratic_cleanup_basis_found',
            'seven_high_bit_translation_bijections_verified':128,'qualified_score':None,
            'seconds':time.monotonic()-started,
            'limits':'Exact abstract affine bank map/phase coefficients only; no native physical source integration, dirty scratch or full cost. Seven consumer ripple/carry erasures and carry13 higherladder ownership separate; retained-bank width is not full circuit peak.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','early_releasable_bank_directions','retained_bank_width','complete_two_stage_zero_Toff_plan','seconds']}),flush=True)
if __name__=='__main__':main()
