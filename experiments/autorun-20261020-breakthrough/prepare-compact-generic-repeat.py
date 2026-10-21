from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).resolve().parent;ex=a.parent;old=ex/'breakthrough-local-de8-replay-20261020/candidate/src/point_add';template=ex/'breakthrough-global-quantum-alias-v3-20261021';r=ex/'breakthrough-compact-generic-repeat-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();pa=t/'point_add';pa.mkdir()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
names=['affine_simplify','quadratic_simplify','truth_simplify','interned_witness','mabsorb','pscan','cond_pass','sqtop_pass','zero_force','classical_factors_xor','breakthrough_generic']
for n in names+['product_simplify','product7_simplify','tests_classical_factors']:shutil.copyfile(old/(n+'.rs'),pa/(n+'.rs'))
shutil.copytree(old/'classical_wide',pa/'classical_wide')
(pa/'mod.rs').write_text('\n'.join('mod '+n+';'for n in names+['classical_wide'])+'\npub fn run(ops:Vec<crate::circuit::Op>)->Vec<crate::circuit::Op>{breakthrough_generic::run(ops)}\n')
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(template/'local-tool'/n,t/n)
p=t/'Cargo.toml';p.write_text(p.read_text().replace('name = "global_quantum_alias"','name = "compact_generic_repeat"'))
s='''use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};mod io;mod point_add;
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);std::env::set_var("HEO_MABSORB","1");for k in["SL_COND","SL_SQTOP","SL_PSCAN_FIX","SL_PSCAN_FAULT","SL_COND_FAULT","SL_SQTOP_FAULT"]{std::env::remove_var(k);}let ops=io::load_ops(&a[1]);let before=ops.len();let out=point_add::run(ops);io::save_ops(&format!("{}.ops.bin",a[2]),&out);let(nq,nb,_,_)=circuit::analyze_ops(out.iter());std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&serde_json::json!({"status":"GENERIC_REAPPLICATION_DIAGNOSTIC_NOT_A_SCORE","input_operations":before,"output_operations":out.len(),"qubits":nq,"classical_bits":nb})).unwrap()+"\\n").unwrap();}
'''
(t/'discover.rs').write_text(s)
paths={'compact1233':ex/'breakthrough-compact-context-alias-20261021/cap1233-r012.ops.bin','compact1234':ex/'breakthrough-compact-context-alias-20261021/cap1234-t21.ops.bin'}
f=json.loads((template/'SOURCE-FREEZE.json').read_bytes());f.update(tool_source_files={p.relative_to(t).as_posix():sha(p)for p in t.rglob('*')if p.is_file()},input_streams={n:sha(p)for n,p in paths.items()},scope='Research-only reapplication of unchanged inherited generic source passes, including full nine-atom classical tables, to two freshly qualified compact/context/global-alias streams. All pass-native controls run before generation; sources copied and hashed. Original protected17 unchanged. No old source-bound table transported. Some generic passes intentionally change internal random bits; original-word fullstream equality is not claimed. Actual fresh curve/phase/dirty development and own frozen final statistical gate required before nonce/benchmark/submission. Diagnostic stream resource counts only.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n');(r/'PLAN.md').write_text(f['scope']+'\n');(r/'.gitignore').write_text('local-tool/\n*.ops.bin\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
s=(template/'run.py').read_text().replace(template.name,r.name).replace("target/release/global_quantum_alias'","target/release/compact_generic_repeat'")
left=s.index('for name,path in [');right=s.index(']:',left)+2
s=s[:left]+"for name,path in [('compact1233',r.parent/'breakthrough-compact-context-alias-20261021/cap1233-r012.ops.bin'),('compact1234',r.parent/'breakthrough-compact-context-alias-20261021/cap1234-t21.ops.bin')]:"+s[right:]
s=s.replace('8*1024**3','6*1024**3').replace("'native_controls':15","'native_controls':'all inherited pass tests; exact count recorded in tests.log'");(r/'run.py').write_text(s)
s=(template/'run-local.sh').read_text().replace(template.name,r.name).replace('--bin global_quantum_alias','--bin compact_generic_repeat').replace('-- --nocapture','-- --nocapture --test-threads=1').replace("grep -q 'test result: ok. 15 passed; 0 failed;' tests.log","grep -Eq 'test result: ok. [1-9][0-9]* passed; 0 failed;' tests.log")
(r/'run-local.sh').write_bytes(s.encode());print(r.name)
