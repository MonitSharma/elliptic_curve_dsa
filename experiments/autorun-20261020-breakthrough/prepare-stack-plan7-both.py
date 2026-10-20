from pathlib import Path
from datetime import datetime,timezone
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-width-plan7-range-20261020';r=root/'experiments/breakthrough-stackv3-width-plan7-both-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','run.py','additional-tests.rs']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();needle='if !rev&&(130..137).contains(&t)&&std::env::var';assert s.count(needle)==1;s=s.replace(needle,'if ((!rev&&(130..137).contains(&t))||(rev&&(124..127).contains(&t)))&&std::env::var');s=s.replace("'supported_forward_drop_range':[130,137,3]", "'supported_drop_ranges':{'forward':[130,137,3],'reverse':[124,127,3]}")
(r/'prepare.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact seven-wire ladder at both admission cliffs

Previous fixedforward130..137 source passes native4, fullpublic714c and all
forward construction at1233. Its next original guard stops reverse126: fold
short21 vs supported16+2+2=20. Preserve that failure and1232forward127 failure.

Predeclaredrop3 onforward130..137 and reverse124..127 onlylowerbudget; retain
loan128, stronger28-bit witness, same explicit50bit/budget7 admission, unchanged
exact ladder and all original unsupported-case/live-parent/cap assertions.
Repeat native4 and fullpublic714c before same rawgrid. No new approximation,
no final gate/nonce/benchmark/score. Actual physicalQ needs protected measurement.
''')
with(root/'experiments/autorun-20261020-breakthrough/LOG.md').open('ab')as out:out.write(('\n'+datetime.now(timezone.utc).isoformat()+' plan7range native4/public714c PASS;1233 forwards fit thenoriginalrev126guard stops21vs20,1232 stopsfwd127. Predeclare sameexactplan7/drop3 reverse124..127 plusforward130..137 onlylowerbudget; no gate/nonce/score.\n').encode())
print(r)
