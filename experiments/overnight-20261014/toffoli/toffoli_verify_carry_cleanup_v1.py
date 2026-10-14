"""Independent truth/linear-rebase verifier and frozen Rust cleanup emitter."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load


def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('closure',type=Path)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--rust',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net)
    receipt=json.loads(args.closure.read_bytes());case=next(item for item in receipt['cases'] if item['fin']==0 and not item['tt_erased'])
    assert case['status']=='free_quadratic_cleanup_basis_found'
    c1=1<<15;c2=(1<<16)^c1;c3=(1<<17)^c2;c4=1<<18;c5=(1<<25)^c4;c6=(1<<27)^c5
    r1=1<<20;r2=(1<<21)^r1;r3=(1<<22)^r2
    physical={0:c1,1:c2,3:c4,6:r2,7:r3,8:(1<<23)^c3,10:c5,12:c6}
    # Exact qubit order: all original constructor gates except measured c3.
    physical_masks=[physical.get(j,1<<(15+j)) for j in range(31) if j!=2]
    data_masks=[1]+net['outputs'][21:27]+[1<<i for i in range(7,15)]
    assert data_masks==case['initial_original_masks']
    data=[combination(mask,original) for mask in data_masks]
    bank=[combination(mask,original) for mask in physical_masks]
    basis=Space(data+bank);assert len(basis.values)==45
    chain_values=[];repair_pairs=[]
    for direction in case['chain']:
        d=direction['pair_basis_rank'];current=data+chain_values
        assert d<=len(current)
        pairs=list(itertools.combinations(range(d),2));mask=direction['quadratic_mask']
        selected=[pair for j,pair in enumerate(pairs) if mask>>j&1]
        value=0
        for i,j in selected:value^=current[i]&current[j]
        assert value==combination(direction['original_affine_mask'],original)
        chain_values.append(value);repair_pairs.append(selected)
    assert len(chain_values)==30 and len(Space(data+chain_values).values)==45
    coordinates=[basis.express(value) for value in chain_values];assert all(mask is not None for mask in coordinates)
    matrix=[mask>>15 for mask in coordinates];data_parts=[mask&((1<<15)-1) for mask in coordinates]
    inverse_operations=[];reduced=list(matrix)
    for col in range(30):
        pivot=next(row for row in range(col,30) if reduced[row]>>col&1)
        if pivot!=col:
            reduced[pivot],reduced[col]=reduced[col],reduced[pivot];inverse_operations.append(['swap',pivot,col])
        for row in range(30):
            if row!=col and reduced[row]>>col&1:
                reduced[row]^=reduced[col];inverse_operations.append(['cx',col,row])
    assert reduced==[1<<i for i in range(30)]
    operations=list(reversed(inverse_operations));replay=[1<<(15+i) for i in range(30)]
    for kind,i,j in operations:
        if kind=='swap':replay[i],replay[j]=replay[j],replay[i]
        else:replay[j]^=replay[i]
    for i,mask in enumerate(data_parts):replay[i]^=mask
    assert replay==coordinates
    assert all(combination(mask,data+bank)==value for mask,value in zip(replay,chain_values))
    # Emit only source-side linear operations and one independent HMR phase coefficient per helper.
    lines=['//! Frozen exact non-lean c3-loan cleanup; component research, no score claim.',
           'use super::*;','pub(super) fn run(c:&mut Builder,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],bank:&[QubitId;30]) {',
           '    let mut data=vec![Lin::k(true)];data.extend(acc[..6].iter().map(|&q|l(q)));',
           '    data.extend(e.iter().chain(nm.iter()).chain(shift.iter()).map(|&q|l(q)));']
    for kind,i,j in operations:lines.append(f'    c.{kind}(bank[{i}],bank[{j}]);')
    for j,mask in enumerate(data_parts):
        for i in range(15):
            if mask>>i&1:lines.append(f'    lin_xor_into(c,&data[{i}],bank[{j}]);')
    for j in range(29,-1,-1):
        lines.extend([f'    let m=c.alloc_bit();c.hmr(bank[{j}],m);c.push_condition(m);'])
        for left,right in repair_pairs[j]:
            a=f'data[{left}].clone()' if left<15 else f'l(bank[{left-15}])'
            b=f'data[{right}].clone()' if right<15 else f'l(bank[{right-15}])'
            lines.append(f'    lin_cz(c,&({a}),&({b}));')
        lines.extend([f'    c.pop_condition();c.free_bit(m);c.release_clean(bank[{j}]);'])
    lines.append('}')
    args.rust.write_bytes(('\n'.join(lines)+'\n').encode())
    proof={'status':'all16384_truth_rows_and_reversible_physical_rebase_verified',
           'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
           'closure_sha256':hashlib.sha256(args.closure.read_bytes()).hexdigest(),'domain_rows':1<<14,
           'guard':'loan && fin==0 && !ttm && !lean45 && drop==0',
           'physical_original_masks':physical_masks,'final_data_original_masks':data_masks,
           'cleanup_original_masks':[item['original_affine_mask'] for item in case['chain']],
           'target_coordinates_over_data15_bank30':coordinates,'rebase_operations':operations,'data_xor_masks':data_parts,
           'phase_pairs':repair_pairs,'rebase_gates':len(operations)+sum(mask.bit_count() for mask in data_parts),
           'phase_CZ_terms':sum(map(len,repair_pairs)),'measurements':30,'charged_cleanup_Toffolis':0,
           'rust_sha256':hashlib.sha256(args.rust.read_bytes()).hexdigest(),'native_verified':False,
           'limits':'Source-bound changed carry-loan non-lean primitive only. Physical gate mapping, every independent measurement coefficient, dirty passengers, producer and complete builder not yet verified.'}
    args.output.write_bytes((json.dumps(proof,indent=2)+'\n').encode())
    print(json.dumps({key:proof[key] for key in ['status','rebase_gates','phase_CZ_terms','measurements','charged_cleanup_Toffolis','rust_sha256']}))


if __name__=='__main__':main()
