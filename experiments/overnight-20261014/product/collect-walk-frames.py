"""Freeze diagnostic frame proofs and first exact model deviations."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent
raw=root/'research-output/overnight-20261014/product/walk-replay'
assert int((raw/'run.exit').read_text())==0
log=(raw/'run.log').read_text()
assert 'PRODUCT_WALK_TOTAL' in log and 'test result: ok. 2 passed' in log
assert log.count('PRODUCT_WALK_FINAL_GUARD ')==10
model=json.loads((out/'walk-frames-analysis.json').read_text())
receipt=dict(status='COMPLETED_SOURCE_BOUND_DIAGNOSTIC',qualified_score=None,exit=0,
 native_sha256=(raw/'native.sha256').read_text().split()[0],source_attestation=(raw/'source.sha256').read_text(),input_attestation=(raw/'input.sha256').read_text(),
 replayed_points_per_source=271,exported_cases_per_source=16,exported_frames=model['frames'],modeled_tick_pairs=model['modeled_tick_pairs'],
 mapping='Exact copied unchanged Y33 sweep entire final raw operation-vector equality, both metadata hash domains, event prefix map and logical pending-wire reconstruction; full complete C5/B3 streams byte-identical to original with all binding assertions intact.',
 native_tests=2,archive_guards='Every final raw coordinate and phase equal prior independent continuous transcript replay on all271 points for each source.',
 phase_scope='Finalized raw global transcript aligned within each source/batch; cross-source measurement order not asserted; no intermediate phase-fault interpretation.',
 model='Independent Python unlimited integer and modp tick map using actual incoming rails/payload/letter; exported known15 plus independent94 only. No sampled controls or width changes.',
 artifact_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in raw.iterdir()if p.is_file()},
 failed_preparation='Initial script matched non-production Walk declarations and asserted before any build/launch; source preserved prepare-walk-frames-failed-v1.py. Correction scopes exact divide_dbg/multiply function entries. Not a mathematical or native counterexample.')
(out/'walk-frames-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
for kind in ['c5','b3']:
 for name in ['receipt.json','candidate.patch']:
  (out/(kind+'-walk-frames-'+name)).write_bytes((root/'research-output/overnight-20261014/product'/(kind+'-walk-frames')/'receipt'/name).read_bytes())
md='''# Source-bound walk tick localization

The read-only C5 and B3 observers retain all source binding assertions and reproduce their complete original streams exactly. Native replay validates the full copied Y33 cleanup transformation and both hash domains, remaps exact operation events and reconstructs pending logical targets. Two independent frame/overlay fault tests pass. All271 points per source end with exactly the archived raw coordinates and phase using the same continuous within-source measurement transcript. There are 1367 frame events per source; raw words are exported for the fifteen known failing points and independent point94.

An independent Python model checks 21792 observed tick pairs using unlimited signed integers and modular arithmetic. It takes each tick's actual incoming values and actual immutable tape bits. The primary source contract is `T <- (T + (-1)^s B)/2 mod p` forward, its inverse `T <- 2T - (-1)^s B`, and the barrel exponent `k1 + 2k2`. Rails use the corresponding exact integer divisions and signed observed widths. This diagnoses a first tick deviation; it does not yet identify the internal carry or prove the intended sign/choice rule globally.

- Point249: both C5 and B3 first deviate in the multiply's forward rail tick109, before any multiply payload is applied. Tape `00001` gives exact target `90838982128839835`; actual target is `-53276205947016037`, a difference of `-2^57`. The source rail is unchanged and all model divisions are exact. The correct target fits the final sixty-bit width, so intermediate width cuts or add/shift overflow require inspection. Both division and square boundary contracts previously pass on this point.
- Point8033: C5 has no observed tick deviation and passes the complete point contracts. B3's first deviation is the division's fused payload tick75 with tape `11001`. The actual target differs from the exact modular map by `+2^51`, while its source payload is preserved. This directly precedes the B3-only wrong slope.
- Independent point94: both sources first deviate in division fused payload tick104, difference `+2^50`, with source preserved.
- Separate failed endpoint premises occur in the multiply for points6376 and7640: actual rail pairs are `(-1,-5)` and `(1,7)`, respectively, in both sources. The production endpoint assumes each rail is `+1` or `-1`.

Complete counterexamples and first-deviation tables are in `walk-frames-analysis.json`; native/source/input attestations and artifact hashes are in `walk-frames-receipt.json`, with exact permitted observer patches and protected-file checks in the C5/B3 observer receipts. Binary SHA256 `400130949d3b4605ffeccbcc098fb6c485df67c7767c1d6d084217edcf45e93f`.

All findings are finite source-bound diagnostics. The model currently checks entire ticks against their real incoming states; subsequent deviations may propagate an earlier failure. A final endpoint test distinguishes convergence from payload arithmetic. Phase is aligned only within each finalized raw source transcript, and intermediate phase may include deferred correction. No resource score, repair or full arithmetic correctness is claimed. No nonce, scorer, simulator or harness change.

Preparation failure is preserved: the first observer script asserted because its textual match also found helper/test Walk declarations. The corrected script restricts instrumentation to the two production functions. No failing build or arithmetic result was produced by that preparation attempt.
'''
(out/'walk-frames-results.md').write_text(md,encoding='utf-8',newline='\n')
