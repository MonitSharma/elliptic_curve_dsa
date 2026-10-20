from pathlib import Path
from datetime import datetime, timezone
import shutil
root=Path(__file__).resolve().parents[2]
old=root/'experiments/breakthrough-stackv3-width-plan7-20261020'
r=root/'experiments/breakthrough-stackv3-width-plan7-range-20261020'
r.mkdir(exist_ok=False)
for p in ['.gitattributes','.gitignore','run.py','additional-tests.rs']:
 shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text()
needle='if !rev&&t==130&&std::env::var'
assert s.count(needle)==1
s=s.replace(needle,'if !rev&&(130..137).contains(&t)&&std::env::var')
s=s.replace("'supported_forward_drop130':3", "'supported_forward_drop_range':[130,137,3]")
(r/'prepare.py').write_text(s)
(r/'PLAN.md').write_text('''# Extend the exact seven-wire plan across the forward loan interval

Previous frozen plan7 source passes all four native arithmetic, phase, width,
admission and fault controls. Lower1233 construction passes130, then stops at131
with the same fold deficit21 and supported shedding20;1232 stops127. Preserve
those failures. The next fixed probe requests three dropped carries on130..137
instead of130 alone, only when cap<1234. The existing exact ladder and explicit
50-bit/budget7 admission are unchanged. Unsupported widths, live-parent and
adjacent-drop conditions retain all original assertions. This is a circuit
construction choice, before fresh simulation inputs. No window/cut change.

Repeat four native controls, reproduce fullpublic714c, then the same fixed
raw1234/t21,1234/t28,1233/t28,1232/t28 cases. Stronger28-bit witness for candidates.
No final gate, nonce, benchmark or scored result. Do not inferQ from budget.
''')
p=root/'experiments/autorun-20261020-breakthrough/LOG.md'
with p.open('ab')as out:out.write(('\n'+datetime.now(timezone.utc).isoformat()+' plan7 passes native4 and moves1233 failure130->131; predeclare unchanged exactplan7 drop3 overforward130..137, old guards retained, same fullpublic control and rawcases; no gate/nonce/score.\n').encode())
print(r)
