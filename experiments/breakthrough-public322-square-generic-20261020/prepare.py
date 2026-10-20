import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-public8b-repeat-final-20261020';grid=ws/'breakthrough-public322-square-grid-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert not t.exists()and(grid/'run.exit').read_text().strip()=='0';rows=json.loads((grid/'RESULT.json').read_text())['cases'];best=next(x for x in rows if x['square_cap']==1408);assert all(x['raw_sha256']==best['raw_sha256']for x in rows if x['square_cap']>=1408)
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),'63d63c90a25e204d3173d5078f5a0bf12c9d65b7'],check=True);assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'std::env::set_var("LF_SQUARE_CAP", &break_cap);';assert raw.count(a)==1;raw=raw.replace(a,b'std::env::set_var("LF_SQUARE_CAP", "1408");');a=b'    finished_pipeline::run(ops)';assert raw.count(a)==1;raw=raw.replace(a,b'    finished_square_pipeline::run(ops)');raw+=b'\nmod finished_square_pipeline;\n';p.write_bytes(raw)
runtime=f'''use crate::circuit::{{Op,OperationType,QubitId}};
use sha3::{{Digest,Sha3_256}};
const RAW_COUNT:usize={best['operations']};
const RAW_SHA3:&str="{best['records_sha3_256']}";
pub(super)const IDENTITY_NONCE:u64=0;
pub(super)fn run(ops:Vec<Op>)->Vec<Op>{{
 assert_eq!(ops.len(),RAW_COUNT,"Frozen square1408 raw operation count");let mut hash=Sha3_256::new();
 for o in &ops{{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{{hash.update(v.to_le_bytes());}}}}
 assert_eq!(format!("{{:x}}",hash.finalize()),RAW_SHA3,"Frozen square1408 raw records");
 let mut ops=super::breakthrough_generic::run(ops);assert!(IDENTITY_NONCE<(1u64<<48));
 for bit in 0..48{{let mut o=Op::empty();o.kind=OperationType::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);o.validate();ops.extend([o,o]);}}ops
}}
''';(t/'src/point_add/finished_square_pipeline.rs').write_bytes(runtime.encode());subprocess.run(['cp','-a','--reflink=auto',str(old/'candidate/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));(r/'SOURCE-FREEZE.json').write_text(json.dumps({'base':'63d63c90a25e204d3173d5078f5a0bf12c9d65b7','source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':f['protected_files'],'identity_nonce':0,'raw_grid_result_sha256':sha(grid/'RESULT.json'),'raw_grid_selected_case':best,'square_cap':1408,'global_cap':1536,'scope':'Independent frozen stageA circuit: widen only existing square workspace1234->1408, preserve arithmetic/precision/public140 schedule. Fixed best raw result ties higher budgets byte-for-byte; choose smallest cap. Apply unchanged generic exact passes once, nonce0 tail. Original source-bound modules remain untouched and unused; any new retained leases must be independently reproved before a new finished candidate gate.'},indent=2)+'\n')
