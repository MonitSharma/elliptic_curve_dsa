from pathlib import Path
from datetime import datetime,timezone
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-width-loan128-20261020';r=root/'experiments/breakthrough-stackv3-width-loan-drop130-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','run.py']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();needle='assert all(sha(t/p)==h for p,h in protected.items());prior=';assert s.count(needle)==1
insert='''p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'fn y28_drop(t: usize, rev: bool) -> usize {';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\\n    if !rev&&t==130&&std::env::var("STACK_DROP130_RESEARCH").is_ok_and(|v|v=="1"){return 2;}');p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'    if let Some((cap,top))=config{';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("STACK_DROP130_RESEARCH",if config.is_some(){"1"}else{"0"});\\n'+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in protected.items());prior='''
s=s.replace(needle,insert).replace("'restore_original_exact_forward_loan_tick128':True","'restore_original_exact_forward_loan_tick128':True,'supported_forward_drop130':2");(r/'prepare.py').write_text(s)
(r/'PLAN.md').write_text('''# Existing exact two-carry drop at forward130

Original exact carryloan128 restoration gets1233 past the128 admission cliff.
The next unchanged y16 guard is fwd130: need36, room15, deficit21; existing
allowed14+2+4 shedding covers20. Parent source already supports exact drop2
at130 under its C35_DROPS configuration; test that existing implementation at
130 only (preserve ordinary129 behavior), reducing fold need by one.

Retain exact loan128 plus supported drop130=2. No new primitive, new approximation
or guard change. First unchanged public714c control with researchflagsOFF;
fixed raw1234/t21,1234/t28,1233/t28,1232/t28 with both exact researchflagsON.
Use stronger28 witness for candidates,21 only inherited diagnostic control.
Freeze source/protected17 before generation, preserve every failure. ActualQ
and executedT require independent measurement and finished benchmark; nominal
cap and staticproxy are not records. No final gate, nonce or packet tuning.
''')
log=f'\n{datetime.now(timezone.utc).isoformat()} predeclare exactloan128+existingdrop130=2 widthprobe: loan128 passesfirstbarrier, now fwd130 deficit21 vs supported20; drop2 reducesneed1 underunchangedguard. Public714c control first,fixedraw1234t21/1234t28/1233t28/1232t28,strongwitness28,no newapprox/gate/nonce.\n';p=root/'experiments/autorun-20261020-breakthrough/LOG.md';p.write_bytes(p.read_bytes().rstrip()+log.encode());print(r)
