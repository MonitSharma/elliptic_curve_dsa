"""Save only this checkpoint in the index; preserve pre-existing doc edits."""
import difflib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
record=json.loads((r/'PUBLIC-RECORD.json').read_text())
assert record['leader']['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af'
block='''## 19 October, 18:20: qualified search continues; arithmetic reader work next

Parent4 remains frozen with its original passing32768-batch gate and complete
universal transfer/filter qualification. Ascending search PID602346 is active
on four14-thread workers; at18:12 it reported20,602,880 complete-window nonce
rows and no pass (live counters, not the terminal JSONL audit). Sustained rate
is about2697/s, giving an uncertain20-hour expected wait rather than the earlier
13-hour pilot extrapolation. Queue-only audit/native benchmark watcher610395
waits for a complete lowest-prefix pass. No uploader is running.

Completed exact scheduling, conditional-support and mapped-measurement methods
all remain Q1234. Stronger supports prove258,577 conditional cleanups but do
not lower the peak. Guard-cofactor pruning removes103 inactive Toffolis and
zero executing Toffolis; it gives no product benefit. Full appropriate
protected transcript controls pass. These are negative diagnostics, not new
records; source, tests, logs, hashes and archived evidence are preserved.

Next: exact carry borrowing with decoded read-only operand queries. Compact
MAJ encodings give free linear readers for two operands. Six independent
decoder truth-table controls pass locally; a source structural scan and full
capsule phase controls are next. Use a conservative600-T whole-program budget
for one qubit; never count a component as a full Q×T result. No new gate or
nonce search has run for these new arithmetic ideas. Failed past gates stand.

[Active search](../experiments/parent4-operational-sat-20261019/STATUS.md) ·
[Completed research index](../experiments/autonomous-20261019/LOG.md) ·
[Next arithmetic experiment](../experiments/product-carry-readers-20261019/STATUS.md).

'''
patch=[]
for name in ('docs/research-plan.md','docs/AGENT_HANDOFF.md','docs/results-status.md'):
    old=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8')
    head,tail=old.split('\n',1);new=head+'\n\n'+block+tail.lstrip('\n')
    patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    p=root/name;working=p.read_text(encoding='utf-8');h,t=working.split('\n',1)
    p.write_text(h+'\n\n'+block+t.lstrip('\n'),encoding='utf-8',newline='\n')
(r/'checkpoint-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
print('Prepared scoped handoff patch; public snapshot at',record['at_utc'])
