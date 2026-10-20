"""Prepare exact full-state screening, without arithmetic/advisory filters."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public140-nonce-20261020'
old=ws/'product-classical-twelve-operational-20261019/tool'
candidate=ws/'breakthrough-public140-finished-20261020/candidate'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((ws/'breakthrough-public140-final-gate-20261020/GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS'
assert sha(candidate/'ops.bin')=='a85c3ffa0ec725b04900ac79d5729dab126a870d566533f53d0f256c0d90cf98'
tool=r/'tool';assert not tool.exists();(tool/'src').mkdir(parents=True)
shutil.copy2(old/'Cargo.toml',tool/'Cargo.toml');shutil.copy2(old/'Cargo.lock',tool/'Cargo.lock')
for f in ['official.rs','fast_curve_c.rs','fast_sim_wide.rs','simd_screen_ffi_wide.rs']:
 shutil.copy2(old/'src'/f,tool/'src'/f)
prefix=(old/'src/main.rs').read_text().split('include!("official.rs");')[0]
prefix+='\ninclude!("official.rs");\ninclude!("fast_curve_c.rs");\ninclude!("fast_sim_wide.rs");\ninclude!("simd_screen_ffi_wide.rs");\ninclude!("screen.rs");\n'
(tool/'src/main.rs').write_text(prefix)
body=(old/'src/baseline_body.rs').read_text()
body=body.replace('model:&RailAdvisory','_model:&()')
body=body.replace('let mut selected=0;let mut i=0;let mut hit=false;while packet.ensure(i,curve){if rail_suspect_many(model,&packet.batches[i]){selected=i;hit=true;break;}i+=1;}', 'let selected=0;let hit=false;assert!(packet.ensure(0,curve));')
body=body.replace('let model=RailAdvisory::new(&a[6]);','let model=();')
body=body.replace('fn baseline_main()', 'fn main()')
body=body.replace('let p=Compact::compile(&ops[..n-TAIL]);let curve=FastCurveC::new(20);', 'let p=Compact::compile(&ops[..n-TAIL]);let curve=FastCurveC::new(20);if std::env::var_os("QUALIFY").is_some(){qualify(&ops,&p,&base,&hash,&tail,&curve,&regs,nq as usize,nb as usize);return;}')
body+='\n'+(r/'qualification.rs').read_text()
(tool/'src/screen.rs').write_text(body)
files={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*')if p.is_file()}
libs={p:sha(Path(p))for p in ['/home/hclau/ecdsa_research/prefilter-20261015/libsimd8wide.so','/home/hclau/ecdsa_research/shake8-20261015/libshake8.so','/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so']}
(r/'SEARCH-DECLARATION.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'candidate_sha256':sha(candidate/'ops.bin'),'gate_sha256':sha(ws/'breakthrough-public140-final-gate-20261020/GATE-RESULT.json'),'tool_source_files':files,'libraries':libs,'policy':'Ascending from 1; lowest passing nonce, never select by Toffolis. Exact full-state rejection only; no arithmetic filters. Eight nonce partial-packet controls 1..8 precede production and are disclosed separately. Production may overrun within a 64-nonce window; all rows retained.','qualification':'Full qubit/classical/phase/RNG state at packet batches 0,70,140 for nonces1..8, protected scalar curve reference on each live shot in those batches, exact seed and RNG bytes. Toy partial-batch masks checked independently. Final passing packet additionally protected full run_tests and unchanged benchmark.','arithmetic_change':'None; only identity tail nonce is changed after frozen passing gate.'},indent=2)+'\n')
