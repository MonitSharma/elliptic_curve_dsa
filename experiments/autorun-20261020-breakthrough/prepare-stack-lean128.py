from pathlib import Path
from datetime import datetime,timezone
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-width-20261020';r=root/'experiments/breakthrough-stackv3-width-lean128-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','run.py']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();needle='p.write_bytes(raw);assert all(sha(t/p)==h for p,h in protected.items());';assert s.count(needle)==1
injection='''p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'fn lean_on(t: usize) -> bool {';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\\n    if t==128&&std::env::var("STACK_LEAN128_RESEARCH").is_ok_and(|v|v=="1"){return true;}');p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'    if let Some((cap,top))=config{';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("STACK_LEAN128_RESEARCH",if config.is_some(){"1"}else{"0"});\\n'+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in protected.items());'''
s=s.replace(needle,injection).replace("'modes':['public'","'fixed_lean_tick128':True,'modes':['public'");(r/'prepare.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact no-copy alternative at tick128

Prior raw1233/1232 budgets stop the unchanged y16 workspace guard at fwd128
(room16 need39, erase room21 need35). Test the source's existing exact lean
no-copy construction at tick128, in both directions where lean_on is queried.
No guard is weakened, no new arithmetic primitive/check truncation/census cut
is introduced. Source documents lean versus copy equivalence and unchanged
seeded compares. Retain all original public precision at21-bit control and use
the documented stronger28-bit witness for lower-width candidates.

Full public control must still exactly reproduce714c4e4c before raw research.
Fixed same cases1234/t21,1234/t28,1233/t28,1232/t28, with tick128 lean enabled
for raw cases only. Other switches/row schedules stay as public88869. Freeze
source/protected17 before generation; preserve every construction failure.
PhysicalQ and complete executedT remain unverified until full final source,
new declared gate versus current product parent, qualified nonce and unchanged
benchmark. Raw results are diagnostics only; do not place them in result plots.
''')
log=f'\n{datetime.now(timezone.utc).isoformat()} predeclare stackv3 exact lean128 native width probe: previous1233/1232 y16 room cliff, use existing no-copy path on128 with originalassertions, public714c control first, fixed1234/t21,1234/t28,1233/t28,1232/t28; no weakercheck, no finalgate/nonce/score.\n';p=root/'experiments/autorun-20261020-breakthrough/LOG.md';p.write_bytes(p.read_bytes().rstrip()+log.encode());print(r)
