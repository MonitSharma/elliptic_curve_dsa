"""Stage only this cycle's root-doc prefix; preserve unrelated working edits."""
import difflib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
block='''## 19 October, 18:50: carry/AND screens complete; frozen search continues

This goal turn made progress through three completed, preserved exact source
experiments. No new Q×T record is verified. Parent4 stays frozen, with its
original passing32768-batch gate and complete transfer/filter qualification.
At18:49 the live four-worker search reported26,595,328 completed-window rows,
no pass, about2703/s. These are provisional counters, not the final prefix
audit. Search602346 and queue-only final watcher610395 remain live. The
rate-based expected wait remains about20h and is not an ETA. No uploader runs.

Carry readers: five full capsule controls pass after the six decoder controls.
279,356 cells are structurally eligible,19 use operand readers. The source-bound
strong allocator reproduces its previous complete output exactly and records
3112 full-width regions. The declared disjoint cover leaves839 uncovered;
there is no full-width candidate. Seven cover controls reject partial peaks
and stop the tentative saving window at the original measurement.

Exact dirty-output AND absorption:511 patterns, zero extra executed Toffolis,
Q1234. Six local controls, five RNG-subsequence controls and512 full protected
raw-input integration shots pass. This is retained-outcome coupling, not an
ordinary statistical gate or benchmark. Combining with carry borrowing leaves
758 of3031 strong-support peak regions uncovered. Generalizing to independent
intervening operations admits no additional cells and emits the exact same
complete stream; ten local controls and512 full integration shots pass. Its
compile-only v1 failure is preserved separately, followed by passing v2.

All three archives were retrieved and every included hash verified:51,63 and46
files. Large tapes stay server-side with hashes. Public API refresh in the AND
experiment confirms9dc3798c/Q1234/T761096/product939192464. No new gate, nonce
screen or native candidate was created for these arithmetic screens. Do not
repeat them or resample any past gate. Q692 and all failed evidence stay intact.

Next useful front: implement the declared materialized-guard scheduler in
product-guard-schedule-20261019. Preserve captured guards with immutable fresh
classical bits/atomic classical macros; remove former Push/Pop scheduling fences
only through exact read/write dependencies. Keep the entire R/Hmr RNG chain.
Start with nested/mutated/direct/inactive-guard controls before source screening.
No implementation or job exists there yet. Other active research from this
cycle is only the frozen parent4 search and its final watcher. Check actual
resources before another one-build/one-core job; do not touch chemistry.

[Carry evidence](../experiments/product-carry-readers-20261019/STATUS.md) ·
[AND evidence](../experiments/product-and-target-20261019/STATUS.md) ·
[Generalized screen](../experiments/product-and-target-loose-20261019/STATUS.md) ·
[Next scheduling declaration](../experiments/product-guard-schedule-20261019/STATUS.md).

'''
patch=[]
for name in ('docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'):
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8')
    h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;working=p.read_text(encoding='utf-8');h,t=working.split('\n',1)
    p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-arithmetic-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:
    f.write('\n\n'+block)
    f.write('Archive SHA256: carry19382a37eab84a064911c4977c2f08e969fa56322853735d924cc6c3ec036a40; AND8e9fae83873391fe43de2c50bf2d4b0ab2d0393e7c37683837e31f3d04f4a174; loose3f4a12117dbe5e75d34ab9982a530aedeee91177c927c0f94ef4a500dbc340eb.\n')
print('Prepared this cycle handoff prefix and appended research log.')
