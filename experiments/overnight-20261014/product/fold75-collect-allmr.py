"""Freeze finite producer phase/value proof; no whole-point or arbitrary-prefix claim."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[3];folder=Path(__file__).parent;raw=root/'research-output/overnight-20261014/product/fold75-allmr'
assert int((raw/'run.exit').read_text())==0
log=(raw/'run.log').read_text();assert 'test result: ok. 8 passed' in log and log.count('PRODUCT_FOLD75_ALLMR_FINAL_GUARD ')==10
rows=[]
for line in log.splitlines():
 if line.startswith('FOLD75_ALLMR '):rows.append(dict(re.findall(r'(\w+)=(\S+)',line)))
assert len(rows)==20
for r in rows:assert (r['nonconstant_q'],r['target_constant'],r['phase_terms'])==('0','true','0')
contexts=sum(int(r['cases'])for r in rows);assert contexts==1084
doc=dict(status='COMPLETED_FINITE_ALL_FUTURE_MEASUREMENT_PROOF',qualified_score=None,exit=0,native_tests=8,
 native_sha256=(raw/'native.sha256').read_text().split()[0],source_attestation=(raw/'source.sha256').read_text(),input_attestation=(raw/'input.sha256').read_text(),
 exact_archived_detail_kernel_sha256='22c3beb43f55ca96d81a3ab8668913e5ad597fbfcfa2e78f99d2a3f9bc19c25c',strict_kernel_byte_prefix='330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98',
 slices=20,finite_case_contexts=contexts,rows=rows,all_final_quantum_slots_constant=True,all_incremental_phase_polynomials_zero=True,
 native_equivalence='Every symbolic output constant equals the original actual whole-prefix native state. All271 source point final coordinates/phase remain archived-identical with full original binding checks.',
 domain='For each actual saved271-point source prefix, phase at entry is additive and past measurement outcomes are fixed by its original continuous transcript. ALL internal future measurement outcomes quantified independently. No arbitrary-prefix, past-MR or whole-point ALLMR claim.',
 inference='B3point8033/t75 and independent94/t104 missing-window-borrow outputs persist for every internal measurement outcome on these fixed entry states, with zero incremental slice phase. Lower-window component contract is satisfied; whole-body arithmetic wrong.',
 preservation='Exact archived detail kernel byte-copy; strict/canonical kernels and protected source unchanged. Four original strict tests, two frame tests, independent diagnostic oracle and open-ripple fault test pass.',
 artifact_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in raw.iterdir()if p.is_file()})
(folder/'fold75-allmr-receipt.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
md='''# Fixed-entry all-measurement proof of missing borrow

Twenty exact original source slices cover forward folds75 and104 on each saved271-point prefix in C5 and B3:1084 finite entry contexts. Every future reset/HMR outcome inside each slice is an independent symbolic variable. All final quantum slots are constant, and every incremental phase polynomial is identically zero. Every constant exactly matches the original whole-prefix native state. Thus the known missing-borrow values persist independently of all measurements internal to these folds.

The before/after boundaries include the real open-ripple producer, fold and restored carry state. Exact copied Y33 transformation and both source/final prefix hash domains are required. All original whole-circuit bindings and byteidentities remain intact; all271 final raw coordinates and phase per source reproduce the archived replay.

Scope is fixed actual entry basis states. Past measurements are fixed by the preserved original continuous transcript; input phase is additive. No arbitrary prefix or whole-point all-measurement correctness is claimed. Zero incremental phase establishes these are deterministic value errors within the finite contexts, rather than changes to the fold's phase proof.

Eight native tests pass: four unchanged strict-kernel tests, two frame/mutation tests, an independent simulator polynomial/value fault oracle and the open-ripple corrupted-carry test. The exact archived detail kernel is a byte-copy, with strict original kernel and canonical shared files unchanged. No score or repair.
'''
md+='\nRuntime binary SHA256 `'+doc['native_sha256']+'`; exact slice sizes, outcome counts, source/input/artifact hashes and native equivalence in `fold75-allmr-receipt.json`.\n'
(folder/'fold75-allmr-results.md').write_text(md,encoding='utf-8',newline='\n')
print(json.dumps({'native':doc['native_sha256'],'contexts':contexts}))
