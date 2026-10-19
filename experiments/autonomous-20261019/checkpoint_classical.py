"""Preserve unrelated working edits; stage only an additive research prefix."""
import difflib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1];e=root/'experiments'
names=['product-guard-mrfree-20261019','product-two-target-20261019','product-branch-alias-20261019','product-classical-factors-refresh-20261019','product-captured-factors-20261019','product-captured-factors-native-20261019','product-classical-factors-native-20261019','product-factor-cost-proof-20261019','product-classical-type-probe-20261019','product-classical-control-expression-20261019','product-classical-nine-proof-20261019','product-classical-nine-20261019']
for name in names:
    p=e/name;assert json.loads((p/'LOCAL-VERIFICATION.json').read_text())['status']=='ARCHIVE_AND_ALL_INCLUDED_HASHES_VERIFIED'
    (p/'STATUS.md').write_text((p/'evidence/STATUS.md').read_text(),newline='\n')
n=e/'product-classical-nine-20261019';decl=json.loads((n/'evidence/qualification/DECLARATION.json').read_text());native=json.loads((n/'evidence/NATIVE-RECEIPT.json').read_text())
assert decl['label']=='pareto-parent4-classical9-gate-20261019-v1' and decl['batch_count']==262144
with (n/'STATUS.md').open('a',newline='\n') as f:f.write('''
## Live qualification checkpoint,19 October20:46 SGT

Native run1336448 exited0;175 source files and17 protected files checked.
Full raw SHA3 is4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f;
compressed SHA25676271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1.
The one final gate was declared at12:46:11 UTC with label
pareto-parent4-classical9-gate-20261019-v1,262144 batches/16777216 shots per
source, versus exact refreshed public9dc3798c stream. Manager1377879 runs
run-gate-v2.sh, two compute threads, streams sequentially, three reserved slots.
Consult gate-v2.exit and qualification/RESULT.json for the authoritative state.
Never restart this declared census or change its label/count/source.

The preceding shell launch1374176 died on CRLF before any declaration,
qualification directory or census shot existed. Its script/log/PID and the
zero-shot GATE-ADMISSION-FAILURE.json are preserved. This is a launcher repair,
not a rerun of a declared gate. The source and inherited nonce are unchanged.
No identity-tail nonce has been screened on this source and no official
benchmark has run. The pre-gate evidence archive intentionally excludes live
census rows; preserve final gate evidence separately when it is terminal.
''')
block='''## 19 October,20:49: native exact classical reductions; one fresh gate running

No new Q×T benchmark record is verified. Public API refresh at20:46 confirms
9dc3798c/Q1234/T761096/product939192464. Preserve Q692 and all old verdicts.

The new isolated parent4-plus-nine candidate is natively byte-identical to
its research stream:17889627 ops,175 point-add source files,17 protected files
unchanged. Raw SHA3 is4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f;
compressed SHA25676271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1.
Source archive SHA2562932b6cf662e2d6be05679b0d5e34a9149ccbceaca57f8ce92cfccd13b8c8f6e.
Eight exact classical factors add no qubits/bits/MR; the ninth replaces one
unconditional Toffoli controlled by q706=bit773 XOR bit774 with two conditioned
CNOTs. Its512 protected full-state/phase/classical/RNG shots save exactly1 T
per shot beyond simple8. Eight independent factor SAT identities and the ninth
dirty-target XOR identity replay UNSAT. Full-stream edit audit proves every
other op and every R/Hmr event unchanged. TRANSFER.json binds the18 old accepted
runtime artifacts. This is source/proof evidence, not runtime acceptance.

The sole final gate was declared20:46:11 SGT: label
pareto-parent4-classical9-gate-20261019-v1,262144 batches/16777216 shots per
source, same fresh inputs versus the exact current public stream. Manager
1377879, run-gate-v2.sh, sequential two-thread streams, three reserved slots.
Consult gate-v2.exit and qualification/RESULT.json. Its verdict is final;
never restart/relabel/extend it. The prior shell1374176 failed on CRLF before
any declaration/directory/shot; preserve its zero-shot admission receipt.
No new-source nonce screen or official benchmark exists. If this gate passes,
qualify a fresh source-bound disabled filter and own-seed/full9024 state/RNG
controls before porting the reviewed operational runtime. Never reuse old
prefix rows for the new source. Keep queue mode and lowest ascending pass.

Completed negatives: exact guard scheduling leavesQ1234 after512 physical-RNG
controls; relaxing only global MR-order fences leavesQ1234 in both fixedcases,
with512 mapped-event transcripts each. Two-target CCX fusion has zero eligible
pairs in six declared public/ordered/gap cases. Strong branch-support aliasing
cannot cover the first full-width state: all1234 supports are unconditional.
Captured-factor16 is natively reproduced but its eight extras have universally
false guards; its executed cost equals simple8, so it is not an alternative
nonce fingerprint. Preserve the compile/admission failures and all archives.

The older frozen parent4 search remains live: shell602346, workers602363,
602364,602365,602367. At20:35 it reported44,089,344 completed-window rows, no
pass, about2716/s. These counters are provisional until terminal prefix audit.
Its passing old gate is unchanged. A real stale path was found in its first
waiting finalizer: correct archive71bbeefc... was sought under obsolete
product67-native instead of product-pareto/parent4-qualification. Corrected
watcher1183677 replaces only stale waiting610395; six corruption controls and
all-input path/archive/gate/18-runtime-hash checks pass. Source-bound snapshot
and SWITCH.json are preserved. Actual final native/benchmark waits for a
certifiable lowest pass; the path audit is not a scored result.

All completed experiment archives in this cycle were retrieved and every
included hash verified locally. Large frozen source archives, binary tapes and
native executables stay server-side with hashes and reconstructable patches.
Do not repeat these source queries or resample old failed gates. Current own
budget is60 old-search slots plus3 new-gate slots, leaving one research slot.
Use latest preflight_v8.py; inspect actual processes before launching anything.
Never touch chemistry/QOB. Stage only this cycle's research and additive docs.

[Nine-reduction candidate](../experiments/product-classical-nine-20261019/STATUS.md) ·
[Universal proof](../experiments/product-classical-nine-proof-20261019/STATUS.md) ·
[Corrected finalizer](../experiments/parent4-final-sat-v2-20261019/STATUS.md).

'''
patch=[]
for name in ('docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'):
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8');h,t=old.split('\n',1);new=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;working=p.read_text(encoding='utf-8');h,t=working.split('\n',1);p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-classical-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with (r/'LOG.md').open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n'+block)
print('Prepared additive checkpoint; unrelated working edits preserved.')
