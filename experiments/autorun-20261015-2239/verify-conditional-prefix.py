"""Independent binding, all-port, binary and packed-word review; no runtime enable."""
from pathlib import Path
from array import array
import hashlib,json,struct
r=Path(__file__).resolve().parent.parent/'prefilter-20261015';p=r/'a29-conditional-prefix-v1';f=r/'a29-conditional-family-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
report=json.loads((p/'global.json').read_text());manifest=json.loads((p/'local-guards.json').read_text())
assert (p/'global.exit').read_text().strip()=='0'
assert (p/'global-before.sha256').read_bytes()==(p/'global-after.sha256').read_bytes()
assert '34 passed; 0 failed' in (p/'global.tests.log').read_text()
assert report['source_old']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert report['source_new']=='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522'
assert report['stop_new']==3991609 and report['stop_old']==3985789
assert report['protected_full_state_prefix_seeds']==report['protected_guard_false_original_A29_prefix_pairs']==4
assert len(report['composed_guards'])==len(manifest['frames'])==29
assert [x['tick'] for x in report['composed_guards']]==list(range(100,129))
bindings=json.loads((f/'actual-fullstream-frame-binding.json').read_text())
assert bindings['status']=='ALL29_ACTUAL_OLD_NEW_FRAMES_AND_ALL_OUTSIDE_OPS_BYTE_IDENTICAL'
assert len(bindings['frames'])==29
classical=json.loads((f/'live-classical-proof.json').read_text())
assert classical['arbitrary_entry_bits'] and classical['all_changed_middle_draws_independent']
assert classical['all_region_boundaries_empty_scope'] and len(classical['rows'])==29
for row in classical['rows']:
    assert row['status']=='EXACT_LIVE_CLASSICAL_PROJECTION_PASS'
    assert all(not v['live'] or v['equal'] for v in row['checks'].values())
for frame,composed in zip(manifest['frames'],report['composed_guards']):
    tick=frame['tick'];result=json.loads((f/f'tick-{tick}.result.json').read_text())
    raw=(f/f'tick-{tick}.guard.bin').read_bytes()
    assert sha(raw)==frame['local_guard_sha256']
    assert result['status']=='PAIRED_FULL_QUANTUM_INTERFACE_PASS_INPUT_ONLY_DIFFERENCE_GUARD'
    assert result['old_local_status']==result['new_local_status']=='EXACT_PROOF'
    assert result['required_A29_prefix_zero_qids']==[]
    assert result['new_region_digest']==frame['actual_new_digest']==composed['new_digest']
    assert result['unresolved_common_qids']==[] and result['delta_rng_terms']==0
    assert result['shared_input_and_dag_namespace'] and result['independent_internal_mr_old_new']
    assert all(d['rng_terms']==0 for d in result['all_nonzero_q_differences'])
    assert [x[0] for x in result['input_ports']]==list(range(1234))
    assert raw[:8]==b'MRMASK01' and struct.unpack_from('<QQQ',raw,8)==(result['guard_compiled_nodes'],1234,1)
    assert composed['all_substituted_quantum_ports_globally_mr_free']
    assert composed['local_guard_sha256']==sha(raw)
# The actual compiler/evaluator, before its metadata-only exporter, is frozen.
old=(r/'tool/src/mask_program_trace.rs').read_bytes();new=(r/'tool/src/a29_mask_program_trace.rs').read_bytes()
assert old.split(b'fn export_mask_program(')[0]==new.split(b'fn export_mask_program(')[0]
expected_kernels={'input_anf_dag_trace.rs':'41560814e64d5cd314c2485704cd4ff4b6280855bc666883b27fec29d0762282',
 'global_rng_anf_retained_masks.rs':'961494a454458919d9f3b0975e8559b59bd5b33f983566b0bf121db854b994f0',
 'reset_projection.rs':'df92a050c855c173daef5ed901c1a6d2d0905543c67b45131d28e5169c17761e',
 'reset_projection_symbols.rs':'8ad9ee8fe585875beaba92babda446aff076523b1ecf77a782f5822cd761c5ee',
 'shadow_value_contract_bound.rs':'e1a63c6fec351ca45ae6095720fe7499d5cbe0952be3de839328ef5c4750a2da',
 'shadow_apply_region_bound.rs':'ba50acaacbc15448cfe1116bf4efac232a3089e388d2f9db4592e71656c69989'}
for name,h in expected_kernels.items():assert sha((r/'tool/src'/name).read_bytes())==h,name
# Cross-check all1024 public ports against the source ABI, including classical A.
abi=json.loads((r.parent/'product-exact-20261015/REPAIR67_ABI.json').read_text())
expected=[]
for reg in range(4):
    for wire in abi['original4b']['registers'][str(reg)]:expected.append(('q' if wire['kind']=='qubit' else 'b')+str(wire['id']))
assert [v['physical'] for v in report['input_ports']]==expected and len(expected)==1024
rows=[line.split()[1:] for line in (r/'packets/audit.tsv').read_text().splitlines() if line.strip()][:64]
assert len(rows)==32 and all(len(row)==6 for row in rows)
input_words=struct.unpack('<1024Q',(p/'audit-input-u64le.bin').read_bytes())
for reg in range(4):
    for bit in range(256):
        expected_word=sum(((int(row[reg],16)>>bit)&1)<<lane for lane,row in enumerate(rows))
        assert input_words[reg*256+bit]==expected_word,(reg,bit)
# Separate Python bit-vector interpreter, reading every actual node/edge.
raw=(p/'public-discrepancy-guard.bin').read_bytes()
assert sha(raw)=='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
assert raw[:8]==b'MRMASK01';n,ni,no=struct.unpack_from('<QQQ',raw,8)
assert (n,ni,no)==(1831784,1024,1) and len(raw)==32+n*16+4
values=array('Q',[0])*n;mask=(1<<64)-1
for i,(kind,a,b,aux) in enumerate(struct.iter_unpack('<IIII',memoryview(raw)[32:32+n*16])):
    assert aux==0
    if kind==0:values[i]=0
    elif kind==1:values[i]=mask
    elif kind==2:assert a<ni;values[i]=input_words[a]
    else:
        assert kind in [3,4,5] and a<i and b<i
        values[i]=(values[a]^values[b]) if kind==3 else (values[a]&values[b]) if kind==4 else (values[a]|values[b])
root=struct.unpack_from('<I',raw,32+n*16)[0];assert root==report['compiled_roots'][0] and root<n
discrepancy=struct.unpack('<Q',(p/'audit-discrepancy-u64le.bin').read_bytes())[0]
safe=struct.unpack('<Q',(p/'audit-safe-u64le.bin').read_bytes())[0]
assert values[root]==discrepancy and safe==(discrepancy^mask) and safe&((1<<32)-1)==(1<<32)-1
out={'status':'INDEPENDENT_SOURCE_BINDINGS_PORTS_FROZEN_KERNELS_ALL29_METADATA_AND_BINARY_GUARD_REVIEW_PASS',
 'guard_sha256':sha(raw),'guard_nodes':n,'public_ports':1024,'audit_inputs':32,'audit_safe_inputs':32,
 'all29_no_zero_entry_assumptions':True,'all29_independent_internal_MR_and_shared_entry_namespace':True,
 'live_classical_kills_reviewed_for_empty_scope_and_unconditional_overwrite':True,
 'conditional_induction_reviewed':True,'combined_dependency_must_be_olddep_OR_discrepancy':True,
 'not_a_new_arithmetic_correctness_or_phase_proof':True,'coverage_cost_and_composite_manifest_still_required':True,
 'no_runtime_search_authority_issued':True}
(p/'ROOT_INDEPENDENT_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
