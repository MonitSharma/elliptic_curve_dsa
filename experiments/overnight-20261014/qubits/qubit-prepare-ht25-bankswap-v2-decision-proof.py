"""Prepare independent fixed-kernel proof outside the frozen N274 candidate."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
source,library,dest,kernel=map(lambda s:Path(s).resolve(),sys.argv[1:5])
KERNEL_SHA='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
assert hashlib.sha256(kernel.read_bytes()).hexdigest()==KERNEL_SHA
tree=dest/'source/point_add';assert not tree.exists();shutil.copytree(source/'src/point_add',tree)
private_kernel=dest/'phase-audit-kernel.rs';private_kernel.write_bytes(kernel.read_bytes())
width=int(re.search(r'pub const N:\s*usize\s*=\s*(\d+)\s*;', (tree/'pointadd_frogdrop.rs').read_text())[1])+417
assert width==692
names=[
 'ht25_fixed2379_and_quotient_boundaries_native',
 'ht25_fixed2379_exact_payload_native',
 'ht25_masked_add_full_sy_dirty_owner_inverse_phase',
 'ht25_preposition_reflection_and_q17_all_sy_inverse_phase',
 'ht25_reserve_bank_partition_dirty_inactive_inverse_phase',
 'ht25_transfer_bank32_full_sy_dirty_quotient_inverse_phase',
 'n275_sz_donor_boundaries_inverse_phase',
 'n275_k32_k24_partition_all_sy_words',
 'n275_v2_full_column_new_boundaries_native',
 'ph_owner_structured_q22_one_column_payload_native',
 'ph_owner_two_qbits_preposition_inverse_dirty_phase',
 'reserve9_columns_crossing_3713_positive_native',
 'reserve9_crossing_payload_3713_exact_shadow_native',
 'cap24_counterexample8048_exact_column_payload_native',
]
path=tree/'tests_midg_k24.rs';text=path.read_text();begin=text.index('fn symbolic(ops:');end=text.index('\nfn apply(',begin)
replacement='#[path='+json.dumps(private_kernel.as_posix())+']\nmod conditional_phase_kernel;\n'
replacement+='pub(crate) fn symbolic(ops:&[Op],q:Vec<u64>)->(Vec<u64>,u64){\n'
replacement+='let proof=conditional_phase_kernel::audit(ops,&q,&[]).expect("Exact fixed-kernel phase/value proof; cap failure inconclusive");\n'
replacement+='eprintln!("DECISION_DIAGRAM_PHASE_PROOF ops={} input_lanes=64 measurement_variables={} maximum_phase_size_bound={} maximum_quantum_size_bound={} scope=all_measurement_outcomes_fixed_inputs",ops.len(),proof.measurements,proof.maximum_phase_size_bound,proof.maximum_quantum_size_bound);\n'
replacement+='(proof.qubits,proof.measurements*64)\n}\n'
text=text[:begin]+replacement+text[end:]
chunks=text.split('\n#[test]');added=[]
for i,chunk in enumerate(chunks):
    match=re.search(r'fn (\w+)\(',chunk)
    if not match or match[1]not in names:continue
    name=match[1];symbolic_calls=chunk.count('symbolic(')
    if name=='ht25_fixed2379_and_quotient_boundaries_native':
        # The native test retains its expected-negative above-capacity case.
        # This proof deliberately admits only below-capacity input lanes.
        needle='let record=rec(&mut b,|b|column_pl(b,&mut fd,cp,&sc,None));';assert needle in chunk
        chunk=chunk.replace(needle,'if label=="q33554432"{continue;}'+needle)
    if symbolic_calls==0:
        needle='let back=run(&inverse,692,&|words|*words=got.q.clone());'
        if needle not in chunk:needle='let back=run(&inverse,692,&|w|*w=got.q.clone());'
        assert chunk.count(needle)==1,(name,'unrecognized inverse pattern')
        chunk=chunk.replace(needle,'let(fq,_)=symbolic(&forward,input.clone());assert_eq!(fq,expected);let(iq,_)=symbolic(&inverse,got.q.clone());assert_eq!(iq,input);'+needle)
        added.append(name)
    else:assert symbolic_calls==2,(name,symbolic_calls)
    chunks[i]=chunk
text='\n#[test]'.join(chunks)
for name in names:
    assert 'fn '+name+'(' in text,name
    text=re.sub(r'\b'+name+r'\b','coordinator_'+name,text)
path.write_text(text)
map_names=['n275_ordinary_three_lane_map_exact','n275_b0_three_lane_extension_controlled_replay']
path=tree/'tests_frogdrop.rs';text=path.read_text();chunks=text.split('\n#[test]');map_added=[]
for i,chunk in enumerate(chunks):
    match=re.search(r'fn (\w+)\(',chunk)
    if not match or match[1]not in map_names:continue
    name=match[1]
    forward_name='out'if name=='n275_b0_three_lane_extension_controlled_replay'else'f'
    needle=f'assert_eq!({forward_name}.phase, 0);';assert chunk.count(needle)==1,(name,'forward pattern')
    chunk=chunk.replace(needle,f'let(fq,_)=super::tests_midg_k24::symbolic(&b.ops[..forward],input.clone());assert_eq!(fq,{forward_name}.q,"ALLMR map forward full quantum state");'+needle)
    assert chunk.count('assert_eq!(both.phase, 0);')==1,(name,'both pattern')
    chunk=chunk.replace('assert_eq!(both.phase, 0);','let(bq,_)=super::tests_midg_k24::symbolic(&b.ops,input.clone());assert_eq!(bq,input,"ALLMR map entire forward/inverse");assert_eq!(both.phase, 0);')
    chunks[i]=chunk.replace('fn '+name+'(','fn coordinator_'+name+'(');map_added.append(name)
assert len(map_added)==2;path.write_text('\n#[test]'.join(chunks))
(dest/'src').mkdir(parents=True)
builder=(library/'src/bin/build_circuit.rs').read_text();serializer=builder[builder.index('const MAGIC:'):builder.index('\nfn main()')]
main='use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};\nuse circuit::Op;\nuse std::fs::{self,File};\nuse std::io::{BufWriter,Write};\nuse std::path::Path;\n#[allow(dead_code)]\n#[path='+json.dumps((tree/'mod.rs').as_posix())+']\nmod point_add;\n'+serializer+'\nfn main(){println!("HT25-v9 source-bound phase proof; no scorer");}\n'
(dest/'src/main.rs').write_text(main)
(dest/'Cargo.toml').write_text('[package]\nname="qubit_ht25_bankswap_v2_fixed_decision_proof"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(library.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n')
(dest/'rust-toolchain').write_bytes((library/'rust-toolchain').read_bytes())
hashes={p.relative_to(source/'src/point_add').as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()}
binding=dict(scope='ALLMR Boolean decision diagrams for fixed64-input lanes per native fixture; does not prove all curve inputs or a score',revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),source=str(source),point_add_patch_sha256=hashlib.sha256(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])).hexdigest(),source_sha256=hashes,component_constructor_width=width,frozen_kernel_sha256=KERNEL_SHA,selected_native_tests=names+map_names,added_phase_calls=added+map_added,research_test_sha256={name:hashlib.sha256((tree/name).read_bytes()).hexdigest()for name in ['tests_midg_k24.rs','tests_frogdrop.rs']},public_builder_serializer_source_sha256=hashlib.sha256((library/'src/bin/build_circuit.rs').read_bytes()).hexdigest())
(dest/'complete-source-binding.json').write_text(json.dumps(binding,indent=2)+'\n');print(json.dumps(binding,indent=2))
