"""Freeze internal producer/borrow evidence with unchanged stream provenance."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];folder=Path(__file__).parent;raw=root/'research-output/overnight-20261014/product/fold75-replay'
assert int((raw/'run.exit').read_text())==0
log=(raw/'run.log').read_text();assert 'test result: ok. 3 passed' in log and log.count('PRODUCT_FOLD_FINAL_GUARD ')==10 and 'PRODUCT_FOLD_TOTAL' in log
analysis=json.loads((folder/'fold75-analysis.json').read_text());cert=json.loads((folder/'fold75-borrow-certificate.json').read_text())
assert len(analysis['proofs'])==64 and all(r['producer_exact']and r['source_preserved_all']for r in analysis['proofs'])
doc=dict(status='COMPLETED_SOURCE_BOUND_FINITE_DIAGNOSTIC',qualified_score=None,exit=0,native_tests=3,
 native_sha256=(raw/'native.sha256').read_text().split()[0],source_attestation=(raw/'source.sha256').read_text(),input_attestation=(raw/'input.sha256').read_text(),
 full_points_replayed_per_source=271,exported_cases_per_source=16,folds_per_case=2,producer_cases=64,all_unfolded_integer_producers_exact=True,
 binding='Both source observers retain all binding assertions and original whole-circuit/raw stream byteidentity; exact copied Y33 transform and both emission/final hash domains; final raw coordinates and phase on all271/source equal archived global transcript replay.',
 producer_frame='Source actual open ripple linear sums, real three overflow E sums, source complement and restored carries; independent fault test detects corrupted carry.',
 resource='Dedicated targets,16GiB virtual cap,4 buildthreads/1 native runtime; original streams and all protected files untouched.',
 phase_scope='Final raw within-source transcript exact; cross-source transcripts unaligned. No intermediate phase cause claim.',
 findings='B3 point8033 tick75 width56 misses borrow into bit56; C5 width57 handles same producer. Independent94 tick104 both width56 miss borrow. All64 observed transforms agree exactly modulo their actual source windows.',
 correction='Earlier message assumed both tick75 windows56; primary source and native evidence corrected C5 to57 before reporting cause.',
 artifact_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in raw.iterdir()if p.is_file()})
(folder/'fold75-receipt.json').write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
for kind in ['c5','b3']:
 for name in ['receipt.json','candidate.patch']:(folder/(kind+'-fold75-'+name)).write_bytes((root/'research-output/overnight-20261014/product'/(kind+'-fold75')/'receipt'/name).read_bytes())
md='''# Actual producer and missing fold borrow

All64 reconstructed add2 producers match exact unlimited-integer sums, including their real three overflow bits, and preserve the source word. Native replay passes three frame/mutation tests and verifies exact original complete circuit/raw byteidentity, all source binding assertions, the copied entire Y33 operation transformation and both prefix hash domains. All271 points per source retain the separately archived final coordinates and phase under the continuous finalized-raw transcript.

The B3-only point8033 first becomes wrong in forward fold75, after a correct producer. Its exact low56 input is `0xba0290bfe`; the correct fold correction is `-73014460621`, giving a low sum of `-23082775759`. The lower56 output is exact modulo2^56, but the borrow into the high word is omitted. The resulting stored word is too large by2^56, and the five-bit final rotation produces the observed2^51 slope error. Closing the open ripple preserves the error.

C5 uses a57-bit forward window through tick99. B3 uses57 only through tick55, then56. Thus C5 fold75 handles the same exact producer correctly. An earlier direct message assumed both windows56; this was corrected from primary source before this report. The difference is window admission, not a carry-constructor/loan error.

Independent point94 first fails at forward fold104, where both sources use56 bits. Its input low word `0x22845abac1` plus correction `-227633318413` is negative. Both omit the same borrow, producing2^56 error before the six-bit rotation, hence2^50 afterward. Every one of64 sampled transformations matches exactly the arithmetic modulo its actual source window while retaining the original high word.

These certificates identify finite whole-body counterexamples while the fold's lower-window component contract remains satisfied. A larger fixed window alone cannot guarantee exact arithmetic for every possible input. Any exact carry/borrow propagation repair needs a separate reversible value, phase, allocator and full source-binding proof. No repair, full benchmark score or resource improvement is claimed.

Files `fold75-analysis.json`, `fold75-borrow-certificate.json` and `fold75-receipt.json` retain all arithmetic words and source/native/input/artifact hashes. The two exact permitted observer patches and protected-file checks are preserved separately. Raw source-bound logs and emitted frames remain under the isolated product evidence area. Measurement phases are aligned only within each finalized raw source transcript; no cross-source or intermediate phase cause is inferred.
'''
md+='\nRuntime binary SHA256 `'+doc['native_sha256']+'`.\n'
(folder/'fold75-results.md').write_text(md,encoding='utf-8',newline='\n')
print(json.dumps({'native':doc['native_sha256'],'certificates':len(cert['certificates'])}))
