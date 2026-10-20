import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'primitive';f=json.loads((r/'SOURCE_FREEZE-v3.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'run-v3.exit').read_text().strip()=='101';assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();(r/'y15-tests-v3.rs').write_bytes(raw)
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b' fn run(guarded:bool,shuffle:bool,guard_word:u64,probe:Option<usize>){',b''' fn apply_part(sim:&mut Simulator<'_,Words>,ops:&[Op],guarded:bool,guard:crate::circuit::BitId){
  let mut push=Op::empty();push.kind=OperationType::PushCondition;push.c_condition=guard;
  if guarded{sim.apply_iter(std::iter::once(&push).chain(ops.iter()));}else{sim.apply_iter(ops.iter());}
 }
 fn run(guarded:bool,shuffle:bool,guard_word:u64,probe:Option<usize>){''')
for a,b in [(b'sim.apply_iter(ops[marks[0]..marks[1]].iter());',b'apply_part(&mut sim,&ops[marks[0]..marks[1]],guarded,guard);'),(b'sim.apply_iter(ops[marks[1]..marks[2]].iter());',b'apply_part(&mut sim,&ops[marks[1]..marks[2]],guarded,guard);'),(b'sim.apply_iter(ops[marks[2]..].iter());',b'apply_part(&mut sim,&ops[marks[2]..],guarded,guard);')]:change(a,b)
change(b'let mut rng=Words{bytes,pos:0};let mut sim=',b'let full_bytes=bytes.clone();let mut rng=Words{bytes,pos:0};let mut sim=')
change(b'sim.bits[guard.0 as usize]=guard_word;sim.apply_iter',b'sim.bits[guard.0 as usize]=guard_word;let initialized=sim.qubits.clone();sim.apply_iter')
change(b'drop(sim);assert_eq!(rng.pos,nd*8);',b'''let final_state=sim.qubits.clone();let final_phase=sim.phase;let final_t=sim.stats.toffoli_gates;drop(sim);assert_eq!(rng.pos,nd*8);
   let mut full_rng=Words{bytes:full_bytes,pos:0};let mut full=Simulator::new(nq as usize,nb as usize,&mut full_rng);full.qubits.copy_from_slice(&initialized);full.bits[guard.0 as usize]=guard_word;full.apply_iter(ops.iter());assert_eq!(full.qubits,final_state);assert_eq!(full.phase,final_phase);assert_eq!(full.stats.toffoli_gates,final_t);drop(full);assert_eq!(full_rng.pos,nd*8);''')
p.write_bytes(raw);f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['fixture_change']='Simulator.apply_iter creates a fresh local condition stack per call. Re-establish outer guard on every segmented observation, and verify against independent uninterrupted full execution. Mathematical certificate, emitted component and production prefix unchanged.'
(r/'SOURCE_FREEZE-v4.json').write_text(json.dumps(f,indent=2)+'\n');(r/'source-v4.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
