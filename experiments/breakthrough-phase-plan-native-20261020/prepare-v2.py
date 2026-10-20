import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert(r/'run.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
old=r/'failed-cleanup-model-v1';old.mkdir(exist_ok=False)
for p in[r/'SOURCE_FREEZE.json',r/'source.patch',r/'tests.log',t/'src/point_add/phase_plan.rs',t/'src/point_add/y15_onefold.rs']:shutil.copyfile(p,old/p.name)
for p in(t/'target/release/deps').glob('build_circuit-*'):
 if p.is_file()and p.stat().st_mode&0o111:shutil.copyfile(p,old/'native-test-binary');break
p=t/'src/point_add/phase_plan.rs';raw=p.read_bytes();needle=b'let need=owned.saturating_sub(budget-kept);';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'if !last&&width-1>budget-kept{continue;} // Retained carry erasure also peaks at kept + width - 1.');p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'for budget in 8..=10{fixture(pattern,budget,false,false,None);if budget<=9';assert raw.count(needle)==1
raw=raw.replace(needle,b'for budget in 9..=10{fixture(pattern,budget,false,false,None);if budget<=9')
needle=b'for budget in[8,9]{for inverse';assert raw.count(needle)==1;raw=raw.replace(needle,b'for budget in[9,10]{for inverse')
needle=b'for(budget,&cost)in(8..=10).zip(&expected){let p=phase_plan::choose(&rows,budget).unwrap();';assert raw.count(needle)==1
raw=raw.replace(needle,b'assert!(phase_plan::choose(&rows,8).is_none());for(budget,&cost)in(9..=10).zip(&expected[1..]){let p=phase_plan::choose(&rows,budget).unwrap();');p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
import subprocess
(r/'source-v2.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']='V1 failed exact width check: cleanup storage was omitted. Preserve failure. V2 explicitly admits retained compare peak kept + width - 1; budget8 infeasible in this specified family; native tests budgets9/10 vs original9. No complete point-add result, final gate or nonce.'
(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
