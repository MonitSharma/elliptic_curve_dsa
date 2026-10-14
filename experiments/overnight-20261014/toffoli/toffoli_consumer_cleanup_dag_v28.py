"""Deterministic post-consumer phase-DAG retention, including seven carries."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_carry_cleanup_closure_v1 import phase_closure

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();start=time.monotonic();net=json.loads(args.netlist.read_bytes());raw,target,original=load(net)
    post=[raw[0]]+raw[7:15]+target[21:27];bank=original[15:];whole=Space(post+bank)
    final_global=phase_closure(post,post+bank,original)
    report={'status':'deterministic_postconsumer_phase_DAG_computed','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':16384,
            'global_final_phase_closure':final_global,'cases':[],'qualified_score':None,
            'guard_scope':'fin0/ttmfalse/nonlean/noESH; original31helpers; all low13 outputs written',
            'limits':'Exact abstract value/phase plan only. Actual source wiring, allocator/replanning, dirty quantum/classical state, higherword native proof and whole cost still separate.'}
    if final_global['status']!='free_quadratic_cleanup_basis_found':
        report.update(status='global_final_phase_closure_blocked',seconds=time.monotonic()-start)
        args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report['status']);return
    generated=[combination(item['original_affine_mask'],original) for item in final_global['chain']]
    full=Space(post+generated);assert len(full.values)==46
    dependencies=[];check=list(post)
    for item,value in zip(final_global['chain'],generated):
        d=item['pair_basis_rank'];pairs=list(itertools.combinations(range(d),2));mask=item['quadratic_mask']
        products=[check[i]&check[j] for i,j in pairs];assert combination(mask,products)==value
        used=set()
        for index,(i,j) in enumerate(pairs):
            if mask>>index&1:
                used.update(k-15 for k in (i,j) if k>=15)
        dependencies.append(sorted(used));check.append(value)
    assert len(generated)==31
    for name,required in [('higher_fields_only',target[9:21]),
                          ('all_lower_fields_and_carry6',target[2:21]+target[27:28])]:
        output_masks=[full.express(value) for value in required];assert all(mask is not None for mask in output_masks)
        selected=set(i-15 for mask in output_masks for i in range(15,46) if mask>>i&1)
        pending=list(selected)
        while pending:
            i=pending.pop()
            for j in dependencies[i]:
                if j not in selected:selected.add(j);pending.append(j)
        indices=sorted(selected);kept=[generated[i] for i in indices]
        keptspace=Space(post+kept);assert len(keptspace.values)==15+len(kept)
        mapped=[keptspace.express(value) for value in required];assert all(mask is not None for mask in mapped)
        early=phase_closure(post+kept,post+bank,original)
        final=phase_closure(post,post+kept,original)
        assert final['status']=='free_quadratic_cleanup_basis_found'
        # All seven consumed fields and original carry6 must survive linearly
        # for ordinary free carry erasure after the upper ladder.
        carry_controls=[keptspace.express(value) for value in target[2:9]+target[27:28]]
        carry_phase_ready=all(mask is not None for mask in carry_controls)
        for a,b,c in itertools.product([0,1],repeat=3):
            s=a^b^c;carry=(a&b)^(a&c)^(b&c)
            assert carry==((s&b)^(s&c)^(b&c)^b^c)
        newfixed=len(kept)+7
        case={'name':name,'retained_bank':len(kept),'retained_global_generator_indices':indices,
              'required_value_masks_in_retained_basis':mapped,'lower7_fields_and_carry6_masks':carry_controls,
              'early':early,'final':final,'both_bank_phase_closures_complete':early['status']=='free_quadratic_cleanup_basis_found',
              'all7carry_phase_ready':carry_phase_ready,'carry_phase_identity_cases':8,
              'carry_phase_identity':'carryout = finalbit*field + finalbit*carryin + field*carryin + field + carryin',
              'retained_consumer_carries':7,'fixed_upperladder_qubits':newfixed,
              'old_fixed_qubits':31,'fixed_upperladder_delta':newfixed-31,
              'prefix_peak_fixed_qubits':38,'upperladder_length_delta':-7,
              'prefix_main_value_ANDs':7,'upperladder_main_value_AND_delta':-7,
              'reconstruction_ANDs':0 if carry_phase_ready else None,
              'complete_abstract_zero_Toff_cleanup':carry_phase_ready and early['status']=='free_quadratic_cleanup_basis_found'}
        report['cases'].append(case)
    report.update(seconds=time.monotonic()-start,global_generator_dependencies=dependencies)
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps([{k:c[k] for k in ['name','retained_bank','fixed_upperladder_delta','all7carry_phase_ready','complete_abstract_zero_Toff_cleanup']} for c in report['cases']]),flush=True)
if __name__=='__main__':main()
