"""Stage an additive handoff; leave unrelated working-tree documentation intact."""
import difflib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments'
for name in ['product-classical-factors-wide-20261019','product-classical-twelve-native-20261019','product-classical-twelve-proof-20261019','product-classical-nine-operational-20261019','classical9-final-20261019']:
    assert json.loads((e/name/'LOCAL-VERIFICATION.json').read_text())['status']=='ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED'
block='''## 19 October,21:35: further exact factors natively reproduced and proved

No new scored Q×T record. Official API refresh21:18 still gives9dc3798c,
Q1234/T761096/product939192464. The sole classical9 gate remains unchanged:
262144 batches/source, label pareto-parent4-classical9-gate-20261019-v1.
Its public-parent side finished16777216 shots in2447.66s; candidate child
1493271 is now running under1377884/1377879. At21:33 it was live after6m.
Do not restart/relabel/rejudge it. Filter waiter1401461 still waits for its
verdict; no new-source nonce or official benchmark exists.

An independent512-bit truth-table screen passed seven controls, including
high-row/cofactor/complement/9-variable tests. At cap7 it reproduces the frozen
simple8 output exactly. At predetermined cap9 after classical9 it finds three
additional static CCX reductions. All512 raw full q/c/phase/physical-RNG
controls match, with493 fewer executed Toffolis. Preserve the compile-only
v1 inner-doc-comment failure; v2 changes that comment only and passes.

The separate classical12 prototype is fully native and frozen before the
classical9 verdict:17889635 ops,180 point-add files,17 protected unchanged,
all18 primitive/table controls pass. No cap environment variable remains.
Raw SHA3 is2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265;
compressed SHA25617c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7;
source archive4b7c6d3bcfc1ee1540d57c2a3e991281408ed90d09c192c5ce60e0fa15ce3d17.
Native1454271 exited0. Proof1490374 exited0: three source-bound identities
replay UNSAT, instrumented whole output is identical, and independent edit
parsing proves every outside op and R/Hmr event unchanged. TRANSFER.json
binds the complete earlier proof/mask chain; rejection stays disabled.

A predeclared component-only valid-point control also exited0: label
classical12-component-executed-20261019-v1,64 batches/4096 fresh shots per
source, same input/RNG. The extra mean executed saving is1.00341796875 T,
SE0.010534977, and every paired value/phase/dirty diagnostic is identical.
This is a component diagnostic, not a failure-rate gate or scored record.
GATE-PLAN.md fixed the independent classical12 label/count/source before this
pilot or the classical9 verdict. Its separate planned final gate is
pareto-parent4-classical12-gate-20261019-v1,262144 batches/source, versus the
freshly checked exact public stream. No machine-readable declaration/census
has started for12. Its own gate and runtime/cost qualification are mandatory;
never reuse9's verdict or screen a nonce early.

Operational classical9 port/control recipes are prepared but not executed.
Only qualified hash/opcount/evidence bindings may change from the reviewed
old runtime; the new control uses two threads. The queue-only finalizer is
also prepared, with actual175-file native-path/archive checks and six
corruption controls passing. Its runtime auditor is explicitly UNBOUND until
new acceptance and prefix control pass, and a complete path/gate/runtime
audit is still required. It preserves historical results even on failure.
Do not run prepare_recipe.py after runtime binding or while a watcher is live.

Next: obtain the existing9 gate's sole verdict, then let its existing waiter
finish or refuse runtime qualification. If eligible, build/accept/control the
9 operational port before consuming the spare three slots with12's planned
gate. Inspect actual load and processes first; latest preflight_v12 recognizes
all current named jobs, and the old four-worker search reserves60 slots.
Only one60-slot search may run: preserve old logs before replacing it after
the new source/runtime/cost/control gates. Do not delete old proof/runtime
paths referenced by new transfer bindings. No uploader, no score-based nonce.

Old parent4 search remains live, with its original eligible gate: at21:17 it
reported50,790,400 completed-window rows and no pass, about2712/s. Counters
remain provisional until complete terminal audit. Corrected watcher1183677
is live. No active chemistry/QOB process was changed. Preserve Q692 and all
failed/pending evidence. All new finished archives were retrieved and every
included hash verified. Keep large tapes/archives/binaries server-side with
their hashes; do not promote component numbers into README result plots.

[Wider source screen](../experiments/product-classical-factors-wide-20261019/STATUS.md) ·
[Frozen extended native source](../experiments/product-classical-twelve-native-20261019/STATUS.md) ·
[Extended proof and valid-point control](../experiments/product-classical-twelve-proof-20261019/STATUS.md) ·
[Prepared finalizer](../experiments/classical9-final-20261019/STATUS.md).

'''
patch=[]
for name in ['docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md']:
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8');h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;h,t=p.read_text(encoding='utf-8').split('\n',1);p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-twelve-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block.rstrip()+'\n')
for name in ['product-classical-twelve-native-20261019','product-classical-twelve-proof-20261019']:
    with (e/name/'STATUS.md').open('a',newline='\n') as f:f.write('\nFull cycle handoff: [research plan](../../docs/research-plan.md). All finished evidence archives have been verified locally; no record is claimed.\n')
print('Prepared additive completed-native/proof/component checkpoint.')
