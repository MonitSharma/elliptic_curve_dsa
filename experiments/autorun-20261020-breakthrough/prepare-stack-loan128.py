from pathlib import Path
from datetime import datetime,timezone
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-width-20261020';r=root/'experiments/breakthrough-stackv3-width-loan128-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','run.py']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();needle='p.write_bytes(raw);assert all(sha(t/p)==h for p,h in protected.items());';assert s.count(needle)==1
injection='''p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'fn carry_loan_selected(rev:bool,t:usize)->bool {CONSUMER_LOANS && !rev && (129..137).contains(&t)}';assert raw.count(needle)==1;raw=raw.replace(needle,b'fn carry_loan_selected(rev:bool,t:usize)->bool {let first=if std::env::var("STACK_LOAN128_RESEARCH").is_ok_and(|v|v=="1"){128}else{129};CONSUMER_LOANS && !rev && (first..137).contains(&t)}');p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'    if let Some((cap,top))=config{';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("STACK_LOAN128_RESEARCH",if config.is_some(){"1"}else{"0"});\\n'+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in protected.items());'''
s=s.replace(needle,injection).replace("'modes':['public'","'restore_original_exact_forward_loan_tick128':True,'modes':['public'");(r/'prepare.py').write_text(s)
(r/'PLAN.md').write_text('''# Restore original exact carry loan at forward128

Parent public88869 retunes the original0c3 forward loan range128..137 to129..137,
claiming about0.3T saving at1234. Lower1233/1232 budgets hit the originaly16 guard
at128: raw fold short23, existing allowed shedding16+2+4 covers22. One loaned
wire may remove this admission cliff without weakening any assertion.

Restore only the original exact forward128 carry loan, using its unchanged
existing implementation. No new primitive, approximation/window/cut, or guard
change. Prior lean128 probe had no effect (the path was not eligible at128),
positive streams identical and lowerbudget failures preserved. Keep that result.

First fullpublic714c control with loanoverride OFF. Fixed raw cases1234/t21,
1234/t28,1233/t28,1232/t28 with loan128 ON. Stronger28-bit square witness is the
candidate precision;21 is an inherited diagnostic control. Freeze before native
generation; measure actual physicalQ and completeT only later, never inferQ
from budget. No final gate, nonce search, benchmark or scored record here.
''')
log=f'\n{datetime.now(timezone.utc).isoformat()} predeclare stackv3 original exact forwardcarryloan128 restoration; unchangedy16 guard rawdeficit23 vs shedcapacity22, one extra loanmayfit1233. Fixedpublic714c control andraw1234t21/1234t28/1233t28/1232t28, strengthenwitness28, preservelean128 noeffectfailure, no finalgate/nonce/score.\n';p=root/'experiments/autorun-20261020-breakthrough/LOG.md';p.write_bytes(p.read_bytes().rstrip()+log.encode());print(r)
