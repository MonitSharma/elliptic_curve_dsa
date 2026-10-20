import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'run-v2.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();(r/'y15-tests-v2.rs').write_bytes(raw)
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'  basis(&mut c,&features,&held,false);',b'  basis(&mut c,&features,&held,false);marks.push(c.op_count());')
change(b'sim.apply_iter(ops[marks[0]..marks[1]].iter());assert_eq!(sim.phase,0,"erase batch{batch}");',b'''sim.apply_iter(ops[marks[0]..marks[1]].iter());
   let expected:Vec<u64>=include_str!("core_loan_transformed.dat").split_whitespace().map(|s|s.parse().unwrap()).collect();
   for(i,q)in held.iter().enumerate(){assert_eq!(sim.qubits[q.0 as usize],expected[i*256+batch]&(if guarded{guard_word}else{u64::MAX}),"transformed helper{i} batch{batch} guarded{guarded}");}
   sim.apply_iter(ops[marks[1]..marks[2]].iter());assert_eq!(sim.phase,0,"erase batch{batch}");''')
change(b'sim.apply_iter(ops[marks[1]..].iter());assert_eq!(sim.phase,0,"roundtrip',b'sim.apply_iter(ops[marks[2]..].iter());assert_eq!(sim.phase,0,"roundtrip')
p.write_bytes(raw);(t/'src/point_add/core_loan_transformed.dat').write_bytes((r/'transformed.dat').read_bytes())
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['fixture_change']='Diagnostic only: check all31 transformed helper functions before any HMR against independent truth table. Preserve failed erasure/reconstruction v2.'
(r/'SOURCE_FREEZE-v3.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v3.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
